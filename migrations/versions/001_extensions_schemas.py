"""Create PostgreSQL extensions and platform schemas.

Revision ID: 001_extensions_schemas
Revises:
Create Date: 2026-06-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

from helpers import create_schemas, drop_schemas

revision: str = "001_extensions_schemas"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    create_schemas()


def downgrade() -> None:
    drop_schemas()
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
