"""Set no required attributes for Company class

Revision ID: 41e8f9ddf473
Revises: 7f4a0a15b52b
Create Date: 2024-06-27 19:04:02.611022

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41e8f9ddf473'
down_revision = '7f4a0a15b52b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column('contact_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('contact_name',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
