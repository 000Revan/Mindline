"""更新daily_tasks表，修复索引

Revision ID: b4c6fd88706e
Revises: bf6b342f5890
Create Date: 2026-07-02 14:49:13.292325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c6fd88706e'
down_revision: Union[str, Sequence[str], None] = 'bf6b342f5890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = 'daily_tasks'
GOAL_INDEX_NAME = 'ix_daily_tasks_goal_status'
GOAL_ID_INDEX_NAME = 'ix_daily_tasks_goal_id'
USER_INDEX_NAME = 'ix_daily_tasks_user_status'
USER_ID_TEMP_INDEX_NAME = 'ix_daily_tasks_user_id_migration_tmp'


def _get_indexes() -> dict[str, tuple[str, ...]]:
    """读取 daily_tasks 当前索引，用于恢复 MySQL 非事务 DDL 的半完成迁移。"""

    inspector = sa.inspect(op.get_bind())
    return {
        index['name']: tuple(index['column_names'])
        for index in inspector.get_indexes(TABLE_NAME)
    }


def _ensure_index(index_name: str, columns: tuple[str, ...]) -> None:
    """确保指定索引存在且列定义一致。"""

    indexes = _get_indexes()
    current_columns = indexes.get(index_name)
    if current_columns == columns:
        return
    if current_columns is not None:
        op.drop_index(index_name, table_name=TABLE_NAME)
    op.create_index(index_name, TABLE_NAME, list(columns), unique=False)


def _replace_foreign_key_index(
    index_name: str,
    target_columns: tuple[str, ...],
    support_index_name: str,
    support_columns: tuple[str, ...],
) -> None:
    """在替换外键索引前建立支撑索引，避免触发 MySQL 1553。"""

    if _get_indexes().get(index_name) == target_columns:
        return

    _ensure_index(support_index_name, support_columns)
    if index_name in _get_indexes():
        op.drop_index(index_name, table_name=TABLE_NAME)
    op.create_index(index_name, TABLE_NAME, list(target_columns), unique=False)


def _drop_index_if_exists(index_name: str) -> None:
    """仅在索引存在时删除，保证失败后的迁移可以安全重试。"""

    if index_name in _get_indexes():
        op.drop_index(index_name, table_name=TABLE_NAME)


def upgrade() -> None:
    """Upgrade schema."""
    # goal_id 在 ORM 中声明了独立索引，保留它作为外键支撑索引。
    _ensure_index(GOAL_ID_INDEX_NAME, ('goal_id',))
    _replace_foreign_key_index(
        index_name=GOAL_INDEX_NAME,
        target_columns=('goal_id', 'task_date'),
        support_index_name=GOAL_ID_INDEX_NAME,
        support_columns=('goal_id',),
    )

    # user_id 没有永久单列索引，仅在替换复合索引期间创建临时索引。
    _replace_foreign_key_index(
        index_name=USER_INDEX_NAME,
        target_columns=('user_id', 'task_date', 'status'),
        support_index_name=USER_ID_TEMP_INDEX_NAME,
        support_columns=('user_id',),
    )
    _drop_index_if_exists(USER_ID_TEMP_INDEX_NAME)


def downgrade() -> None:
    """Downgrade schema."""
    _replace_foreign_key_index(
        index_name=USER_INDEX_NAME,
        target_columns=('user_id', 'status'),
        support_index_name=USER_ID_TEMP_INDEX_NAME,
        support_columns=('user_id',),
    )
    _drop_index_if_exists(USER_ID_TEMP_INDEX_NAME)

    _replace_foreign_key_index(
        index_name=GOAL_INDEX_NAME,
        target_columns=('goal_id', 'status'),
        support_index_name=GOAL_ID_INDEX_NAME,
        support_columns=('goal_id',),
    )
    _drop_index_if_exists(GOAL_ID_INDEX_NAME)
