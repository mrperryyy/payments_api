"""empty message

Revision ID: 01184206d697
Revises: bd294bf624d2
Create Date: 2022-06-20 16:57:27.790185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01184206d697'
down_revision = 'bd294bf624d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payment', sa.Column('status', sa.String(length=8), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payment', 'status')
    # ### end Alembic commands ###