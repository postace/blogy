"""add facebook and google id for user

Revision ID: dbe1b762f3bb
Revises: 0c4ae5efe682
Create Date: 2019-09-21 09:15:36.648516

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'dbe1b762f3bb'
down_revision = '0c4ae5efe682'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('fb_id', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('gg_id', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('has_required_info', sa.Boolean(), nullable=False))
    op.alter_column('users', 'email',
                    existing_type=mysql.VARCHAR(length=256),
                    nullable=False)
    op.create_index(op.f('ix_users_fb_id'), 'users', ['fb_id'], unique=True)
    op.create_index(op.f('ix_users_gg_id'), 'users', ['gg_id'], unique=True)
    op.drop_column('users', 'has_enough_info')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users',
                  sa.Column('has_enough_info', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_users_gg_id'), table_name='users')
    op.drop_index(op.f('ix_users_fb_id'), table_name='users')
    op.alter_column('users', 'email',
                    existing_type=mysql.VARCHAR(length=256),
                    nullable=True)
    op.drop_column('users', 'has_required_info')
    op.drop_column('users', 'gg_id')
    op.drop_column('users', 'fb_id')
    # ### end Alembic commands ###
