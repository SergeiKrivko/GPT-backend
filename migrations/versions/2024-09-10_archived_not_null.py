"""'archived_not_null'

Revision ID: e3d872d39a42
Revises: e2a5f6d79f15
Create Date: 2024-09-10 19:09:37.660748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3d872d39a42'
down_revision: Union[str, None] = 'e2a5f6d79f15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chat', 'archived',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chat', 'archived',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
