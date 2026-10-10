"""add energy type to network metering fees

Revision ID: d9738c969069
Revises: 3e6a9d9418b2
Create Date: 2026-10-05 18:52:07.054481
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9738c969069"
down_revision: Union[str, Sequence[str], None] = "3e6a9d9418b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing rows are electricity metering fees.
    op.add_column(
        "network_metering_fees",
        sa.Column(
            "energy_type",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE network_metering_fees
        SET energy_type = 'electricity'
        WHERE energy_type IS NULL
        """
    )

    op.alter_column(
        "network_metering_fees",
        "energy_type",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.drop_constraint(
        "uq_network_metering_fee",
        "network_metering_fees",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_network_metering_fee",
        "network_metering_fees",
        [
            "network_operator_id",
            "year",
            "energy_type",
            "meter_type",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_network_metering_fee",
        "network_metering_fees",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_network_metering_fee",
        "network_metering_fees",
        [
            "network_operator_id",
            "year",
            "meter_type",
        ],
    )

    op.drop_column(
        "network_metering_fees",
        "energy_type",
    )
