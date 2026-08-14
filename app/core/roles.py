"""Registro central de roles da aplicação (Sprint 0).

Motivo
------
As roles hoje são strings soltas espalhadas pelo código (``"admin"``, ``"user"``),
o que facilita typos (ex.: ``"Admin"``, ``"ADMIN"``) e dificulta a evolução.
Centralizar em um único enum permite:

- adicionar uma nova role editando **1 arquivo** (preparação para micro-SaaS);
- validar valores em schemas, models e controle de acesso usando **uma só fonte de verdade**;
- reutilizar em ``require_role`` / ``require_any_role`` (Sprint 2).

Sintaxe
-------
``RoleUsuario(StrEnum)``: enum cujos membros também são ``str``.
Ao herdar de ``str``, o valor serializa como string pura (ex.: ``"admin"``)
no banco, no JWT e no Pydantic — em vez do nome do membro (``RoleUsuario.ADMIN``).

Uso previsto (Sprints 2+)
-------------------------
- ``Usuario.role`` (SQLAlchemy) usa ``RoleUsuario`` como tipo/default.
- ``require_role(RoleUsuario.ADMIN)`` compara com ``.value``.
- Schemas Pydantic aceitam apenas os valores de ``ROLES_VALIDAS``.
"""

from enum import StrEnum


class RoleUsuario(StrEnum):
    """Roles válidas no sistema."""

    ADMIN = "admin"
    USER = "user"


# Set derivado do enum — validações usam SEMPRE este conjunto,
# garantindo que nada fique dessincronizado do enum acima.
ROLES_VALIDAS: set[str] = {role.value for role in RoleUsuario}
