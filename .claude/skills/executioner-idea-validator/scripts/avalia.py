#!/usr/bin/env python3
"""Atalho que roda scorecard.py e registrar_ideia.py em sequencia.

Complementa o workflow de dois comandos -- nao os substitui. Para o caso comum
em que o JSON da ideia ja esta completo, evita o risco de rodar so o scorecard
e esquecer o registro: `avalia.py` chama primeiro `scorecard.main()` (imprime o
scorecard formatado a partir dos campos do proprio JSON) e, se ele nao falhar,
chama `registrar_ideia.main()` com os mesmos argumentos relevantes.

Nao recalcula nem revalida nada: cada `main()` roda exatamente o parsing e a
validacao que ja tem, como se fosse chamado isoladamente. `avalia.py` so monta
o argv do scorecard a partir dos campos do JSON e propaga o primeiro exit code
diferente de zero -- pesos, faixas, sanitizacao e o detector de padroes
continuam vivendo so em scorecard.py/registrar_ideia.py.

Para conferir a conta antes de fechar o JSON, ou para rodar so --reindex, use
os scripts scorecard.py/registrar_ideia.py isolados: este atalho exige o JSON
completo desde o inicio e nao expoe --reindex.

Uso:
    python3 avalia.py --json ideia.json
    python3 avalia.py --json ideia.json --dry-run
    python3 avalia.py --json ideia.json --aceitar-padroes-suspeitos
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scorecard
import registrar_ideia as reg

ENV_TESTE = reg.ENV_TESTE


def _argv_scorecard(dados: dict):
    """Monta o argv de scorecard.py a partir dos campos do JSON da ideia.

    Devolve None se o JSON nao tiver os campos minimos para o preview -- nesse
    caso, avalia.py pula a etapa e vai direto para registrar_ideia.main(), que
    e quem reporta o erro real de schema (nao duplicamos essa validacao aqui).
    """
    try:
        notas = dados["notas"]
        argv = []
        for pilar in scorecard.PILARES:
            if isinstance(notas[pilar], bool):
                raise ValueError("nota booleana")
            argv += [f"--{pilar}", str(int(notas[pilar]))]
        argv += ["--demoavel", str(dados["demoavel"])]
        if dados.get("risco_tecnico"):
            argv += ["--risco-tecnico", str(dados["risco_tecnico"])]
        return argv
    except (KeyError, TypeError, ValueError):
        return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, required=True, help="arquivo JSON da ideia")
    p.add_argument("--output-dir", type=Path, default=Path("output"),
                   help="raiz do banco (padrao: ./output; fora do cwd so com "
                        f"{ENV_TESTE}=1)")
    p.add_argument("--datahora", help=f"ISO-8601 fixo, para testes (exige {ENV_TESTE}=1)")
    p.add_argument("--dry-run", action="store_true", help="mostra o destino e nao grava")
    p.add_argument("--aceitar-padroes-suspeitos", action="store_true",
                   help="registra mesmo com padroes de injecao detectados; so apos revisao "
                        "humana do texto. Fica anotado no historico.")
    a = p.parse_args(argv)

    try:
        dados = json.loads(a.json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        dados = None

    if isinstance(dados, dict):
        argv_scorecard = _argv_scorecard(dados)
        if argv_scorecard is not None:
            print("=== SCORECARD ===")
            codigo = scorecard.main(argv_scorecard)
            print()
            if codigo != 0:
                return codigo

    argv_registrar = ["--json", str(a.json), "--output-dir", str(a.output_dir)]
    if a.datahora:
        argv_registrar += ["--datahora", a.datahora]
    if a.dry_run:
        argv_registrar.append("--dry-run")
    if a.aceitar_padroes_suspeitos:
        argv_registrar.append("--aceitar-padroes-suspeitos")

    print("=== REGISTRO ===")
    return reg.main(argv_registrar)


if __name__ == "__main__":
    sys.exit(main())
