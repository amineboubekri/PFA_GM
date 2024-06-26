"""empty message

Revision ID: 197765150187
Revises: ac5f2428cc53
Create Date: 2024-07-01 23:48:28.431010

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '197765150187'
down_revision = 'ac5f2428cc53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_transactions', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('total_transactions')

    # ### end Alembic commands ###
