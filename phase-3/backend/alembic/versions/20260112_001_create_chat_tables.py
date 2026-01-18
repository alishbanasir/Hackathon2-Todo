"""Create conversations and messages tables for Phase 3 AI chatbot

Revision ID: 001_create_chat_tables
Revises:
Create Date: 2026-01-12 10:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001_create_chat_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema - create conversations and messages tables."""

    # Create message_role enum type
    message_role_enum = sa.Enum('user', 'assistant', name='message_role', native_enum=False)
    message_role_enum.create(op.get_bind(), checkfirst=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('openai_thread_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('openai_thread_id'),
    )

    # Create indexes for conversations table
    op.create_index(
        'ix_conversations_id',
        'conversations',
        ['id'],
        unique=False
    )
    op.create_index(
        'ix_conversations_user_id',
        'conversations',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_conversations_last_message_at',
        'conversations',
        ['last_message_at'],
        unique=False
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes for messages table
    op.create_index(
        'ix_messages_id',
        'messages',
        ['id'],
        unique=False
    )
    op.create_index(
        'ix_messages_conversation_id',
        'messages',
        ['conversation_id'],
        unique=False
    )
    op.create_index(
        'ix_messages_created_at',
        'messages',
        ['created_at'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade database schema - drop conversations and messages tables."""

    # Drop indexes first
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_index('ix_messages_id', table_name='messages')

    op.drop_index('ix_conversations_last_message_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_id', table_name='conversations')

    # Drop tables
    op.drop_table('messages')
    op.drop_table('conversations')

    # Drop enum type
    message_role_enum = sa.Enum('user', 'assistant', name='message_role', native_enum=False)
    message_role_enum.drop(op.get_bind(), checkfirst=True)
