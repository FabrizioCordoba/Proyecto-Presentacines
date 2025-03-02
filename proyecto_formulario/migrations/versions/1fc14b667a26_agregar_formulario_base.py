"""Agregar formulario_base

Revision ID: 1fc14b667a26
Revises: 
Create Date: 2025-02-07 12:40:48.105764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fc14b667a26'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('formulario_base',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('postulante_id', sa.Integer(), nullable=False),
    sa.Column('concurso_id', sa.Integer(), nullable=False),
    sa.Column('datos_generales', sa.JSON(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['concurso_id'], ['concurso.id'], ),
    sa.ForeignKeyConstraint(['postulante_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('respuesta_campo_dinamico',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('formulario_id', sa.Integer(), nullable=False),
    sa.Column('campo_id', sa.Integer(), nullable=False),
    sa.Column('valor', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['campo_id'], ['campo_formulario.id'], ),
    sa.ForeignKeyConstraint(['formulario_id'], ['formulario_base.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('respuesta_campo_dinamico')
    op.drop_table('formulario_base')
    # ### end Alembic commands ###
