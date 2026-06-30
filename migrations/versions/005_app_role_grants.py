"""Create application database role and grant tenant-scoped table access.

Revision ID: 005_app_role_grants
Revises: 004_memory_entries
Create Date: 2026-06-29
"""

from __future__ import annotations

import os
from typing import Sequence, Union

from alembic import op

from helpers import PLATFORM_SCHEMAS, PLATFORM_TABLES

revision: str = "005_app_role_grants"
down_revision: Union[str, None] = "004_memory_entries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

APP_ROLE = "aep_app"


def _app_db_password() -> str:
    password = os.environ.get("AEP_APP_DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "AEP_APP_DB_PASSWORD must be set before running migrations "
            "(see .env.example)"
        )
    return password.replace("'", "''")


def upgrade() -> None:
    password = _app_db_password()
    op.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
                CREATE ROLE {APP_ROLE} WITH LOGIN PASSWORD '{password}'
                    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
            ELSE
                ALTER ROLE {APP_ROLE} WITH PASSWORD '{password}';
            END IF;
        END
        $$
        """)

    for schema in PLATFORM_SCHEMAS:
        op.execute(f"GRANT USAGE ON SCHEMA {schema} TO {APP_ROLE}")

    for schema, table in PLATFORM_TABLES:
        qualified = f"{schema}.{table}"
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {qualified} TO {APP_ROLE}")
        op.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema}
            GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {APP_ROLE}
            """)


def downgrade() -> None:
    for schema, table in reversed(PLATFORM_TABLES):
        qualified = f"{schema}.{table}"
        op.execute(f"REVOKE ALL ON {qualified} FROM {APP_ROLE}")

    for schema in reversed(PLATFORM_SCHEMAS):
        op.execute(f"""
            ALTER DEFAULT PRIVILEGES FOR ROLE current_user IN SCHEMA {schema}
            REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM {APP_ROLE}
            """)
        op.execute(f"REVOKE USAGE ON SCHEMA {schema} FROM {APP_ROLE}")

    op.execute(f"DROP ROLE IF EXISTS {APP_ROLE}")
