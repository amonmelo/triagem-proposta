"""Testes unitários das regras R1–R6 e da validação de campos."""
from datetime import date, datetime

import pytest

from triagem.modelo import CAMPOS_OBRIGATORIOS, RECUSADA, REVISAO_HUMANA
from triagem.regras import (
    interpretar_data,
    r1_area_degradada,
    r2_alerta_desmatamento,
    r3_situacao_car,
    r4_situacao_cadastral,
    r5_area_matricula_vs_car,
    validar_campos,
)

PROPOSTA_BASE = {
    "id": "T-1",
    "area_degradada_ha": 300,
    "area_matricula_ha": 500,
    "area_car_ha": 490,
    "alerta_desmatamento": None,
    "situacao_car": "Ativo",
    "situacao_cadastral": "Regular",
}


class TestInterpretarData:
    @pytest.mark.parametrize(
        "entrada,esperado",
        [
            ("2020-01-01", date(2020, 1, 1)),
            ("15/03/2023", date(2023, 3, 15)),
            ("2020-01-01T23:59:59", date(2020, 1, 1)),  # hora descartada
            ("2020-01-01 10:00", date(2020, 1, 1)),
            (" 2020-01-01 ", date(2020, 1, 1)),
            (date(2021, 6, 1), date(2021, 6, 1)),
            (datetime(2021, 6, 1, 12, 0), date(2021, 6, 1)),
        ],
    )
    def test_reconhece_formatos(self, entrada, esperado):
        assert interpretar_data(entrada) == esperado

    @pytest.mark.parametrize(
        "entrada",
        [None, "", "   ", "banana", "32/13/2021", "2021-13-01", 20210315, [], True],
    )
    def test_formato_estranho_devolve_none(self, entrada):
        assert interpretar_data(entrada) is None


class TestR1AreaDegradada:
    @pytest.mark.parametrize("area", [100, 100.0, 850, 10_000])
    def test_aceita_a_partir_de_100(self, area):
        violacao, detalhe = r1_area_degradada(float(area))
        assert violacao is None
        assert "100" in detalhe

    @pytest.mark.parametrize("area", [99.99, 60, 0.1])
    def test_recusa_abaixo_de_100(self, area):
        violacao, _ = r1_area_degradada(area)
        assert violacao is not None
        assert violacao.regra == "R1"
        assert violacao.parecer_sugerido == RECUSADA


class TestR2AlertaDesmatamento:
    @pytest.mark.parametrize(
        "alerta",
        [
            None,  # nulo = sem alerta
            [],
            "2020-01-01",  # o próprio dia do corte não recusa (esclarecimento)
            "01/01/2020",
            "2020-01-01T23:59:59",  # ainda é 01/01
            "2019-12-31",
            date(2020, 1, 1),
            ["2019-06-01", "01/01/2020"],
            ["2018-12-31", "2019-01-01"],
        ],
    )
    def test_nao_recusa(self, alerta):
        violacao, _ = r2_alerta_desmatamento(alerta)
        assert violacao is None

    @pytest.mark.parametrize(
        "alerta",
        [
            "2020-01-02",  # um dia depois do corte já recusa
            "02/01/2020",
            "15/03/2023",
            "2026-05-05",
            ["2019-06-01", "2020-01-02"],  # basta um alerta posterior
            ["01/01/2020", "15/03/2023"],
        ],
    )
    def test_recusa_alerta_posterior_ao_corte(self, alerta):
        violacao, _ = r2_alerta_desmatamento(alerta)
        assert violacao is not None
        assert violacao.regra == "R2"
        assert violacao.parecer_sugerido == RECUSADA

    @pytest.mark.parametrize(
        "alerta",
        ["banana", "32/13/2021", "", "   ", ["banana"], ["2019-01-01", "banana"], [None]],
    )
    def test_formato_ilegivel_vai_para_revisao(self, alerta):
        violacao, _ = r2_alerta_desmatamento(alerta)
        assert violacao is not None
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert violacao.pendencia  # revisão humana sempre vem com ação concreta

    @pytest.mark.parametrize(
        "alerta",
        ["2099-01-01", "31/12/2030", ["2019-01-01", "2099-01-01"]],
    )
    def test_data_no_futuro_vai_para_revisao(self, alerta):
        # Data que ainda não chegou é erro de digitação, não alerta: não recusa.
        violacao, _ = r2_alerta_desmatamento(alerta, hoje=date(2026, 10, 19))
        assert violacao is not None
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert "futuro" in violacao.mensagem
        assert violacao.pendencia

    def test_alerta_real_vence_data_no_futuro_na_mesma_lista(self):
        violacao, _ = r2_alerta_desmatamento(
            ["2099-01-01", "15/03/2023"], hoje=date(2026, 10, 19)
        )
        assert violacao.parecer_sugerido == RECUSADA

    def test_data_de_hoje_ainda_conta_como_alerta(self):
        violacao, _ = r2_alerta_desmatamento("2026-10-19", hoje=date(2026, 10, 19))
        assert violacao.parecer_sugerido == RECUSADA

    def test_recusa_cita_a_data_recebida(self):
        violacao, _ = r2_alerta_desmatamento("15/03/2023")
        assert "15/03/2023" in violacao.mensagem

    def test_ilegivel_cita_o_valor_recebido(self):
        violacao, _ = r2_alerta_desmatamento("banana")
        assert "banana" in violacao.mensagem


