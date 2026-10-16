"""Testes de integração: os 5 exemplos do teste, combinação de regras e bordas."""
import json
from pathlib import Path

import pytest

from triagem.modelo import RECUSADA, REVISAO_HUMANA, SEGUE, EntradaInvalida
from triagem.triagem import triar

PASTA_EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"


def _carregar(nome):
    return json.loads((PASTA_EXEMPLOS / nome).read_text(encoding="utf-8"))


class TestExemplosDaSecao4:
    """Os 5 exemplos do enunciado — os pareeres esperados foram definidos por
    nós e estão travados aqui (o teste não dava o gabarito de propósito)."""

    @pytest.mark.parametrize(
        "arquivo,parecer_esperado,regras_dos_motivos",
        [
            ("P-001.json", SEGUE, []),
            ("P-002.json", RECUSADA, ["R1"]),                # 60 ha < 100 ha
            ("P-003.json", REVISAO_HUMANA, ["R5"]),          # 11,11% de divergência
            ("P-004.json", RECUSADA, ["R2", "R3"]),          # recusa + revisão: vale RECUSADA, lista os dois
            ("P-005.json", REVISAO_HUMANA, ["R4", "R6"]),    # campo ausente + cadastro pendente
        ],
    )
    def test_parecer_e_motivos(self, arquivo, parecer_esperado, regras_dos_motivos):
        parecer = triar(_carregar(arquivo))
        assert parecer.parecer == parecer_esperado
        assert [m.regra for m in parecer.motivos] == regras_dos_motivos

    def test_p001_segue_nao_tem_pendencia(self):
        parecer = triar(_carregar("P-001.json"))
        assert parecer.pendencias == []
        assert all(r.resultado == "ok" for r in parecer.regras)

    def test_p002_motivo_cita_a_area(self):
        parecer = triar(_carregar("P-002.json"))
        assert "60" in parecer.motivos[0].mensagem

    def test_p004_lista_todos_os_motivos_mesmo_recusada(self):
        parecer = triar(_carregar("P-004.json"))
        assert parecer.parecer == RECUSADA
        assert len(parecer.motivos) == 2
        assert "15/03/2023" in parecer.motivos[0].mensagem
        assert "Pendente" in parecer.motivos[1].mensagem
        assert parecer.pendencias == []  # recusada não gera pendência de correção

    def test_p005_r5_fica_nao_avaliada_por_falta_de_matricula(self):
        parecer = triar(_carregar("P-005.json"))
        por_regra = {r.regra: r for r in parecer.regras}
        assert por_regra["R1"].resultado == "ok"          # 300 ha >= 100 ha
        assert por_regra["R5"].resultado == "nao_avaliada"  # não há matrícula para comparar
        assert por_regra["R3"].resultado == "ok"

    def test_regras_sao_reportadas_em_ordem(self):
        parecer = triar(_carregar("P-005.json"))
        assert [r.regra for r in parecer.regras] == ["R1", "R2", "R3", "R4", "R5", "R6"]

    def test_p005_pendencias_apontam_acao_concreta(self):
        parecer = triar(_carregar("P-005.json"))
        acoes = " | ".join(p["acao"] for p in parecer.pendencias)
        assert "area_matricula_ha" in acoes
        assert "Pendente de regularização" in acoes


class TestDecisaoCombinada:
    def test_recusa_vence_revisao_e_lista_tudo(self):
        proposta = {
            "id": "C-1",
            "area_degradada_ha": 60,               # R1: RECUSADA
            "area_matricula_ha": 300,
            "area_car_ha": 298,
            "alerta_desmatamento": None,
            "situacao_car": "Ativo",
            "situacao_cadastral": "Irregular",     # R4: REVISÃO HUMANA
        }
        parecer = triar(proposta)
        assert parecer.parecer == RECUSADA
        assert [m.regra for m in parecer.motivos] == ["R1", "R4"]
        assert parecer.pendencias == []

    def test_so_revisao_lista_pendencias(self):
        proposta = {
            "id": "C-2",
            "area_degradada_ha": 400,
            "area_matricula_ha": 900,
            "area_car_ha": 1000,                   # R5: 11,11%
            "alerta_desmatamento": None,
            "situacao_car": "Ativo",
            "situacao_cadastral": "Regular",
        }
        parecer = triar(proposta)
        assert parecer.parecer == REVISAO_HUMANA
        assert len(parecer.pendencias) == 1
        assert parecer.pendencias[0]["regra"] == "R5"

    def test_duas_recusas_e_uma_revisao(self):
        proposta = {
            "id": "C-3",
            "area_degradada_ha": 60,               # R1
            "area_matricula_ha": 300,
            "area_car_ha": 400,                    # R5: revisão
            "alerta_desmatamento": "2021-01-01",   # R2
            "situacao_car": "Ativo",
            "situacao_cadastral": "Regular",
        }
        parecer = triar(proposta)
        assert parecer.parecer == RECUSADA
        assert [m.regra for m in parecer.motivos] == ["R1", "R2", "R5"]


