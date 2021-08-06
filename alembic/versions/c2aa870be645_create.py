"""create

Revision ID: c2aa870be645
Revises: 58a97523aeda
Create Date: 2019-07-31 15:58:51.694344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2aa870be645'
down_revision = '58a97523aeda'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session', sa.String(), nullable=True),
    sa.Column('duration', sa.String(), nullable=True),
    sa.Column('order_type', sa.String(), nullable=True),
    sa.Column('order_strategy_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('leg',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('order_leg_type', sa.String(), nullable=True),
    sa.Column('asset_type', sa.String(), nullable=True),
    sa.Column('symbol', sa.String(), nullable=True),
    sa.Column('instruction', sa.String(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('leg')
    op.drop_table('order')
    # ### end Alembic commands ###
