"""empty message

Revision ID: ba3c17b0245c
Revises: 49b3e2f820af
Create Date: 2023-12-06 16:28:55.600831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba3c17b0245c'
down_revision = '49b3e2f820af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('links',
    sa.Column('link_id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(length=50), nullable=True),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['family_id'], ['families.family_id'], ),
    sa.PrimaryKeyConstraint('link_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('links')
    # ### end Alembic commands ###