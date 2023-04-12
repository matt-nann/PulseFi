"""Init Migration

Revision ID: 6e3a44926a2e
Revises: 
Create Date: 2023-04-12 10:43:51.215292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e3a44926a2e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fitbit_authorized', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('fitbit_access_token', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('fitbit_refresh_token', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('spotify_authorized', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('spotify_token', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('dummy', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Users', schema=None) as batch_op:
        batch_op.drop_column('dummy')
        batch_op.drop_column('spotify_token')
        batch_op.drop_column('spotify_authorized')
        batch_op.drop_column('fitbit_refresh_token')
        batch_op.drop_column('fitbit_access_token')
        batch_op.drop_column('fitbit_authorized')

    # ### end Alembic commands ###
