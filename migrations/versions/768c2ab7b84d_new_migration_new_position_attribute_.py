"""new migration: new 'position' attribute for InterviewParameter class

Revision ID: 768c2ab7b84d
Revises: a7731e89b972
Create Date: 2024-06-26 14:31:32.669966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '768c2ab7b84d'
down_revision = 'a7731e89b972'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interview_parameter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('situation', sa.String(), nullable=True))
        batch_op.alter_column('position',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.drop_column('role_description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interview_parameter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_description', sa.VARCHAR(), nullable=True))
        batch_op.alter_column('position',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.drop_column('situation')

    # ### end Alembic commands ###
