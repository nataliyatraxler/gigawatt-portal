"""fix gas pauschale unit

Revision ID: 3a093869b273
Revises: 1945a9d6a655
Create Date: 2026-09-28 23:01:19.942056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a093869b273'
down_revision: Union[str, Sequence[str], None] = '1945a9d6a655'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename Gas Pauschale unit from year to month."""
    op.alter_column(
        "gas_network_tariffs",
        "pauschale_cent_year",
        new_column_name="pauschale_cent_month",
    )


def downgrade() -> None:
    """Restore previous Gas Pauschale column name."""
    op.alter_column(
        "gas_network_tariffs",
        "pauschale_cent_month",
        new_column_name="pauschale_cent_year",
    )
