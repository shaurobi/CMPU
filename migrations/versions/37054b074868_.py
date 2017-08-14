"""empty message

Revision ID: 37054b074868
Revises: fb9497d1def7
Create Date: 2017-08-10 21:35:55.111211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37054b074868'
down_revision = 'fb9497d1def7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('finishTime', sa.Time(), nullable=True))
    op.add_column('event', sa.Column('startTime', sa.Time(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'startTime')
    op.drop_column('event', 'finishTime')
    # ### end Alembic commands ###