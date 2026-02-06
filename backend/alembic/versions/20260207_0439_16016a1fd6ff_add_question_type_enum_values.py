"""add_question_type_enum_values

Revision ID: 16016a1fd6ff
Revises: fc214a3c3c14
Create Date: 2026-02-07 04:39:10.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16016a1fd6ff'
down_revision = 'fc214a3c3c14'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new values to QuestionType enum
    # Lưu ý: "commit" mỗi lệnh alter type để tránh lỗi "ALTER TYPE ... cannot run inside a transaction block"
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'word_from_meaning'")
        op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'meaning_from_word'")
        op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'dictation'")
        op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'synonym_antonym_mcq'")
        op.execute("ALTER TYPE questiontype ADD VALUE IF NOT EXISTS 'definition_mcq'")


def downgrade() -> None:
    # Postgres không hỗ trợ remove value khỏi enum dễ dàng
    pass
