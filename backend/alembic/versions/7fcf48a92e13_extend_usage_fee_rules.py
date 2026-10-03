"""extend usage fee rules

Revision ID: 7fcf48a92e13
Revises: a86a1d7ad61e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7fcf48a92e13"
down_revision: Union[str, Sequence[str], None] = "a86a1d7ad61e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NULL = Regel gilt für das gesamte Netzgebiet des Netzbetreibers.
    op.alter_column(
        "usage_fee_rules",
        "gkz",
        existing_type=sa.String(length=10),
        nullable=True,
    )

    # Optionaler konkreter Lieferant für lieferantenabhängige Regeln.
    op.add_column(
        "usage_fee_rules",
        sa.Column(
            "provider_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # all = gilt unabhängig vom Lieferanten
    # local_only = gilt nur beim lokalen Lieferanten
    op.add_column(
        "usage_fee_rules",
        sa.Column(
            "supplier_scope",
            sa.String(length=20),
            nullable=False,
            server_default="all",
        ),
    )

    # Manche Prozentregeln schließen das Messentgelt ausdrücklich aus.
    op.add_column(
        "usage_fee_rules",
        sa.Column(
            "include_metering_fee",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.create_foreign_key(
        "fk_usage_fee_rules_provider_id",
        "usage_fee_rules",
        "providers",
        ["provider_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_usage_fee_rules_provider_id",
        "usage_fee_rules",
        ["provider_id"],
    )

    op.drop_constraint(
        "uq_usage_fee_rule",
        "usage_fee_rules",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_usage_fee_rule",
        "usage_fee_rules",
        [
            "gkz",
            "network_operator_id",
            "energy_type",
            "calculation_type",
            "provider_id",
            "supplier_scope",
            "valid_from",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_usage_fee_rule",
        "usage_fee_rules",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_usage_fee_rule",
        "usage_fee_rules",
        [
            "gkz",
            "network_operator_id",
            "energy_type",
            "calculation_type",
            "valid_from",
        ],
    )

    op.drop_index(
        "ix_usage_fee_rules_provider_id",
        table_name="usage_fee_rules",
    )

    op.drop_constraint(
        "fk_usage_fee_rules_provider_id",
        "usage_fee_rules",
        type_="foreignkey",
    )

    op.drop_column(
        "usage_fee_rules",
        "include_metering_fee",
    )

    op.drop_column(
        "usage_fee_rules",
        "supplier_scope",
    )

    op.drop_column(
        "usage_fee_rules",
        "provider_id",
    )

    op.alter_column(
        "usage_fee_rules",
        "gkz",
        existing_type=sa.String(length=10),
        nullable=False,
    )
