"""Init

Revision ID: 881080518230
Revises: 
Create Date: 2018-12-23 21:12:11.984428

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '881080518230'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'note_notes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('context_id', sa.String(100), nullable=False),
    )

    op.create_table(
        'signup_events',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('fields', sa.JSON, nullable=False),
        sa.Column('context_id', sa.String(100), nullable=False),
        sa.Column('start_time', sa.Integer, nullable=False),
        sa.Column('end_time', sa.Integer),
        sa.Column('qq_group_number', sa.BigInteger),
    )

    op.create_table(
        'signup_signups',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('context_id', sa.String(100), nullable=False),
        sa.Column('event_id', sa.Integer, sa.ForeignKey('signup_events.id'),
                  nullable=False),
        sa.Column('field_values', sa.JSON, nullable=False),
        sa.Column('qq_number', sa.BigInteger),
    )


def downgrade():
    op.drop_table('note_notes')

    op.drop_table('signup_signups')
    op.drop_table('signup_events')
