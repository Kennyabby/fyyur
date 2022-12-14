"""empty message

Revision ID: da5de3ff3bc9
Revises: 2c3426639f97
Create Date: 2022-08-14 06:00:18.425558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da5de3ff3bc9'
down_revision = '2c3426639f97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website_link', sa.String(length=500), nullable=True))
    op.drop_column('artists', 'website')
    op.add_column('venues', sa.Column('website_link', sa.String(length=500), nullable=True))
    op.drop_column('venues', 'website')
    op.execute("UPDATE venues SET website_link='http://napsui.herokuapp.com' WHERE website_link is NULL")
    op.execute("UPDATE artists SET website_link='http://napsui.herokuapp.com' WHERE website_link is NULL")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.drop_column('venues', 'website_link')
    op.add_column('artists', sa.Column('website', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.drop_column('artists', 'website_link')
    # ### end Alembic commands ###
