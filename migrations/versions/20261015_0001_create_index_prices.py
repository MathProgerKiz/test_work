"""Create the index_prices table.

Revision ID: 20261015_0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20261015_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "index_prices",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(precision=24, scale=8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint(
            "ticker", "timestamp", name="uq_index_prices_ticker_timestamp"
        ),
    )


def downgrade() -> None:
    op.drop_table("index_prices")
