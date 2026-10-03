"""restore gas pauschale yearly unit

Revision ID: 512ec93bbba6
Revises: 3a093869b273
Create Date: 2026-09-28 23:35:07.982722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '512ec93bbba6'
down_revision: Union[str, Sequence[str], None] = '3a093869b273'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Restore Gas Pauschale unit to Cent/Jahr."""
    op.alter_column(
        "gas_network_tariffs",
        "pauschale_cent_month",
        new_column_name="pauschale_cent_year",
    )


def downgrade() -> None:
    """Rename Gas Pauschale back to month."""
    op.alter_column(
        "gas_network_tariffs",
        "pauschale_cent_year",
        new_column_name="pauschale_cent_month",
    )