class TestCasosDeBorda:
    def test_area_exatamente_100_segue(self):
        proposta = {**_carregar("borda/area_100ha_exata.json")}
        assert triar(proposta).parecer == SEGUE

    def test_alerta_no_dia_do_corte_segue(self):
        assert triar(_carregar("borda/alerta_no_dia_do_corte.json")).parecer == SEGUE

    def test_alerta_um_dia_depois_recusa(self):
        assert triar(_carregar("borda/alerta_um_dia_depois.json")).parecer == RECUSADA

    def test_divergencia_exatamente_5_por_cento_segue(self):
        assert triar(_carregar("borda/divergencia_5pct_exata.json")).parecer == SEGUE

    def test_divergencia_pouco_acima_de_5_por_cento_revisa(self):
        assert triar(_carregar("borda/divergencia_5pct_acima.json")).parecer == REVISAO_HUMANA

    def test_car_normalizado_minusculo_e_espacado_segue(self):
        assert triar(_carregar("borda/car_minusculo_espacado.json")).parecer == SEGUE

    def test_car_fora_da_lista_revisa_citando_valor(self):
        parecer = triar(_carregar("borda/car_fora_da_lista.json"))
        assert parecer.parecer == REVISAO_HUMANA
        assert "Em análise" in parecer.motivos[0].mensagem

    def test_alerta_ilegivel_revisa(self):
        parecer = triar(_carregar("borda/alerta_ilegivel.json"))
        assert parecer.parecer == REVISAO_HUMANA
        assert [m.regra for m in parecer.motivos] == ["R2"]

    def test_todos_os_campos_ausentes(self):
        parecer = triar(_carregar("borda/todos_campos_ausentes.json"))
        assert parecer.parecer == REVISAO_HUMANA
        assert len(parecer.motivos) == 7
        assert all(m.regra == "R6" for m in parecer.motivos)
        assert len(parecer.pendencias) == 7

    def test_id_invalido_usa_apelido_sem_id(self):
        parecer = triar(_carregar("borda/campo_id_ausente.json"))
        assert parecer.proposta_id == "sem-id"
        assert parecer.parecer == REVISAO_HUMANA

    def test_area_negativa_nao_recusa_errado_revisa(self):
        # -50 < 100 recusaria "na letra", mas área negativa é dado quebrado:
        # a decisão foi mandar para revisão humana (R6), não recusar.
        parecer = triar(_carregar("borda/area_negativa.json"))
        assert [m.regra for m in parecer.motivos] == ["R6"]
        assert parecer.parecer == REVISAO_HUMANA

    def test_campo_extra_nao_afeta_o_parecer(self):
        proposta = _carregar("P-001.json")
        proposta["municipio"] = "Uberlândia"
        proposta["observacoes"] = "qualquer coisa"
        assert triar(proposta).parecer == SEGUE

    def test_determinismo_mesma_entrada_mesma_saida(self):
        dados = _carregar("P-004.json")
        assert triar(dados).to_dict() == triar(dados).to_dict()


class TestEntradaInvalida:
    @pytest.mark.parametrize("entrada", [[], "texto", 42, None, [{"id": "x"}]])
    def test_entrada_que_nao_e_objeto_levanta_erro(self, entrada):
        with pytest.raises(EntradaInvalida):
            triar(entrada)
