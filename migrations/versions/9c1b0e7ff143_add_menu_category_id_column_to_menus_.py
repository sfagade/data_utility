"""Add menu_category_id column to menus table

Revision ID: 9c1b0e7ff143
Revises:
Create Date: 2025-01-02 19:25:00.123385

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9c1b0e7ff143"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("menus", sa.Column("menu_category_id", sa.Integer(), nullable=True))
    op.alter_column("menus", "menu_id", new_column_name="id")
    op.alter_column("menu_items", "menu_item_id", new_column_name="id")


def downgrade() -> None:
    pass
