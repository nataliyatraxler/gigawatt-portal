from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.tariff import Tariff
from app.models.tariff_document import TariffDocument, TariffDocumentType
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/tariff-documents",
    tags=["tariff-documents"],
)

UPLOAD_DIR = Path("uploads/tariff_documents")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_tariff_or_404(tariff_id: int, db: Session) -> Tariff:
    tariff = db.query(Tariff).filter(Tariff.id == tariff_id).first()

    if tariff is None:
        raise HTTPException(
            status_code=404,
            detail="Tarif nicht gefunden.",
        )

    return tariff


def ensure_upload_permission(
    tariff: Tariff,
    current_user: User,
) -> None:
    if current_user.role == UserRole.SUPERADMIN:
        return

    if (
        current_user.role == UserRole.LIEFERANT
        and current_user.provider_id == tariff.provider_id
    ):
        return

    raise HTTPException(
        status_code=403,
        detail="Keine Berechtigung zum Hochladen von Tarifdokumenten.",
    )


def document_response(document: TariffDocument) -> dict:
    return {
        "id": document.id,
        "tariff_id": document.tariff_id,
        "document_type": document.document_type.value,
        "file_name": document.file_name,
        "uploaded_at": document.uploaded_at,
        "download_url": f"/tariff-documents/{document.id}/download",
    }


@router.post("/tariffs/{tariff_id}")
async def upload_tariff_document(
    tariff_id: int,
    document_type: TariffDocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tariff = get_tariff_or_404(tariff_id, db)
    ensure_upload_permission(tariff, current_user)

    original_name = Path(file.filename or "").name

    if not original_name:
        raise HTTPException(
            status_code=400,
            detail="Dateiname fehlt.",
        )

    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Nur PDF-Dateien sind erlaubt.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Die PDF-Datei darf maximal 10 MB groß sein.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Die hochgeladene Datei ist keine gültige PDF-Datei.",
        )

    tariff_dir = UPLOAD_DIR / str(tariff_id)
    tariff_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}.pdf"
    file_path = tariff_dir / stored_name
    file_path.write_bytes(content)

    document = TariffDocument(
        tariff_id=tariff_id,
        uploaded_by_user_id=current_user.id,
        document_type=document_type,
        file_name=original_name,
        file_path=str(file_path),
        active=True,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document_response(document)


@router.get("/tariffs/{tariff_id}")
def list_tariff_documents(
    tariff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_tariff_or_404(tariff_id, db)

    documents = (
        db.query(TariffDocument)
        .filter(
            TariffDocument.tariff_id == tariff_id,
            TariffDocument.active.is_(True),
        )
        .order_by(
            TariffDocument.document_type.asc(),
            TariffDocument.uploaded_at.desc(),
        )
        .all()
    )

    return [document_response(document) for document in documents]


@router.get("/{document_id}/download")
def download_tariff_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(TariffDocument)
        .filter(
            TariffDocument.id == document_id,
            TariffDocument.active.is_(True),
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Dokument nicht gefunden.",
        )

    file_path = Path(document.file_path)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF-Datei nicht gefunden.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document.file_name,
    )
