"""Integração simulada com gerenciador de tarefas — o item opcional do teste.

O "gerenciador" aqui é um quadro em Markdown: cada triagem feita com
`--quadro` vira uma seção no fim do arquivo, com data/hora e pendências
prontas para marcar. Sem servidor, sem conta — o analista vê o card onde
já trabalha. Em produção, o mesmo bloco iria para a API do gerenciador.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from .modelo import ROTULOS, Parecer


def adicionar_tarefa(
    quadro: Path, parecer: Parecer, momento: Optional[datetime] = None
) -> str:
    """Anexa a proposta como nova tarefa no fim do quadro. Devolve o caminho."""
    quando = (momento or datetime.now()).strftime("%d/%m/%Y %H:%M")
    linhas = [
        "",
        "---",
        "",
        f"## {parecer.proposta_id} — {ROTULOS[parecer.parecer]} (triada em {quando})",
        "",
        "**Motivos**",
        "",
    ]
    if parecer.motivos:
        linhas.extend(f"- **{m.regra}** — {m.mensagem}" for m in parecer.motivos)
    else:
        linhas.append("- Nenhum — a proposta atende todas as regras.")

    if parecer.pendencias:
        linhas.extend(["", "**Pendências**", ""])
        linhas.extend(
            f"- [ ] **{p['regra']}** — {p['acao']}" for p in parecer.pendencias
        )

    with quadro.open("a", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")
    return str(quadro)
