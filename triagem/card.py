"""Card de tarefa em Markdown: título, parecer, motivos e pendências.

Proposta com SEGUE não tem pendências (esclarecimento do enunciado); uma
RECUSADA também não gera pendências de correção — o que ela tem é motivo.
"""
from __future__ import annotations

from .modelo import RECUSADA, REVISAO_HUMANA, ROTULOS, Parecer


def gerar_card(parecer: Parecer) -> str:
    """Devolve o card pronto para colar em um gerenciador de tarefas."""
    linhas = [
        f"# Triagem {parecer.proposta_id}",
        "",
        f"**Parecer: {ROTULOS[parecer.parecer]}**",
        "",
        "**Motivos**",
        "",
    ]

    if parecer.motivos:
        for motivo in parecer.motivos:
            linhas.append(f"- **{motivo.regra}** — {motivo.mensagem}")
    else:
        linhas.append("- Nenhum — a proposta atende todas as regras.")

    linhas.extend(["", "**Pendências**", ""])

    if parecer.parecer == REVISAO_HUMANA:
        for pendencia in parecer.pendencias:
            linhas.append(f"- [ ] **{pendencia['regra']}** — {pendencia['acao']}")
    elif parecer.parecer == RECUSADA:
        linhas.append("- Nenhuma — proposta recusada; comunicar o proponente citando os motivos.")
    else:
        linhas.append("- Nenhuma.")

    return "\n".join(linhas) + "\n"
