from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ProjectRoleName


class Project(Base):
    """Project { id, sppCode, name, curator, startDate } — process_full_v4.md, раздел 5."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    spp_code: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)  # формат NN-NNNN
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    curator: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)


class ProjectRole(Base):
    """Реализация User.projectRoles: [{projectId, role}] отдельной таблицей.

    project_id nullable — единственное отступление от буквальной пары {projectId, role}:
    роль ADMIN (раздел 1: «отдельная системная роль, не в списке входа») не привязана
    к конкретному проекту (администратор управляет проектами и справочниками глобально).
    """

    __tablename__ = "project_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    role: Mapped[ProjectRoleName] = mapped_column(Enum(ProjectRoleName, name="project_role_name"), nullable=False)
