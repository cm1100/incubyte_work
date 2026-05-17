"""salary_non_negative_check_constraint

Adds CK(salary >= 0) so the DB rejects negative salaries even when callers
bypass the API layer (e.g. the bulk-insert seed script).

Revision ID: 169503585ddb
Revises: ec33b043f926
Create Date: 2026-05-17 11:39:52.823829

Note: autogenerate cannot detect new CheckConstraints, so this migration is
hand-written. Uses batch_alter_table for SQLite compatibility (SQLite can
only add CHECK via table rebuild; Alembic batch mode handles that).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "169503585ddb"
down_revision: Union[str, Sequence[str], None] = "ec33b043f926"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("employees") as batch_op:
        batch_op.create_check_constraint(
            "ck_employees_salary_non_negative", "salary >= 0"
        )


def downgrade() -> None:
    with op.batch_alter_table("employees") as batch_op:
        batch_op.drop_constraint("ck_employees_salary_non_negative", type_="check")
