"""deleted pricing

Revision ID: 8128cf96f544
Revises: 20e373ff406d
Create Date: 2019-07-22 12:10:53.222982

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8128cf96f544'
down_revision = '20e373ff406d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pricing')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pricing',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('underlying', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('symbolId', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('delta', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('bidPrice', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('bidSize', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('askPrice', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('askSize', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('ivAtBid', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('ivAtAsk', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('ivBidFit', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('ivAskFit', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('timestamp', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('askMarket', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('bidMarket', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('comment', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pricing_pkey')
    )
    # ### end Alembic commands ###
