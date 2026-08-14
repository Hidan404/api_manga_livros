"""Modelo de refresh tokens persistidos (Sprint 2).

Permite revogar tokens (logout) e detectar REUSO (rotação):
- A cada `/auth/refresh`, o jti usado é marcado como `revogado`.
- Se um jti já revogado for usado de novo → possível roubo → a sessão inteira
  do usuário é invalidada (`revogar_todos`).
"""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    # identificador único do token (inside do JWT), para busca/revogação
    jti = Column(String(64), unique=True, nullable=False, index=True)
    expira_em = Column(DateTime(timezone=True), nullable=False)
    revogado = Column(Boolean, nullable=False, default=False)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    usuario = relationship("Usuario", back_populates="refresh_tokens")
