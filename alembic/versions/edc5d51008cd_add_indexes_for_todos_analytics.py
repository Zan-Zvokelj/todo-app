"""add indexes for todos analytics

Revision ID: edc5d51008cd
Revises: a94b2ebd9ef1
Create Date: 2026-01-09 11:02:04.607739
"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'edc5d51008cd'
down_revision: Union[str, Sequence[str], None] = 'a94b2ebd9ef1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Single-column indexes ---
    op.create_index(
        "ix_todos_owner_id",
        "todos",
        ["owner_id"]
    )

    op.create_index(
        "ix_todos_complete",
        "todos",
        ["complete"]
    )

    op.create_index(
        "ix_todos_created_at",
        "todos",
        ["created_at"]
    )

    # --- Composite index (most important one) ---
    op.create_index(
        "ix_todos_owner_complete",
        "todos",
        ["owner_id", "complete"]
    )


def downgrade() -> None:
    op.drop_index("ix_todos_owner_complete", table_name="todos")
    op.drop_index("ix_todos_created_at", table_name="todos")
    op.drop_index("ix_todos_complete", table_name="todos")
    op.drop_index("ix_todos_owner_id", table_name="todos")