class TestR3SituacaoCar:
    @pytest.mark.parametrize("valor", ["Ativo", "ativo", "ATIVO", "  ativo  ", "Ativo\t"])
    def test_ativo_passa(self, valor):
        violacao, _ = r3_situacao_car(valor)
        assert violacao is None

    @pytest.mark.parametrize("valor", ["Pendente", "pendente", "PENDENTE", " Pendente "])
    def test_pendente_vai_para_revisao(self, valor):
        violacao, _ = r3_situacao_car(valor)
        assert violacao is not None
        assert violacao.parecer_sugerido == REVISAO_HUMANA

    @pytest.mark.parametrize("valor", ["Cancelado", "cancelado", "Suspenso", "SUSPENSO"])
    def test_cancelado_ou_suspenso_recusa(self, valor):
        violacao, _ = r3_situacao_car(valor)
        assert violacao is not None
        assert violacao.parecer_sugerido == RECUSADA

    @pytest.mark.parametrize("valor", ["Em análise", "Ativa", "Pendente de regularização"])
    def test_valor_fora_da_lista_vai_para_revisao_citando_valor(self, valor):
        violacao, _ = r3_situacao_car(valor)
        assert violacao is not None
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert valor in violacao.mensagem  # esclarecimento: citar o valor recebido


class TestR4SituacaoCadastral:
    @pytest.mark.parametrize("valor", ["Regular", "regular", "REGULAR", " regular "])
    def test_regular_passa(self, valor):
        violacao, _ = r4_situacao_cadastral(valor)
        assert violacao is None

    @pytest.mark.parametrize(
        "valor", ["Pendente de regularização", "Suspenso", "Irregular", "Nulo"]
    )
    def test_qualquer_outra_coisa_vai_para_revisao(self, valor):
        violacao, _ = r4_situacao_cadastral(valor)
        assert violacao is not None
        assert violacao.regra == "R4"
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert valor in violacao.mensagem


class TestR5MatriculaVsCar:
    @pytest.mark.parametrize(
        "matricula,car",
        [
            (1200, 1190),   # 0,83%
            (2000, 1900),   # exatamente 5% — passa (borda pedida no teste)
            (2000, 2100),   # CAR maior, exatamente 5% no outro sentido
            (900, 945),     # exatamente 5% (45/900)
            (100, 100),     # idênticas
        ],
    )
    def test_dentro_da_tolerancia_passa(self, matricula, car):
        violacao, _ = r5_area_matricula_vs_car(float(matricula), float(car))
        assert violacao is None

    @pytest.mark.parametrize(
        "matricula,car",
        [
            (900, 1000),      # P-003: 11,11%
            (2000, 1899.99),  # um fio acima de 5%
            (2000, 2100.01),  # um fio acima, CAR maior
        ],
    )
    def test_acima_de_5_por_cento_revisa(self, matricula, car):
        violacao, _ = r5_area_matricula_vs_car(float(matricula), float(car))
        assert violacao is not None
        assert violacao.regra == "R5"
        assert violacao.parecer_sugerido == REVISAO_HUMANA

    def test_mensagem_cita_o_percentual(self):
        violacao, _ = r5_area_matricula_vs_car(900, 1000)
        assert "11.11%" in violacao.mensagem


