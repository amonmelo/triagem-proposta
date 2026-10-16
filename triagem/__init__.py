"""triagem-proposta: triagem determinística de propostas (regras R1–R6)."""
from .modelo import (
    CAMPOS_OBRIGATORIOS,
    RECUSADA,
    REVISAO_HUMANA,
    SEGUE,
    EntradaInvalida,
    Parecer,
)
from .triagem import triar

__version__ = "1.0.0"

__all__ = [
    "CAMPOS_OBRIGATORIOS",
    "EntradaInvalida",
    "Parecer",
    "RECUSADA",
    "REVISAO_HUMANA",
    "SEGUE",
    "triar",
    "__version__",
]
