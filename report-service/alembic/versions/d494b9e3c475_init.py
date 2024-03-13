"""init

Revision ID: d494b9e3c475
Revises: 
Create Date: 2024-03-13 17:53:08.078977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd494b9e3c475'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('accounts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('iban', sa.String(length=34), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('iban')
    )
    op.create_table('transactions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('account_id', sa.String(length=36), nullable=False),
    sa.Column('transaction_id', sa.String(length=36), nullable=False),
    sa.Column('sender_iban', sa.String(length=34), nullable=False),
    sa.Column('sender_bic', sa.String(length=11), nullable=False),
    sa.Column('sender_name', sa.String(length=255), nullable=True),
    sa.Column('amount', sa.Numeric(precision=255), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('purpose', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('accounts')
    # ### end Alembic commands ###