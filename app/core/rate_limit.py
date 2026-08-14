"""Rate limiting central (Sprint 2).

Usa `slowapi` com chave baseada no IP de origem (`get_remote_address`).
O limiter é um singleton: é registrado no `app.state` (main.py) e usado
nas rotas sensíveis (ex.: login) via decorator `@limiter.limit(...)`.

Observação: `slowapi` guarda contadores em memória por processo — suficiente
para o Render (1 worker) e para estudo. Para múltiplos workers, usar um
backend distribuído (ex.: Redis).
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
