"""empty message

Revision ID: 626ed6e8da32
Revises: 
Create Date: 2020-08-05 15:46:26.648948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '626ed6e8da32'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('company')
    # ### end Alembic commands ###