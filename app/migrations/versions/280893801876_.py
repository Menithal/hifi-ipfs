"""empty message

Revision ID: 280893801876
Revises: dcbee03e3639
Create Date: 2018-07-25 14:55:46.978524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '280893801876'
down_revision = 'dcbee03e3639'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('uploads', sa.Column('parent_hash', sa.Text(), nullable=True))
    op.add_column('uploads', sa.Column('is_avatar', sa.Boolean))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('uploads', 'parent_hash')
    op.drop_column('uploads', 'is_avatar')
    # ### end Alembic commands ###
