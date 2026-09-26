"""Updated the table schemas to use uuidv7 (database-generated)

Revision ID: 1b6b20e5ff30
Revises: dfe4cc0abf92
Create Date: 2026-08-18 19:39:36.094212

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b6b20e5ff30"
down_revision: Union[str, Sequence[str], None] = "dfe4cc0abf92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("user", "id", server_default=sa.text("uuidv7()"))

    op.alter_column("problem", "id", server_default=sa.text("uuidv7()"))

    op.alter_column("test_case", "id", server_default=sa.text("uuidv7()"))

    op.alter_column("submission", "id", server_default=sa.text("uuidv7()"))


def downgrade() -> None:
    op.alter_column("submission", "id", server_default=None)
    op.alter_column("test_case", "id", server_default=None)
    op.alter_column("problem", "id", server_default=None)
    op.alter_column("user", "id", server_default=None)
