"""Add index to Favorite and ON DELETE CASCADE

Revision ID: d2684df9ef08
Revises: ed39fa3508bf
Create Date: 2025-09-05 14:51:06.751864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2684df9ef08'
down_revision: Union[str, Sequence[str], None] = 'ed39fa3508bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_favorite_customer_id'), 'favorite', ['customer_id'], unique=False)
    op.drop_constraint(op.f('favorite_customer_id_fkey'), 'favorite', type_='foreignkey')
    op.create_foreign_key('favorite_customer_id_fkey', 'favorite', 'customer', ['customer_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('favorite_customer_id_fkey', 'favorite', type_='foreignkey')
    op.create_foreign_key(op.f('favorite_customer_id_fkey'), 'favorite', 'customer', ['customer_id'], ['id'])
    op.drop_index(op.f('ix_favorite_customer_id'), table_name='favorite')
