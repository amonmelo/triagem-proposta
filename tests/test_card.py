"""Testes do card em Markdown."""
import json
from pathlib import Path

from triagem.card import gerar_card
from triagem.modelo import RECUSADA, REVISAO_HUMANA, SEGUE
from triagem.triagem import triar

PASTA_EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"


def _card(nome):
    proposta = json.loads((PASTA_EXEMPLOS / nome).read_text(encoding="utf-8"))
    return gerar_card(triar(proposta))


def test_card_segue():
    card = _card("P-001.json")
    assert card.startswith("# Triagem P-001")
    assert "**Parecer: SEGUE**" in card
    assert "- Nenhum — a proposta atende todas as regras." in card
    assert "Nenhuma." in card
    assert "- [ ]" not in card  # sem pendências para marcar


def test_card_segue_nao_mostra_regra_recusada():
    card = _card("P-001.json")
    assert "RECUSADA" not in card


def test_card_recusada_lista_todos_os_motivos():
    card = _card("P-004.json")
    assert "**Parecer: RECUSADA**" in card
    assert "- **R2** —" in card
    assert "- **R3** —" in card
    assert "15/03/2023" in card
    assert "- [ ]" not in card  # recusada não gera checklist de correção


def test_card_revisao_humana_com_checklist():
    card = _card("P-005.json")
    assert "**Parecer: REVISÃO HUMANA**" in card  # forma acentuada no card
    assert "- [ ] **R6** — Incluir o campo `area_matricula_ha` na proposta." in card
    assert "- [ ] **R4** —" in card


def test_card_revisao_cita_o_valor_recebido():
    card = _card("borda/car_fora_da_lista.json")
    assert '"Em análise"' in card


def test_card_sem_id():
    card = _card("borda/campo_id_ausente.json")
    assert card.startswith("# Triagem sem-id")
