"""add usage fee rules

Revision ID: a86a1d7ad61e
Revises: 8030d6058006
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a86a1d7ad61e"
down_revision: Union[str, Sequence[str], None] = "8030d6058006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usage_fee_rules",
        sa.Column("id", sa.Integer(), nullable=False),

        # Gemeinde — однозначно определяется из адресных данных.
        sa.Column("gkz", sa.String(length=10), nullable=False),

        # Netzbetreiber, для которого действует правило.
        sa.Column(
            "network_operator_id",
            sa.Integer(),
            nullable=False,
        ),

        # Strom / Gas.
        sa.Column(
            "energy_type",
            sa.String(length=20),
            nullable=False,
        ),

        # Например:
        # cent_per_kwh
        # percent_of_network_tariff
        # percent_of_energy_cost
        # percent_of_energy_and_network
        sa.Column(
            "calculation_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "value",
            sa.Numeric(12, 6),
            nullable=False,
        ),

        sa.Column(
            "valid_from",
            sa.Date(),
            nullable=False,
        ),

        sa.Column(
            "valid_to",
            sa.Date(),
            nullable=True,
        ),

        # Откуда взято правило / примечание к импорту.
        sa.Column(
            "source",
            sa.String(length=255),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["network_operator_id"],
            ["network_operators.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "gkz",
            "network_operator_id",
            "energy_type",
            "calculation_type",
            "valid_from",
            name="uq_usage_fee_rule",
        ),
    )

    op.create_index(
        "ix_usage_fee_rules_gkz",
        "usage_fee_rules",
        ["gkz"],
    )

    op.create_index(
        "ix_usage_fee_rules_network_operator_id",
        "usage_fee_rules",
        ["network_operator_id"],
    )

    op.create_index(
        "ix_usage_fee_rules_lookup",
        "usage_fee_rules",
        [
            "gkz",
            "network_operator_id",
            "energy_type",
        ],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_usage_fee_rules_lookup",
        table_name="usage_fee_rules",
    )

    op.drop_index(
        "ix_usage_fee_rules_network_operator_id",
        table_name="usage_fee_rules",
    )

    op.drop_index(
        "ix_usage_fee_rules_gkz",
        table_name="usage_fee_rules",
    )

    op.drop_table("usage_fee_rules")
