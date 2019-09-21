"""initial migration mysql

Revision ID: 0c4ae5efe682
Revises: 
Create Date: 2019-09-21 09:12:37.816951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c4ae5efe682'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('phone_number', sa.String(length=16), nullable=True),
    sa.Column('occupation', sa.String(length=64), nullable=True),
    sa.Column('member_from', sa.String(length=16), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('has_enough_info', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
