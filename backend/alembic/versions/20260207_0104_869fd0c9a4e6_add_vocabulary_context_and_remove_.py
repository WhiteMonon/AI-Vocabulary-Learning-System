"""Alembic migration script template."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '869fd0c9a4e6'
down_revision = '9676121ee5fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Step 1: Create vocabulary_contexts table
    op.create_table(
        'vocabulary_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vocabulary_id', sa.Integer(), nullable=False),
        sa.Column('sentence', sa.String(), nullable=False),
        sa.Column('translation', sa.String(), nullable=True),
        sa.Column('ai_provider', sa.String(), nullable=False, server_default='system'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vocabulary_id'], ['vocabularies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vocabulary_contexts_vocabulary_id', 'vocabulary_contexts', ['vocabulary_id'])
    op.create_index('ix_vocabulary_contexts_provider', 'vocabulary_contexts', ['ai_provider'])
    
    # Step 2: Migrate existing example_sentence data to vocabulary_contexts
    # Use raw SQL to handle data migration
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO vocabulary_contexts (vocabulary_id, sentence, ai_provider, created_at, updated_at)
        SELECT 
            vm.vocabulary_id,
            vm.example_sentence,
            'migrated',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        FROM vocabulary_meanings vm
        WHERE vm.example_sentence IS NOT NULL AND vm.example_sentence != ''
    """))
    
    # Step 3: Drop example_sentence column from vocabulary_meanings
    op.drop_column('vocabulary_meanings', 'example_sentence')


def downgrade() -> None:
    """Downgrade database schema."""
    # Step 1: Re-add example_sentence column to vocabulary_meanings
    op.add_column('vocabulary_meanings', 
        sa.Column('example_sentence', sa.String(), nullable=True))
    
    # Step 2: Migrate data back from vocabulary_contexts (take first context per vocabulary)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE vocabulary_meanings vm
        SET example_sentence = (
            SELECT vc.sentence
            FROM vocabulary_contexts vc
            WHERE vc.vocabulary_id = vm.vocabulary_id
            AND vc.ai_provider = 'migrated'
            ORDER BY vc.id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM vocabulary_contexts vc2
            WHERE vc2.vocabulary_id = vm.vocabulary_id
            AND vc2.ai_provider = 'migrated'
        )
    """))
    
    # Step 3: Drop vocabulary_contexts table
    op.drop_index('ix_vocabulary_contexts_provider', table_name='vocabulary_contexts')
    op.drop_index('ix_vocabulary_contexts_vocabulary_id', table_name='vocabulary_contexts')
    op.drop_table('vocabulary_contexts')

