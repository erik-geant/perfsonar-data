"""Create docs table

Revision ID: 5dd5eef151c5
Revises: 
Create Date: 2017-06-29 10:08:50.147525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dd5eef151c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "docs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("doc", sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table("docs")
