"""crear tabla entries

Revision ID: 0001
Revises:
Create Date: 2026-11-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Las bases anteriores a Alembic (como produccion) ya tienen la tabla, creada con create_all.
    # En ese caso no se toca nada y la base solo queda marcada en esta revision.
    if sa.inspect(op.get_bind()).has_table("entries"):
        return

    op.create_table(
        "entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entries_id", "entries", ["id"])


def downgrade() -> None:
    # Atencion: borra la tabla con todos sus datos.
    op.drop_index("ix_entries_id", table_name="entries")
    op.drop_table("entries")
