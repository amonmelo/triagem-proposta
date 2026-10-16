"""Linha de comando da triagem.

    python -m triagem proposta.json              # parecer em JSON + card
    python -m triagem proposta.json --card      # só o card em Markdown
    python -m triagem proposta.json --json      # só o parecer em JSON
    python -m triagem exemplos/                 # todo *.json do diretório
    cat proposta.json | python -m triagem -     # lê da entrada padrão

Códigos de saída: 0 = triou tudo (o parecer é resultado, não erro);
2 = problema de entrada (arquivo ilegível, JSON inválido, não é objeto).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Union

from .card import gerar_card
from .modelo import EntradaInvalida
from .quadro import adicionar_tarefa
from .triagem import triar


def _coletar_alvos(alvos: List[str]) -> List[Union[str, Path]]:
    """Expande diretórios para os *.json de dentro, incluindo subpastas."""
    expandidos: List[Union[str, Path]] = []
    for alvo in alvos:
        if alvo == "-":
            expandidos.append("-")
            continue
        caminho = Path(alvo)
        if caminho.is_dir():
            expandidos.extend(sorted(caminho.rglob("*.json")))
        else:
            expandidos.append(caminho)
    return expandidos


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="triagem",
        description=(
            "Triagem determinística de propostas de recuperação de pastagens "
            "(regras R1–R6 do teste AgDev)."
        ),
    )
    parser.add_argument(
        "propostas",
        nargs="+",
        help="arquivo(s) JSON, diretório(s) com *.json, ou '-' para ler do stdin",
    )
    formato = parser.add_mutually_exclusive_group()
    formato.add_argument("--json", action="store_true", help="imprime só o parecer em JSON")
    formato.add_argument("--card", action="store_true", help="imprime só o card em Markdown")
    parser.add_argument(
        "--quadro",
        metavar="ARQUIVO",
        help=(
            "além de imprimir, anexa o resultado como tarefa num quadro em "
            "Markdown (integração simulada com gerenciador de tarefas)"
        ),
    )
    args = parser.parse_args(argv)

    codigo = 0
    processadas = 0
    for alvo in _coletar_alvos(args.propostas):
        if alvo == "-":
            nome = "<stdin>"
            texto = sys.stdin.read()
        else:
            nome = str(alvo)
            try:
                texto = Path(alvo).read_text(encoding="utf-8")
            except OSError as erro:
                print(f"ERRO: não consegui ler {alvo}: {erro}", file=sys.stderr)
                codigo = 2
                continue

        try:
            dados = json.loads(texto)
            parecer = triar(dados)
        except json.JSONDecodeError as erro:
            print(f"ERRO: {nome} não é JSON válido: {erro}", file=sys.stderr)
            codigo = 2
            continue
        except EntradaInvalida as erro:
            print(f"ERRO: {nome}: {erro}", file=sys.stderr)
            codigo = 2
            continue

        if args.json:
            corpo = json.dumps(parecer.to_dict(), ensure_ascii=False, indent=2)
        elif args.card:
            corpo = gerar_card(parecer)
        else:
            corpo = (
                json.dumps(parecer.to_dict(), ensure_ascii=False, indent=2)
                + "\n\n"
                + gerar_card(parecer)
            )

        if processadas:
            print()
        if not (args.json or args.card):
            print(f"===== {nome} =====")
        print(corpo, end="")
        if args.quadro:
            caminho_tarefa = adicionar_tarefa(Path(args.quadro), parecer)
            print(f"tarefa adicionada em {caminho_tarefa}", file=sys.stderr)
        processadas += 1

    return codigo


if __name__ == "__main__":
    sys.exit(main())
