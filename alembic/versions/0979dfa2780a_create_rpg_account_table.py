"""create rpg account table

Revision ID: 0979dfa2780a
Revises: 79e8ae38af71
Create Date: 2019-02-01 23:10:02.728932

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0979dfa2780a'
down_revision = '79e8ae38af71'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rpg_accounts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('qq_number', sa.BigInteger, nullable=False, unique=True),
        sa.Column('created_dt', sa.DateTime(timezone=True)),
        sa.Column('total_coins', sa.BigInteger),
        sa.Column('total_sign_in', sa.BigInteger),
        sa.Column('last_sign_in_date', sa.Date),
    )


def downgrade():
    op.drop_table('rpg_accounts')
