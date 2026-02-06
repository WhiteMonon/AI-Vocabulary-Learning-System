"""Add vocabulary meanings and dictionary cache tables

Revision ID: 20260206_vocabulary_meanings
Revises: 118d4b8b5129
Create Date: 2026-02-06

Migration này thực hiện:
1. Tạo WordType và MeaningSource enums
2. Tạo vocabulary_meanings table (one-to-many với vocabularies)
3. Tạo dictionary_cache table
4. Migrate data từ vocabularies.definition sang vocabulary_meanings
5. Thêm word_type, is_word_type_manual columns vào vocabularies
6. Xóa definition, example_sentence, difficulty_level từ vocabularies
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '20260206_vocabulary_meanings'
down_revision = '118d4b8b5129'
branch_labels = None
depends_on = None

# Define enums
# Sử dụng trực tiếp dialects.postgresql.ENUM để có quyền kiểm soát create_type
word_type_enum_pg = postgresql.ENUM('function_word', 'content_word', name='wordtype', create_type=False)
meaning_source_enum_pg = postgresql.ENUM('manual', 'dictionary_api', 'auto_translate', name='meaningsource', create_type=False)

# Enum objects dùng cho các database khác (nếu cần) hoặc manual create
word_type_enum = sa.Enum('function_word', 'content_word', name='wordtype')
meaning_source_enum = sa.Enum('manual', 'dictionary_api', 'auto_translate', name='meaningsource')


def upgrade() -> None:
    """Upgrade database schema."""
    
    # 1. Tạo enums thủ công và an toàn
    conn = op.get_bind()
    
    # Kiểm tra wordtype
    res = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'wordtype'")).first()
    if not res:
        conn.execute(sa.text("CREATE TYPE wordtype AS ENUM ('function_word', 'content_word')"))
        
    # Kiểm tra meaningsource
    res = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'meaningsource'")).first()
    if not res:
        conn.execute(sa.text("CREATE TYPE meaningsource AS ENUM ('manual', 'dictionary_api', 'auto_translate')"))
    
    # 2. Tạo vocabulary_meanings table
    op.create_table('vocabulary_meanings',
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vocabulary_id', sa.Integer(), nullable=False),
        sa.Column('definition', sa.String(), nullable=False),
        sa.Column('example_sentence', sa.String(), nullable=True),
        # Sử dụng enum_pg với create_type=False
        sa.Column('meaning_source', meaning_source_enum_pg, server_default='manual', nullable=False),
        sa.Column('is_auto_generated', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['vocabulary_id'], ['vocabularies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vocabulary_meanings_vocabulary_id', 'vocabulary_meanings', ['vocabulary_id'], unique=False)
    
    # 3. Tạo dictionary_cache table
    op.create_table('dictionary_cache',
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('word', sa.String(), nullable=False),
        sa.Column('definition', sa.String(), nullable=False),
        # Sử dụng enum_pg với create_type=False
        sa.Column('source', meaning_source_enum_pg, nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('word', name='uq_dictionary_cache_word')
    )
    op.create_index('ix_dictionary_cache_word', 'dictionary_cache', ['word'], unique=True)
    op.create_index('ix_dictionary_cache_expires_at', 'dictionary_cache', ['expires_at'], unique=False)
    
    # 4. Migrate existing data: vocabularies.definition → vocabulary_meanings
    # Lấy current timestamp cho created_at/updated_at
    op.execute("""
        INSERT INTO vocabulary_meanings (vocabulary_id, definition, example_sentence, meaning_source, is_auto_generated, created_at, updated_at)
        SELECT id, definition, example_sentence, 'manual', false, created_at, updated_at
        FROM vocabularies
        WHERE definition IS NOT NULL
    """)
    
    # 5. Thêm word_type và is_word_type_manual columns vào vocabularies
    op.add_column('vocabularies', sa.Column('word_type', word_type_enum_pg, nullable=True))
    op.add_column('vocabularies', sa.Column('is_word_type_manual', sa.Boolean(), server_default='false', nullable=False))
    
    # 6. Set default word_type = 'content_word' cho existing records
    op.execute("UPDATE vocabularies SET word_type = 'content_word'")
    op.alter_column('vocabularies', 'word_type', nullable=False)
    
    # 7. Xóa columns cũ
    op.drop_column('vocabularies', 'definition')
    op.drop_column('vocabularies', 'example_sentence')
    op.drop_column('vocabularies', 'difficulty_level')


def downgrade() -> None:
    """Downgrade database schema."""
    
    # 1. Thêm lại columns cũ
    op.add_column('vocabularies', sa.Column('definition', sa.String(), nullable=True))
    op.add_column('vocabularies', sa.Column('example_sentence', sa.String(), nullable=True))
    op.add_column('vocabularies', sa.Column('difficulty_level', 
        sa.Enum('EASY', 'MEDIUM', 'HARD', name='difficultylevel'), 
        server_default='MEDIUM', nullable=False))
    
    # 2. Migrate data back: lấy meaning đầu tiên cho mỗi vocabulary
    op.execute("""
        UPDATE vocabularies v
        SET definition = (
            SELECT vm.definition 
            FROM vocabulary_meanings vm 
            WHERE vm.vocabulary_id = v.id 
            ORDER BY vm.id ASC 
            LIMIT 1
        ),
        example_sentence = (
            SELECT vm.example_sentence 
            FROM vocabulary_meanings vm 
            WHERE vm.vocabulary_id = v.id 
            ORDER BY vm.id ASC 
            LIMIT 1
        )
    """)
    
    # 3. Set NOT NULL cho definition
    op.alter_column('vocabularies', 'definition', nullable=False)
    
    # 4. Xóa columns mới
    op.drop_column('vocabularies', 'word_type')
    op.drop_column('vocabularies', 'is_word_type_manual')
    
    # 5. Drop tables
    op.drop_index('ix_dictionary_cache_expires_at', table_name='dictionary_cache')
    op.drop_index('ix_dictionary_cache_word', table_name='dictionary_cache')
    op.drop_table('dictionary_cache')
    
    op.drop_index('ix_vocabulary_meanings_vocabulary_id', table_name='vocabulary_meanings')
    op.drop_table('vocabulary_meanings')
    
    # 6. Drop enums
    conn = op.get_bind()
    conn.execute(sa.text("DROP TYPE IF EXISTS meaningsource"))
    conn.execute(sa.text("DROP TYPE IF EXISTS wordtype"))
