"""Logging estruturado (Sprint 6).

Formato JSON em produção (fácil de agregar no Render/observabilidade) e
formato texto simples em desenvolvimento.
"""

import json
import logging
from datetime import UTC, datetime

from app.core.configuracao import config


class JsonFormatter(logging.Formatter):
    """Formata cada registro como uma linha JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(UTC).isoformat(),
            "nivel": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configurar_logging(nivel: int = logging.INFO) -> None:
    """Configura o logging da aplicação (idempotente)."""

    root = logging.getLogger()
    if any(getattr(h, "_structured", False) for h in root.handlers):
        return

    for handler in root.handlers:
        root.removeHandler(handler)

    handler = logging.StreamHandler()
    handler._structured = True  # type: ignore[attr-defined]
    if config.ENVIRONMENT == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root.setLevel(nivel)
    root.addHandler(handler)
