"""empty message

Revision ID: 49b3e2f820af
Revises: 5c7aef842a16
Create Date: 2023-11-29 15:39:11.601188

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '49b3e2f820af'
down_revision = '5c7aef842a16'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=100), nullable=True))
        batch_op.alter_column('event_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=False)
        batch_op.drop_column('event_time')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('event_time', mysql.TIME(), nullable=True))
        batch_op.alter_column('event_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=False)
        batch_op.drop_column('description')

    # ### end Alembic commands ###