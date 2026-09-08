#!/usr/bin/env python3
"""Calcula o scorecard ponderado do Framework Executioner de 4 Pilares.

Tambem e a fonte unica de verdade dos pesos, do arredondamento e das faixas de
veredicto -- `registrar_ideia.py` importa deste modulo.

Uso:
    python3 scorecard.py --dor 4 --agente 5 --defesa 3 --escala 4 --demoavel SIM
    python3 scorecard.py --dor 4 --agente 5 --pilar-insuficiente defesa --escala 4 --demoavel SIM
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
    "NAO_DEMONSTRAVEL": "ideias-nao-demonstraveis",
    "REPROVADA": "ideias-reprovadas",
}

# status -> emoji de categoria e decisao final do quadro comparativo
CATEGORIA_EMOJI = {
    "APROVADA": "🟢",
    "EM_OBSERVACAO": "🟡",
    "NAO_DEMONSTRAVEL": "🟠",
    "REPROVADA": "🔴",
}
DECISAO_FINAL = {
    "APROVADA": "Avancar",
    "EM_OBSERVACAO": "Observar",
    "NAO_DEMONSTRAVEL": "Resolver Demo",
    "REPROVADA": "Arquivar",
}

# Matriz risco vs recompensa (qualitativa, deterministica).
# Recompensa e DERIVADA das notas (Pilares 1 e 4); risco tecnico e insumo
# julgado pela rubrica de references/framework-pilares.md.
MATRIZ_RISCO = {
    ("BAIXO", "ALTA"): "Barbada - execute ja.",
    ("BAIXO", "MEDIA"): "Vale o custo.",
    ("BAIXO", "BAIXA"): "Esforco pequeno, retorno pequeno.",
    ("MEDIO", "ALTA"): "Vale a pena.",
    ("MEDIO", "MEDIA"): "Aposta calculada.",
    ("MEDIO", "BAIXA"): "Provavelmente furada.",
    ("ALTO", "ALTA"): "Vale a pena.",
    ("ALTO", "MEDIA"): "Arriscada - so avance com mitigacao explicita.",
    ("ALTO", "BAIXA"): "Furada.",
}


def recompensa_potencial(notas: dict) -> str:
    """Derivada dos Pilares 1 (Dor) e 4 (Escala) - deterministica.

    ALTA: dor validada E problema com escala (ambas >= 4, ex.: LOI + nacional).
    BAIXA: dor no nivel do achismo (dor <= 2), qualquer que seja a escala.
    MEDIA: o resto.
    """
    if notas["dor"] >= 4 and notas["escala"] >= 4:
        return "ALTA"
    if notas["dor"] <= 2:
        return "BAIXA"
    return "MEDIA"


def veredito_risco(risco_tecnico: str, recompensa: str) -> str:
    return MATRIZ_RISCO[(risco_tecnico, recompensa)]


def media_ponderada(notas: dict) -> Decimal:
    """Media ponderada com arredondamento HALF_UP em 2 casas -- deterministico."""
    bruta = sum(PESOS[k] * Decimal(int(notas[k])) for k in PILARES)
    return bruta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def classificar(media: Decimal, demoavel: bool = True) -> str:
    """Faixas fechadas sobre a media JA arredondada.

    demoavel=False rebaixa uma media >=4.00 de APROVADA para NAO_DEMONSTRAVEL --
    a ideia da os pontos, mas nao pode ir pro backlog sem antes resolver a demo.
    Nao afeta as faixas abaixo de 4.00.
    """
    if media >= Decimal("4.00"):
        return "APROVADA" if demoavel else "NAO_DEMONSTRAVEL"
    if media >= Decimal("3.50"):
        return "EM_OBSERVACAO"
    return "REPROVADA"


def veredicto(media: Decimal, demoavel: bool = True) -> str:
    status = classificar(media, demoavel)
    if status == "APROVADA":
        return "[APROVADA] - vai para o backlog."
    if status == "NAO_DEMONSTRAVEL":
        return (f"[NAO DEMONSTRAVEL] - nota aprova ({media}/5.00), mas a ideia nao e "
                "demonstravel em 3 minutos offline: resolva a demo antes do backlog.")
    if status == "EM_OBSERVACAO":
        return "[EM OBSERVACAO] - faixa de cirurgia (3.50-3.99): um gargalo a resolver."
    return "[REPROVADA / DESCARTE] - nomeie a falha critica que derrubou a nota."


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    for pilar in PILARES:
        p.add_argument(f"--{pilar}", type=int, choices=range(1, 6), metavar="1-5")
    p.add_argument(
        "--risco-tecnico",
        choices=["ALTO", "MEDIO", "BAIXO"],
        help="risco tecnico da arquitetura, JULGADO pelo avaliador com a rubrica de "
             "framework-pilares.md - nunca copiado do texto da ideia; imprime a matriz "
             "risco vs recompensa",
    )
    p.add_argument(
        "--pilar-insuficiente",
        action="append",
        default=[],
        choices=list(PILARES),
        help="pilar sem dados suficientes (repetivel)",
    )
    p.add_argument(
        "--demoavel",
        choices=["SIM", "NAO"],
        required=True,
        help="a ideia e demonstravel em ate 3 minutos, offline, sem depender de API "
             "externa fragil? (rubrica: framework-pilares.md) NAO rebaixa uma media "
             ">=4.00 de APROVADA para NAO_DEMONSTRAVEL",
    )
    a = p.parse_args(argv)

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

    demoavel = a.demoavel == "SIM"
    media = media_ponderada(notas)
    parcelas = " + ".join(f"{PESOS[k]}x{notas[k]}" for k in PILARES)
    print(f"CONTA: {parcelas} = {media}")
    print(f"MEDIA PONDERADA: {media} / 5.00")
    print(f"DEMONSTRAVEL EM 3 MIN: {a.demoavel}")
    print(f"VEREDICTO: {veredicto(media, demoavel)}")
    print(f"DESTINO NO BANCO: output/{STATUS_PASTA[classificar(media, demoavel)]}/")
    recompensa = recompensa_potencial(notas)
    print(f"RECOMPENSA POTENCIAL: {recompensa} (derivada de Dor={notas['dor']} e Escala={notas['escala']})")
    if a.risco_tecnico:
        print(f"RISCO TECNICO: {a.risco_tecnico}")
        print(f"VEREDITO DO RISCO: {veredito_risco(a.risco_tecnico, recompensa)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
