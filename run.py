"""Atalho para rodar de qualquer pasta (ex.: Claude Desktop):

    python caminho/para/esta/pasta/run.py proposta.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from triagem.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
