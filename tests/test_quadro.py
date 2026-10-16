"""Testes da integração simulada com quadro de tarefas (item opcional)."""
import json
from datetime import datetime
from pathlib import Path

from triagem.cli import main
from triagem.quadro import adicionar_tarefa
from triagem.triagem import triar

PASTA_EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"
QUANDO_FIXO = datetime(2026, 10, 20, 9, 30)


def _parecer_de(nome):
    proposta = json.loads((PASTA_EXEMPLOS / nome).read_text(encoding="utf-8"))
    return triar(proposta)


def test_cria_quadro_e_anexa_recusada(tmp_path):
    quadro = tmp_path / "quadro.md"
    adicionar_tarefa(quadro, _parecer_de("P-004.json"), momento=QUANDO_FIXO)
    texto = quadro.read_text(encoding="utf-8")
    assert "## P-004 — RECUSADA (triada em 20/10/2026 09:30)" in texto
    assert "- **R2** —" in texto and "- **R3** —" in texto
    assert "- [ ]" not in texto  # recusada não gera checklist


def test_revisao_humana_entra_com_checklist(tmp_path):
    quadro = tmp_path / "quadro.md"
    adicionar_tarefa(quadro, _parecer_de("P-005.json"), momento=QUANDO_FIXO)
    texto = quadro.read_text(encoding="utf-8")
    assert "## P-005 — REVISÃO HUMANA" in texto
    assert "- [ ] **R6** — Incluir o campo `area_matricula_ha` na proposta." in texto


def test_cada_triagem_anexa_uma_nova_secao(tmp_path):
    quadro = tmp_path / "quadro.md"
    adicionar_tarefa(quadro, _parecer_de("P-001.json"), momento=QUANDO_FIXO)
    adicionar_tarefa(quadro, _parecer_de("P-002.json"), momento=QUANDO_FIXO)
    texto = quadro.read_text(encoding="utf-8")
    assert texto.count("## P-001") == 1
    assert texto.count("## P-002") == 1
    assert texto.count("\n---\n") == 2  # uma seção por triagem


def test_cli_flag_quadro(tmp_path, capsys):
    quadro = tmp_path / "quadro.md"
    codigo = main(
        [str(PASTA_EXEMPLOS / "P-003.json"), "--card", "--quadro", str(quadro)]
    )
    capturado = capsys.readouterr()
    assert codigo == 0
    assert "tarefa adicionada em" in capturado.err  # aviso fora do stdout
    assert "## P-003 — REVISÃO HUMANA" in quadro.read_text(encoding="utf-8")
