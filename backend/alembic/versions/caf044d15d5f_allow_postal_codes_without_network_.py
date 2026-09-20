"""allow postal codes without network operator

Revision ID: caf044d15d5f
Revises: cb4e5d178a24
Create Date: 2026-09-19 22:45:41.773511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caf044d15d5f'
down_revision: Union[str, Sequence[str], None] = 'cb4e5d178a24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow postal codes without assigned network operator."""
    op.alter_column(
        'postal_codes',
        'network_operator_id',
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Require network operator for every postal code."""
    op.alter_column(
        'postal_codes',
        'network_operator_id',
        existing_type=sa.Integer(),
        nullable=False,
    )