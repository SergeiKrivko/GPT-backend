"""'chat_id_index'

Revision ID: d2a8f8732d00
Revises: cec27e6dcacd
Create Date: 2024-09-07 12:37:27.119939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2a8f8732d00'
down_revision: Union[str, None] = 'cec27e6dcacd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_message_chat_uuid'), 'message', ['chat_uuid'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_chat_uuid'), table_name='message')
    # ### end Alembic commands ###