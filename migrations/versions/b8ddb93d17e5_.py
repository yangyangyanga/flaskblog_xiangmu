"""empty message

Revision ID: b8ddb93d17e5
Revises: 9463f0aee67c
Create Date: 2017-10-24 20:34:09.729444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8ddb93d17e5'
down_revision = '9463f0aee67c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('photo_url', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'photo_url')
    # ### end Alembic commands ###
