"""Testes da linha de comando (saída, flags, diretório, stdin e erros)."""
import io
import json
from pathlib import Path

import pytest

from triagem.cli import main

PASTA_EXEMPLOS = Path(__file__).resolve().parents[1] / "exemplos"

PROPOSTA_OK = {
    "id": "CLI-1",
    "area_degradada_ha": 300,
    "area_matricula_ha": 500,
    "area_car_ha": 490,
    "alerta_desmatamento": None,
    "situacao_car": "Ativo",
    "situacao_cadastral": "Regular",
}


def test_arquivo_valido_saide_parecer_e_card(capsys):
    codigo = main([str(PASTA_EXEMPLOS / "P-002.json")])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert '"parecer": "RECUSADA"' in saida
    assert "# Triagem P-002" in saida
    assert f"===== {PASTA_EXEMPLOS / 'P-002.json'} =====" in saida


def test_flag_json_sai_so_o_json(capsys):
    main([str(PASTA_EXEMPLOS / "P-002.json"), "--json"])
    saida = capsys.readouterr().out
    assert '"parecer": "RECUSADA"' in saida
    assert "# Triagem" not in saida
    assert "=====" not in saida
    json.loads(saida)  # a saída inteira é um JSON válido


def test_flag_card_sai_so_o_card(capsys):
    main([str(PASTA_EXEMPLOS / "P-002.json"), "--card"])
    saida = capsys.readouterr().out
    assert saida.startswith("# Triagem P-002")
    assert '"parecer"' not in saida


def test_le_do_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(PROPOSTA_OK)))
    codigo = main(["-"])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert '"parecer": "SEGUE"' in saida
    assert "# Triagem CLI-1" in saida


def test_diretorio_processa_todos_os_json(capsys):
    esperados = len(list(PASTA_EXEMPLOS.rglob("*.json")))
    codigo = main([str(PASTA_EXEMPLOS)])
    saida = capsys.readouterr().out
    assert codigo == 0
    assert saida.count("===== ") == esperados


def test_arquivo_inexistente(capsys):
    codigo = main(["definitivamente-nao-existe.json"])
    capturado = capsys.readouterr()
    assert codigo == 2
    assert "não consegui ler" in capturado.err


def test_json_invalido(tmp_path, capsys):
    arquivo = tmp_path / "quebrado.json"
    arquivo.write_text("{isso nao e json", encoding="utf-8")
    codigo = main([str(arquivo)])
    capturado = capsys.readouterr()
    assert codigo == 2
    assert "não é JSON válido" in capturado.err


def test_json_que_nao_e_objeto(tmp_path, capsys):
    arquivo = tmp_path / "lista.json"
    arquivo.write_text("[1, 2, 3]", encoding="utf-8")
    codigo = main([str(arquivo)])
    capturado = capsys.readouterr()
    assert codigo == 2
    assert "objeto JSON" in capturado.err


def test_lote_com_um_arquivo_ruim_processa_os_bons_e_devolve_erro(tmp_path, capsys):
    (tmp_path / "bom.json").write_text(json.dumps(PROPOSTA_OK), encoding="utf-8")
    (tmp_path / "ruim.json").write_text("{quebrado", encoding="utf-8")
    codigo = main([str(tmp_path), "--json"])
    saida = capsys.readouterr().out
    assert codigo == 2
    assert '"proposta_id": "CLI-1"' in saida  # o bom foi triado mesmo assim


def test_varios_arquivos_na_mesma_chamada(capsys):
    codigo = main(
        [
            str(PASTA_EXEMPLOS / "P-001.json"),
            str(PASTA_EXEMPLOS / "P-004.json"),
        ]
    )
    saida = capsys.readouterr().out
    assert codigo == 0
    assert "# Triagem P-001" in saida
    assert "# Triagem P-004" in saida
