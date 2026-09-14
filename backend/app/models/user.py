from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """User { id, name, surname, projectRoles: [...] } — process_full_v4.md, раздел 5.

    Вход без пароля (имя + фамилия), поэтому нет полей учётных данных.
    projectRoles реализован как отдельная таблица ProjectRole (см. project.py).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
