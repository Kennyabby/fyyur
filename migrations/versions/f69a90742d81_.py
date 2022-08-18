"""empty message

Revision ID: f69a90742d81
Revises: 3f28226a970b
Create Date: 2022-08-13 15:08:45.530042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f69a90742d81'
down_revision = '3f28226a970b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('artists', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.drop_table('shows')
    # ### end Alembic commands ###
