"""Configuração simples de logging.

O que são 'logs técnicos'?
- É um registro estruturado (DEBUG/INFO/WARNING/ERROR) do que o programa fez.
- Diferente de print: você pode ligar/desligar facilmente e guardar em arquivo.

Nesta V4:
- 'modo=verbose' imprime tabelas na tela (didático).
- logging (DEBUG) guarda detalhes técnicos (opcional).
"""

from __future__ import annotations

import logging
from typing import Optional

def criar_logger(
    nome: str = "momentos_inercia_v4",
    *,
    nivel: int = logging.INFO,
    arquivo: Optional[str] = None,
) -> logging.Logger:
    logger = logging.getLogger(nome)

    # Evita duplicar handlers se o usuário criar várias vezes
    if getattr(logger, "_v4_configurado", False):
        logger.setLevel(nivel)
        return logger

    logger.setLevel(nivel)
    fmt = logging.Formatter("[%(levelname)s] %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(nivel)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if arquivo:
        fh = logging.FileHandler(arquivo, encoding="utf-8")
        fh.setLevel(nivel)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    logger._v4_configurado = True  # type: ignore[attr-defined]
    return logger
