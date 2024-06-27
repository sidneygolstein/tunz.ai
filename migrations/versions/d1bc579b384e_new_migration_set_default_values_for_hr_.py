"""New migration: set default values for HR attributes name, surname

Revision ID: d1bc579b384e
Revises: bb771cec775a
Create Date: 2024-06-27 16:24:54.418628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1bc579b384e'
down_revision = 'bb771cec775a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hr', schema=None) as batch_op:
        batch_op.alter_column('company_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('hr', schema=None) as batch_op:
        batch_op.alter_column('company_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
