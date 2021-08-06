"""testTable

Revision ID: 824d860f5198
Revises: 3162212c55f2
Create Date: 2019-07-16 15:15:25.643152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '824d860f5198'
down_revision = '3162212c55f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('testing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('underlying', sa.Float(), nullable=True),
    sa.Column('symbolId', sa.String(length=25), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('testing')
    # ### end Alembic commands ###
