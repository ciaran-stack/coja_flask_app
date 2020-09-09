"""empty message

Revision ID: 42d8a6a9f96f
Revises: 626ed6e8da32
Create Date: 2020-08-05 16:13:02.534998

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42d8a6a9f96f'
down_revision = '626ed6e8da32'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('cik_num', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'cik_num')
    # ### end Alembic commands ###