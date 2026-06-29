"""add user locale

Revision ID: 40856d7e2a6f
Revises: fe56fa70289e
Create Date: 2026-06-28 16:53:17.360327

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision = '40856d7e2a6f'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    # Backfill existing rows with the default locale ("en") via server_default.
    op.add_column(
        'user',
        sa.Column(
            'locale',
            sqlmodel.sql.sqltypes.AutoString(length=5),
            nullable=False,
            server_default='en',
        ),
    )


def downgrade():
    op.drop_column('user', 'locale')
