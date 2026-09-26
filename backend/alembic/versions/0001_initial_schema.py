from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


order_status = postgresql.ENUM(
    "CREATED",
    "COOKING",
    "DELIVERING",
    "COMPLETED",
    "CANCELLED",
    name="order_status",
)


def upgrade() -> None:
    order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column(
            "is_available",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("image_url", sa.String(length=2048), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("customer_phone", sa.String(length=50), nullable=False),
        sa.Column("delivery_address", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "CREATED",
                "COOKING",
                "DELIVERING",
                "COMPLETED",
                "CANCELLED",
                name="order_status",
                create_type=False,
            ),
            server_default=sa.text("'CREATED'"),
            nullable=False,
        ),
        sa.Column(
            "total_price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "price_at_order",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["menu_item_id"],
            ["menu_items.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("menu_items")
    order_status.drop(op.get_bind(), checkfirst=True)
