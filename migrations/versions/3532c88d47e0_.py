"""empty message

Revision ID: 3532c88d47e0
Revises: 
Create Date: 2020-10-25 21:13:41.153603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3532c88d47e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('day_values',
    sa.Column('id', sa.String(length=3), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('order')
    )
    op.create_table('goals',
    sa.Column('id', sa.String(length=10), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.Column('sign', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('goal', sa.String(length=30), nullable=False),
    sa.Column('time', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('about', sa.Text(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('picture', sa.String(length=50), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('time_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=5), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order')
    )
    op.create_table('goals_teachers',
    sa.Column('goal_id', sa.String(length=10), nullable=True),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], )
    )
    op.create_table('schedules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Boolean(), nullable=True),
    sa.Column('day_id', sa.String(length=3), nullable=False),
    sa.Column('time_id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['day_id'], ['day_values.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
    sa.ForeignKeyConstraint(['time_id'], ['time_values.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('schedule_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bookings')
    op.drop_table('schedules')
    op.drop_table('goals_teachers')
    op.drop_table('time_values')
    op.drop_table('teachers')
    op.drop_table('requests')
    op.drop_table('goals')
    op.drop_table('day_values')
    # ### end Alembic commands ###
