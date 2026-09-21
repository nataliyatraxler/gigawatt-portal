"""Add customer type to regulatory charges

Revision ID: 5e5d6e38ec53
Revises: bc5577f9bbc1
Create Date: 2026-09-21
"""

from alembic import op
import sqlalchemy as sa


revision = "5e5d6e38ec53"
down_revision = "bc5577f9bbc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "regulatory_charges",
        sa.Column(
            "customer_type",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE regulatory_charges
        SET customer_type = 'gewerbe'
        WHERE name = 'Elektrizitätsabgabe'
        """
    )

    op.drop_constraint(
        "uq_regulatory_charge",
        "regulatory_charges",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_regulatory_charge",
        "regulatory_charges",
        [
            "name",
            "calculation_type",
            "network_level",
            "tariff_type",
            "network_area",
            "customer_type",
            "valid_from",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_regulatory_charge",
        "regulatory_charges",
        type_="unique",
    )

    op.execute(
        """
        DELETE FROM regulatory_charges
        WHERE name = 'Elektrizitätsabgabe'
          AND customer_type = 'privat'
        """
    )

    op.execute(
        """
        UPDATE regulatory_charges
        SET customer_type = NULL
        WHERE name = 'Elektrizitätsabgabe'
        """
    )

    op.create_unique_constraint(
        "uq_regulatory_charge",
        "regulatory_charges",
        [
            "name",
            "calculation_type",
            "network_level",
            "tariff_type",
            "network_area",
            "valid_from",
        ],
    )

    op.drop_column("regulatory_charges", "customer_type")