class TestR6ValidarCampos:
    def test_base_nao_tem_violacao(self):
        resultado = validar_campos(PROPOSTA_BASE)
        assert resultado["violacoes"] == []
        assert len(resultado["valores"]) == 7

    def test_alerta_nulo_e_dado_valido(self):
        # esclarecimento do enunciado: alerta_desmatamento nulo = sem alerta
        resultado = validar_campos({**PROPOSTA_BASE, "alerta_desmatamento": None})
        assert resultado["violacoes"] == []
        assert resultado["valores"]["alerta_desmatamento"] is None

    @pytest.mark.parametrize("campo", list(CAMPOS_OBRIGATORIOS))
    def test_campo_ausente(self, campo):
        proposta = {k: v for k, v in PROPOSTA_BASE.items() if k != campo}
        resultado = validar_campos(proposta)
        assert len(resultado["violacoes"]) == 1
        violacao = resultado["violacoes"][0]
        assert violacao.regra == "R6"
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert f"`{campo}`" in violacao.mensagem  # diz qual campo falta
        assert campo not in resultado["valores"]

    def test_objeto_vazio_gera_sete_violacoes(self):
        resultado = validar_campos({})
        assert len(resultado["violacoes"]) == 7
        assert all(v.regra == "R6" for v in resultado["violacoes"])

    # O alerta fica de fora: nele, nulo é "sem alerta", não ausência.
    @pytest.mark.parametrize(
        "campo", [c for c in CAMPOS_OBRIGATORIOS if c != "alerta_desmatamento"]
    )
    def test_nulo_equivale_a_ausente_para_os_demais_campos(self, campo):
        resultado = validar_campos({**PROPOSTA_BASE, campo: None})
        assert len(resultado["violacoes"]) == 1
        assert resultado["violacoes"][0].regra == "R6"

    @pytest.mark.parametrize(
        "campo,valor_ruim",
        [
            ("id", 123),
            ("id", ""),
            ("id", "   "),
            ("area_degradada_ha", "850"),   # número escrito como texto
            ("area_degradada_ha", True),    # bool é armadilha clássica em Python
            ("area_degradada_ha", -50),     # área negativa não existe
            ("area_degradada_ha", 0),       # zero também não
            ("area_degradada_ha", float("inf")),  # json.loads aceita Infinity
            ("area_car_ha", float("nan")),
            ("area_matricula_ha", 0),
            ("area_car_ha", -1),
            ("alerta_desmatamento", 5),     # número não é data
            ("alerta_desmatamento", {"data": "2021-01-01"}),
            ("situacao_car", 7),
            ("situacao_car", ""),
            ("situacao_car", "\t \n"),
            ("situacao_cadastral", ["Regular"]),
            ("situacao_cadastral", "   "),
        ],
    )
    def test_valor_inutilizavel(self, campo, valor_ruim):
        resultado = validar_campos({**PROPOSTA_BASE, campo: valor_ruim})
        assert len(resultado["violacoes"]) == 1
        violacao = resultado["violacoes"][0]
        assert violacao.regra == "R6"
        assert violacao.parecer_sugerido == REVISAO_HUMANA
        assert f"`{campo}`" in violacao.mensagem
        assert violacao.pendencia

    def test_campo_extra_e_ignorado(self):
        resultado = validar_campos({**PROPOSTA_BASE, "municipio": "Uberlândia"})
        assert resultado["violacoes"] == []
