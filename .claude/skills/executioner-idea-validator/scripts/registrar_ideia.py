#!/usr/bin/env python3
"""Registra uma ideia avaliada no banco de ideias (output/).

Deterministico por construcao: mesmo JSON de entrada + mesmo --datahora produz
byte a byte o mesmo arquivo. O slug, a pasta de destino, a ordem das secoes e a
ordenacao do indice sao todos derivados dos dados, nunca de julgamento.

Uso:
    python3 registrar_ideia.py --json ideia.json
    cat ideia.json | python3 registrar_ideia.py
    python3 registrar_ideia.py --json ideia.json --dry-run
    python3 registrar_ideia.py --reindex          # so reconstroi INDEX.md/banco.json

Contrato do JSON: veja assets/ideia.exemplo.json e references/banco-de-ideias.md.
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scorecard import (PILARES, ROTULOS, PESOS, STATUS_PASTA, CATEGORIA_EMOJI,
                       DECISAO_FINAL, classificar, media_ponderada,
                       recompensa_potencial, veredito_risco)
from taxonomia import validar

CAMPOS_TEXTO = (
    "titulo",
    "escopo_proposta",
    "problema",
    "quem_sofre",
    "arquitetura_agentes",
    "fontes_dados",
    "gargalo",
    "pai",
    "justificativa_horizonte",
    "justificativa_risco_tecnico",
)
CAMPOS_LISTA = ("riscos", "proximos_passos")

STATUS_ROTULO = {
    "APROVADA": "APROVADA",
    "EM_OBSERVACAO": "EM OBSERVACAO",
    "REPROVADA": "REPROVADA",
}


# --------------------------------------------------------------------------- #
# helpers deterministicos
# --------------------------------------------------------------------------- #
def slugificar(titulo: str) -> str:
    base = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    base = re.sub(r"-{2,}", "-", base)[:60].strip("-")
    if not base:
        raise ValueError("titulo nao gera slug valido (use ao menos uma letra ou digito)")
    return base


def aspas(valor: str) -> str:
    return '"' + str(valor).replace("\\", "\\\\").replace('"', '\\"') + '"'


def desaspas(valor: str) -> str:
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        valor = valor[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return valor


def ler_frontmatter(texto: str) -> dict:
    """Parser minimo para o frontmatter que ESTE script gera (escalares e listas)."""
    if not texto.startswith("---\n"):
        return {}
    fim = texto.find("\n---\n", 4)
    if fim == -1:
        return {}
    dados, chave_lista = {}, None
    for linha in texto[4:fim].split("\n"):
        if not linha.strip():
            continue
        if linha.startswith("  - ") and chave_lista:
            dados[chave_lista].append(desaspas(linha[4:]))
            continue
        chave, _, valor = linha.partition(":")
        chave = chave.strip()
        if valor.strip():
            dados[chave], chave_lista = desaspas(valor), None
        else:
            dados[chave], chave_lista = [], chave
    return dados


def ler_historico(texto: str) -> list:
    """Recupera as linhas da tabela de historico de um arquivo ja existente."""
    linhas = []
    dentro = False
    for linha in texto.split("\n"):
        if linha.startswith("## Historico de avaliacoes"):
            dentro = True
            continue
        if dentro:
            if linha.startswith("## "):
                break
            if linha.startswith("| ") and not re.match(r"^\|[\s\-|]+\|$", linha):
                celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
                if celulas and celulas[0].lower() not in ("data/hora", ""):
                    linhas.append(celulas)
    return linhas


# --------------------------------------------------------------------------- #
# validacao
# --------------------------------------------------------------------------- #
def validar_payload(d: dict) -> dict:
    opcionais = ("justificativa_horizonte", "justificativa_risco_tecnico")
    faltando = [c for c in CAMPOS_TEXTO if c not in opcionais and not str(d.get(c, "")).strip()]
    if faltando:
        raise ValueError("campos de texto obrigatorios ausentes ou vazios: " + ", ".join(faltando))

    for campo in CAMPOS_LISTA:
        valores = d.get(campo)
        if not isinstance(valores, list) or not valores or not all(str(v).strip() for v in valores):
            raise ValueError(f"{campo}: esperada lista nao vazia de strings")

    notas = d.get("notas")
    if not isinstance(notas, dict):
        raise ValueError("notas: esperado objeto com dor/agente/defesa/escala")
    for pilar in PILARES:
        v = notas.get(pilar)
        if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 5:
            raise ValueError(f"notas.{pilar}: esperado inteiro de 1 a 5 (recebido {v!r}). "
                             "Pilar sem dados = veredicto INSUFICIENTE: NAO registre no banco.")

    just = d.get("justificativas")
    if not isinstance(just, dict) or any(not str(just.get(p, "")).strip() for p in PILARES):
        raise ValueError("justificativas: exigida uma frase por pilar (dor/agente/defesa/escala)")

    validar("dominio_negocio", str(d.get("dominio_negocio", "")))
    validar("potencial_produto_real", str(d.get("potencial_produto_real", "")))
    validar("horizonte", str(d.get("horizonte", "")))
    validar("risco_tecnico", str(d.get("risco_tecnico", "")))

    dk = d.get("death_knell")
    if not isinstance(dk, dict) or not str(dk.get("condicao", "")).strip():
        raise ValueError("death_knell: esperado objeto {condicao, prazo} com condicao "
                         "objetiva e verificavel")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(dk.get("prazo", ""))):
        raise ValueError("death_knell.prazo: esperada data ISO (YYYY-MM-DD), no maximo "
                         "7 dias apos a avaliacao")

    funcoes = d.get("funcao_negocio")
    if not isinstance(funcoes, list) or not 1 <= len(funcoes) <= 3:
        raise ValueError("funcao_negocio: esperada lista com 1 a 3 funcoes TOGAF")
    for f in funcoes:
        validar("funcao_negocio", str(f))
    if len(set(funcoes)) != len(funcoes):
        raise ValueError("funcao_negocio: funcoes duplicadas")

    tags = d.get("tags", [])
    if not isinstance(tags, list) or any(not str(t).strip() for t in tags):
        raise ValueError("tags: esperada lista de strings nao vazias")
    return d


# --------------------------------------------------------------------------- #
# renderizacao
# --------------------------------------------------------------------------- #
def render(d: dict, media: Decimal, status: str, slug: str,
           criado_em: str, agora: str, historico: list) -> str:
    notas, just = d["notas"], d["justificativas"]
    funcoes = [str(f) for f in d["funcao_negocio"]]
    tags = sorted({str(t).strip().lower() for t in d.get("tags", [])})
    recompensa = recompensa_potencial(notas)
    risco = str(d["risco_tecnico"])
    verd_risco = veredito_risco(risco, recompensa)
    decisao = DECISAO_FINAL[status]
    dk = d["death_knell"]

    fm = [
        "---",
        f"id: {aspas(slug)}",
        f"titulo: {aspas(d['titulo'])}",
        f"status: {aspas(status)}",
        f"media_ponderada: {media}",
        f"dominio_negocio: {aspas(d['dominio_negocio'])}",
        "funcao_negocio:",
        *[f"  - {aspas(f)}" for f in funcoes],
        f"horizonte: {aspas(d['horizonte'])}",
        f"potencial_produto_real: {aspas(d['potencial_produto_real'])}",
        f"risco_tecnico: {aspas(risco)}",
        f"recompensa_potencial: {aspas(recompensa)}",
        f"decisao: {aspas(decisao)}",
        f"death_knell_prazo: {aspas(dk['prazo'])}",
        f"death_knell_condicao: {aspas(str(dk['condicao']).strip())}",
        *[f"nota_{p}: {notas[p]}" for p in PILARES],
        f"criado_em: {aspas(criado_em)}",
        f"atualizado_em: {aspas(agora)}",
        "tags:",
        *[f"  - {aspas(t)}" for t in tags],
        "---",
        "",
    ]

    cab = [
        f"# {d['titulo']}",
        "",
        "| Campo | Valor |",
        "| --- | --- |",
        f"| **Titulo** | {d['titulo']} |",
        f"| **Data/hora do registro** | {criado_em} |",
        f"| **Ultima avaliacao** | {agora} |",
        f"| **Dominio de negocio** | {d['dominio_negocio']} |",
        f"| **Funcao de negocio (TOGAF)** | {' · '.join(funcoes)} |",
        f"| **Status** | **{STATUS_ROTULO[status]}** ({media}/5.00) |",
        f"| **Horizonte** | {d['horizonte']} |",
        f"| **Potencial de produto real** | {d['potencial_produto_real']} |",
        f"| **Risco vs recompensa** | Risco {risco} x Recompensa {recompensa} — {verd_risco} |",
        f"| **Decisão** | {CATEGORIA_EMOJI[status]} {decisao} |",
        f"| **Death knell** | {str(dk['condicao']).strip()} (prazo: {dk['prazo']}) |",
        f"| **Tags** | {', '.join(tags) if tags else '—'} |",
        "",
    ]

    corpo = [
        "## Escopo da proposta",
        "",
        d["escopo_proposta"].strip(),
        "",
        "## Problema e quem sofre",
        "",
        f"**Problema.** {d['problema'].strip()}",
        "",
        f"**Quem sofre.** {d['quem_sofre'].strip()}",
        "",
        "## Arquitetura de agentes",
        "",
        d["arquitetura_agentes"].strip(),
        "",
        "## Fontes de dados e defensibilidade",
        "",
        d["fontes_dados"].strip(),
        "",
        "## Scorecard",
        "",
        "| Pilar | Peso | Nota | Justificativa |",
        "| --- | --- | --- | --- |",
        *[f"| {ROTULOS[p]} | {PESOS[p]} | {notas[p]}/5 | {str(just[p]).strip()} |"
          for p in PILARES],
        f"| **Media ponderada** | | **{media}/5.00** | Faixa: {STATUS_ROTULO[status]} |",
        "",
        "## Veredicto",
        "",
        f"**{STATUS_ROTULO[status]}** — media ponderada {media}/5.00 "
        f"({' + '.join(f'{PESOS[p]}x{notas[p]}' for p in PILARES)}).",
        "",
        "## Matriz risco vs recompensa",
        "",
        f"**Recompensa potencial:** {recompensa} — derivada das notas de Dor "
        f"({notas['dor']}/5) e Escala ({notas['escala']}/5).",
        "",
        f"**Risco técnico:** {risco}. "
        + (str(d.get("justificativa_risco_tecnico", "")).strip()
           or "_Sem justificativa registrada._"),
        "",
        f"**Veredito do risco:** {verd_risco}",
        "",
        "## Cirurgia — gargalo unico",
        "",
        d["gargalo"].strip(),
        "",
        "## Plano de acao imediato (48h)",
        "",
        d["pai"].strip(),
        "",
        "## Death knell",
        "",
        f"**Condição:** {str(dk['condicao']).strip()}",
        "",
        f"**Prazo:** {dk['prazo']}. Não cumprida até esta data, a ideia é enterrada — "
        "reavalie com a condição como evidência negativa ou arquive.",
        "",
        "## Potencial fora do hackathon",
        "",
        f"**Horizonte:** {d['horizonte']} · **Potencial de produto real:** "
        f"{d['potencial_produto_real']}",
        "",
        str(d.get("justificativa_horizonte", "")).strip()
        or "_Sem analise de horizonte registrada nesta avaliacao._",
        "",
        "## Riscos e premissas",
        "",
        *[f"- {str(r).strip()}" for r in d["riscos"]],
        "",
        "## Proximos passos",
        "",
        *[f"{i}. {str(p).strip()}" for i, p in enumerate(d["proximos_passos"], 1)],
        "",
        "## Historico de avaliacoes",
        "",
        "| Data/hora | Media | Status | Observacao |",
        "| --- | --- | --- | --- |",
        *[f"| {' | '.join(linha)} |" for linha in historico],
        "",
    ]
    return "\n".join(fm + cab + corpo)


def construir_indice(raiz: Path) -> tuple:
    registros = []
    for status, pasta in STATUS_PASTA.items():
        for arquivo in sorted((raiz / pasta).glob("*.md")):
            fm = ler_frontmatter(arquivo.read_text(encoding="utf-8"))
            if not fm.get("id"):
                continue
            fm["_status"] = status
            fm["_path"] = f"{pasta}/{arquivo.name}"
            registros.append(fm)

    linhas = [
        "# Banco de ideias — indice",
        "",
        "> Arquivo GERADO por `scripts/registrar_ideia.py`. Nao edite a mao:",
        "> qualquer registro ou `--reindex` sobrescreve.",
        "",
        f"Total de ideias no banco: **{len(registros)}**",
        "",
    ]
    for status, pasta in STATUS_PASTA.items():
        grupo = sorted(
            [r for r in registros if r["_status"] == status],
            key=lambda r: (-float(r.get("media_ponderada", 0)), r["id"]),
        )
        linhas += [
            f"## {STATUS_ROTULO[status]} ({len(grupo)})",
            "",
        ]
        if not grupo:
            linhas += ["_Nenhuma ideia nesta faixa._", ""]
            continue
        linhas += [
            "| Ideia | Media | Dominio | Funcao primaria | Horizonte | Potencial | Atualizado |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in grupo:
            funcao = r.get("funcao_negocio") or ["—"]
            linhas.append(
                f"| [{r.get('titulo', r['id'])}]({r['_path']}) "
                f"| {r.get('media_ponderada', '—')} "
                f"| {r.get('dominio_negocio', '—')} "
                f"| {funcao[0]} "
                f"| {r.get('horizonte', '—')} "
                f"| {r.get('potencial_produto_real', '—')} "
                f"| {r.get('atualizado_em', '—')} |"
            )
        linhas.append("")

    todos = sorted(
        registros,
        key=lambda r: (-float(r.get("media_ponderada", 0)), r["id"]),
    )
    linhas += [
        "## Quadro comparativo",
        "",
        "| Ideia | Media | Categoria | Risco vs Recompensa | Death Knell (Prazo) | Decisao Final |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in todos:
        risco_rr = (f"Risco {r['risco_tecnico']} x Recompensa {r['recompensa_potencial']}"
                    if r.get("risco_tecnico") and r.get("recompensa_potencial") else "—")
        dk_cel = (f"{r['death_knell_condicao']} ({r['death_knell_prazo']})"
                  if r.get("death_knell_condicao") and r.get("death_knell_prazo") else "—")
        linhas.append(
            f"| [{r.get('titulo', r['id'])}]({r['_path']}) "
            f"| {r.get('media_ponderada', '—')} "
            f"| {CATEGORIA_EMOJI[r['_status']]} "
            f"| {risco_rr} "
            f"| {dk_cel} "
            f"| {r.get('decisao') or DECISAO_FINAL[r['_status']]} |"
        )
    linhas.append("")

    joias = sorted(
        [r for r in registros if r.get("horizonte") in ("PRODUTO", "HACKATHON_E_PRODUTO")],
        key=lambda r: (-float(r.get("media_ponderada", 0)), r["id"]),
    )
    linhas += [
        "## Radar de produto real",
        "",
        "Ideias com horizonte PRODUTO ou HACKATHON_E_PRODUTO — inclusive reprovadas no",
        "framework do edital. Sao os ativos que sobrevivem ao hackathon.",
        "",
    ]
    if joias:
        linhas += ["| Ideia | Status no edital | Media | Horizonte | Potencial |",
                   "| --- | --- | --- | --- | --- |"]
        linhas += [
            f"| [{r.get('titulo', r['id'])}]({r['_path']}) | {STATUS_ROTULO[r['_status']]} "
            f"| {r.get('media_ponderada', '—')} | {r.get('horizonte', '—')} "
            f"| {r.get('potencial_produto_real', '—')} |"
            for r in joias
        ]
    else:
        linhas.append("_Nenhuma ideia com potencial fora do hackathon ate agora._")
    linhas.append("")

    banco = {
        "total": len(registros),
        "ideias": [
            {
                "id": r["id"],
                "titulo": r.get("titulo"),
                "status": r["_status"],
                "media_ponderada": float(r.get("media_ponderada", 0)),
                "dominio_negocio": r.get("dominio_negocio"),
                "funcao_negocio": r.get("funcao_negocio", []),
                "horizonte": r.get("horizonte"),
                "potencial_produto_real": r.get("potencial_produto_real"),
                "risco_tecnico": r.get("risco_tecnico"),
                "recompensa_potencial": r.get("recompensa_potencial"),
                "decisao": r.get("decisao"),
                "death_knell": (
                    {"condicao": r.get("death_knell_condicao"),
                     "prazo": r.get("death_knell_prazo")}
                    if r.get("death_knell_prazo") else None
                ),
                "notas": {p: int(r.get(f"nota_{p}", 0)) for p in PILARES},
                "tags": r.get("tags", []),
                "criado_em": r.get("criado_em"),
                "atualizado_em": r.get("atualizado_em"),
                "arquivo": r["_path"],
            }
            for r in sorted(registros, key=lambda r: r["id"])
        ],
    }
    return "\n".join(linhas), banco


def escrever_indice(raiz: Path) -> int:
    indice, banco = construir_indice(raiz)
    (raiz / "INDEX.md").write_text(indice, encoding="utf-8")
    (raiz / "banco.json").write_text(
        json.dumps(banco, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return banco["total"]


# --------------------------------------------------------------------------- #
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", type=Path, help="arquivo JSON da ideia (padrao: stdin)")
    p.add_argument("--output-dir", type=Path, default=Path("output"),
                   help="raiz do banco (padrao: ./output)")
    p.add_argument("--datahora", help="ISO-8601 fixo, para reprodutibilidade/testes")
    p.add_argument("--dry-run", action="store_true", help="mostra o destino e nao grava")
    p.add_argument("--reindex", action="store_true",
                   help="apenas reconstroi INDEX.md e banco.json")
    a = p.parse_args()

    raiz = a.output_dir
    for pasta in STATUS_PASTA.values():
        (raiz / pasta).mkdir(parents=True, exist_ok=True)

    if a.reindex:
        total = escrever_indice(raiz)
        print(f"Indice reconstruido: {total} ideia(s) em {raiz}/")
        return 0

    bruto = a.json.read_text(encoding="utf-8") if a.json else sys.stdin.read()
    try:
        d = validar_payload(json.loads(bruto))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2

    agora = a.datahora or datetime.now().astimezone().isoformat(timespec="seconds")
    media = media_ponderada(d["notas"])
    status = classificar(media)
    slug = slugificar(d["titulo"])
    destino = raiz / STATUS_PASTA[status] / f"{slug}.md"

    anterior, criado_em, historico = None, agora, []
    for pasta in STATUS_PASTA.values():
        candidato = raiz / pasta / f"{slug}.md"
        if candidato.exists():
            anterior = candidato
            texto = candidato.read_text(encoding="utf-8")
            criado_em = ler_frontmatter(texto).get("criado_em") or agora
            historico = ler_historico(texto)
            break

    observacao = str(d.get("observacao_revisao", "")).strip() or (
        "Registro inicial." if anterior is None else "Reavaliacao."
    )
    linha_nova = [agora, str(media), STATUS_ROTULO[status], observacao.replace("|", "/")]
    if not historico or historico[-1][:3] != linha_nova[:3]:
        historico.append(linha_nova)

    conteudo = render(d, media, status, slug, criado_em, agora, historico)

    if a.dry_run:
        print(f"[dry-run] destino: {destino}")
        if anterior and anterior != destino:
            print(f"[dry-run] mover de: {anterior}")
        print(f"[dry-run] media {media} -> {status}")
        return 0

    destino.write_text(conteudo, encoding="utf-8")
    movido = ""
    if anterior and anterior != destino:
        anterior.unlink()
        movido = f" (movida de {anterior.parent.name}/)"

    total = escrever_indice(raiz)
    acao = "Atualizada" if anterior else "Registrada"
    print(f"{acao}: {destino}{movido}")
    print(f"Status: {STATUS_ROTULO[status]} | Media: {media}/5.00 | "
          f"Horizonte: {d['horizonte']}")
    print(f"Indice atualizado: {raiz}/INDEX.md ({total} ideia(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
