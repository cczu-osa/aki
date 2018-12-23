"""Add 'max_signups' column

Revision ID: 79e8ae38af71
Revises: 881080518230
Create Date: 2018-12-23 22:40:38.147800

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '79e8ae38af71'
down_revision = '881080518230'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('signup_events', sa.Column('max_signups', sa.Integer))
    op.execute('UPDATE signup_events SET max_signups=0')
    op.alter_column('signup_events', 'max_signups', nullable=False)


def downgrade():
    op.drop_column('signup_events', 'max_signups')
