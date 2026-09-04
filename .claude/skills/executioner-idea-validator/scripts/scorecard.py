#!/usr/bin/env python3
"""Calcula o scorecard ponderado do Framework Executioner de 4 Pilares.

Tambem e a fonte unica de verdade dos pesos, do arredondamento e das faixas de
veredicto -- `registrar_ideia.py` importa deste modulo.

Uso:
    python3 scorecard.py --dor 4 --agente 5 --defesa 3 --escala 4
    python3 scorecard.py --dor 4 --agente 5 --pilar-insuficiente defesa --escala 4
"""

import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP

PILARES = ("dor", "agente", "defesa", "escala")

PESOS = {
    "dor": Decimal("0.30"),
    "agente": Decimal("0.30"),
    "defesa": Decimal("0.25"),
    "escala": Decimal("0.15"),
}

ROTULOS = {
    "dor": "Pilar 1 (Dor Real e Validacao)",
    "agente": "Pilar 2 (Centralidade do Agente)",
    "defesa": "Pilar 3 (Defensibilidade)",
    "escala": "Pilar 4 (Escala Nacional)",
}

# status -> (rotulo humano, pasta de destino em output/)
STATUS_PASTA = {
    "APROVADA": "ideias-aprovadas",
    "EM_OBSERVACAO": "ideias-em-observacao",
    "REPROVADA": "ideias-reprovadas",
}


def media_ponderada(notas: dict) -> Decimal:
    """Media ponderada com arredondamento HALF_UP em 2 casas -- deterministico."""
    bruta = sum(PESOS[k] * Decimal(int(notas[k])) for k in PILARES)
    return bruta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def classificar(media: Decimal) -> str:
    """Faixas fechadas sobre a media JA arredondada."""
    if media >= Decimal("4.00"):
        return "APROVADA"
    if media >= Decimal("3.50"):
        return "EM_OBSERVACAO"
    return "REPROVADA"


def veredicto(media: Decimal) -> str:
    status = classificar(media)
    if status == "APROVADA":
        return "[APROVADA] - vai para o backlog."
    if status == "EM_OBSERVACAO":
        return "[REPROVADA] - faixa de cirurgia (3.50-3.99): um gargalo a resolver."
    return "[REPROVADA / DESCARTE] - nomeie a falha critica que derrubou a nota."


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for pilar in PILARES:
        p.add_argument(f"--{pilar}", type=int, choices=range(1, 6), metavar="1-5")
    p.add_argument(
        "--pilar-insuficiente",
        action="append",
        default=[],
        choices=list(PILARES),
        help="pilar sem dados suficientes (repetivel)",
    )
    a = p.parse_args()

    insuficientes = list(dict.fromkeys(a.pilar_insuficiente))
    notas = {k: getattr(a, k) for k in PILARES}

    conflito = [k for k in insuficientes if notas[k] is not None]
    if conflito:
        p.error(f"pilar marcado como insuficiente nao pode ter nota: {', '.join(conflito)}")

    faltando = [k for k, v in notas.items() if v is None and k not in insuficientes]
    if faltando:
        p.error(f"informe a nota ou marque como insuficiente: {', '.join(faltando)}")

    print("SCORECARD EXECUTIONER")
    print("-" * 52)
    for k in PILARES:
        valor = "INSUFICIENTE" if k in insuficientes else f"{notas[k]}/5"
        print(f"{ROTULOS[k]:<38} peso {PESOS[k]}  {valor}")
    print("-" * 52)

    if insuficientes:
        print("MEDIA: nao calculada.")
        print("VEREDICTO: [INSUFICIENTE] - exija os dados de: " + ", ".join(insuficientes))
        print("Nao renormalize pesos, nao suponha notas e NAO registre no banco.")
        return 0

    media = media_ponderada(notas)
    parcelas = " + ".join(f"{PESOS[k]}x{notas[k]}" for k in PILARES)
    print(f"CONTA: {parcelas} = {media}")
    print(f"MEDIA PONDERADA: {media} / 5.00")
    print(f"VEREDICTO: {veredicto(media)}")
    print(f"DESTINO NO BANCO: output/{STATUS_PASTA[classificar(media)]}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
