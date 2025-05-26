"""add agent tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type for agent roles
    agent_role_enum = postgresql.ENUM(
        'coordinator', 'researcher', 'analyzer', 'writer', 'reviewer', 'executor',
        name='agentrole'
    )
    agent_role_enum.create(op.get_bind())

    # Create agents table
    op.create_table('agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('node_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('coordinator', 'researcher', 'analyzer', 'writer', 'reviewer', 'executor', name='agentrole'), nullable=False),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_executions table
    op.create_table('agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('state', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create agent_messages table
    op.create_table('agent_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sender_id', sa.String(length=255), nullable=False),
        sa.Column('recipient_id', sa.String(length=255), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['workflow_executions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('agent_messages')
    op.drop_table('agent_executions')
    op.drop_table('agents')
    
    # Drop enum type
    agent_role_enum = postgresql.ENUM('coordinator', 'researcher', 'analyzer', 'writer', 'reviewer', 'executor', name='agentrole')
    agent_role_enum.drop(op.get_bind())