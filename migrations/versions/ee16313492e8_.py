"""empty message

Revision ID: ee16313492e8
Revises: 
Create Date: 2025-03-31 19:07:38.802244

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee16313492e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('user_type', sa.String(length=20), nullable=True),
    sa.Column('company_type', sa.String(length=20), nullable=True),
    sa.Column('account_verified', sa.Boolean(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('company_name', sa.String(length=200), nullable=True),
    sa.Column('nit', sa.String(length=20), nullable=True),
    sa.Column('profession', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('empresas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('ruc', sa.String(length=20), nullable=False),
    sa.Column('direccion', sa.String(length=200), nullable=True),
    sa.Column('telefono', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ruc')
    )
    op.create_table('fichas_formacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=200), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('fecha', sa.DateTime(), nullable=True),
    sa.Column('lugar', sa.String(length=200), nullable=True),
    sa.Column('duracion', sa.String(length=50), nullable=True),
    sa.Column('responsable', sa.String(length=100), nullable=True),
    sa.Column('objetivos', sa.Text(), nullable=True),
    sa.Column('codigo', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('empresa_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tareas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('fecha_completada', sa.DateTime(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('assigned_to_id', sa.Integer(), nullable=True),
    sa.Column('empresa_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('listas_asistencia',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
    sa.Column('estado', sa.String(length=50), nullable=True),
    sa.Column('enlace_compartible', sa.String(length=200), nullable=True),
    sa.Column('ficha_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ficha_id'], ['fichas_formacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('preguntas_formacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('texto', sa.String(length=500), nullable=False),
    sa.Column('tipo', sa.String(length=50), nullable=False),
    sa.Column('opciones', sa.Text(), nullable=True),
    sa.Column('ficha_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ficha_id'], ['fichas_formacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('asistentes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('documento', sa.String(length=20), nullable=True),
    sa.Column('cargo', sa.String(length=100), nullable=True),
    sa.Column('telefono', sa.String(length=20), nullable=True),
    sa.Column('firma_data', sa.Text(), nullable=True),
    sa.Column('fecha_registro', sa.DateTime(), nullable=True),
    sa.Column('lista_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lista_id'], ['listas_asistencia.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('respuestas_formacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('respuesta', sa.Text(), nullable=True),
    sa.Column('pregunta_id', sa.Integer(), nullable=False),
    sa.Column('asistente_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['asistente_id'], ['asistentes.id'], ),
    sa.ForeignKeyConstraint(['pregunta_id'], ['preguntas_formacion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('respuestas_formacion')
    op.drop_table('asistentes')
    op.drop_table('preguntas_formacion')
    op.drop_table('listas_asistencia')
    op.drop_table('tareas')
    op.drop_table('fichas_formacion')
    op.drop_table('empresas')
    op.drop_table('users')
    # ### end Alembic commands ###
