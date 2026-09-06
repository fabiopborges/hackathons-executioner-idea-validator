#!/usr/bin/env python3
"""Vocabulario controlado do banco de ideias.

Classificacao livre destroi a comparabilidade do banco. Estes enums sao a fonte
unica de verdade: `registrar_ideia.py` rejeita qualquer valor fora deles, e
`references/taxonomia-negocio.md` e gerado a partir daqui (--markdown).

FUNCOES_NEGOCIO segue a decomposicao de Business Function da Business
Architecture do TOGAF (ADM Fase B): capacidades estaveis que a organizacao
exerce, independentes de estrutura organizacional ou de tecnologia.
"""

import sys

# Dominio de negocio = setor/industria em que a dor vive.
DOMINIOS_NEGOCIO = (
    "Agronegocio",
    "Construcao e Imobiliario",
    "Educacao",
    "Energia e Utilities",
    "Financeiro e Bancario",
    "Juridico",
    "Logistica e Transporte",
    "Manufatura e Industria",
    "Midia e Entretenimento",
    "Recursos Humanos e Servicos Profissionais",
    "Saude",
    "Seguros",
    "Setor Publico",
    "Tecnologia e SaaS",
    "Telecomunicacoes",
    "Turismo e Hospitalidade",
    "Varejo e E-commerce",
    "Transversal",
)

# Funcao de negocio = capacidade TOGAF que o agente executa ou apoia.
FUNCOES_NEGOCIO = (
    "Estrategia e Planejamento",
    "Marketing e Geracao de Demanda",
    "Vendas e Gestao de Canais",
    "Gestao de Clientes e Relacionamento",
    "Atendimento e Suporte ao Cliente",
    "Desenvolvimento de Produto e Servico",
    "Operacoes e Entrega de Servico",
    "Cadeia de Suprimentos e Logistica",
    "Manufatura e Producao",
    "Suprimentos e Compras",
    "Gestao de Ativos e Manutencao",
    "Gestao Financeira e Contabil",
    "Gestao de Riscos, Compliance e Auditoria",
    "Juridico e Contratos",
    "Gestao de Pessoas",
    "Gestao de Dados e Informacao",
    "Tecnologia da Informacao",
)

# Potencial de virar produto real fora do hackathon.
POTENCIAL_PRODUTO = ("ALTO", "MEDIO", "BAIXO")

# Risco tecnico da arquitetura proposta (rubrica em framework-pilares.md).
# Na duvida entre dois niveis, escolha o MAIOR - o inverso da regra das notas.
RISCO_TECNICO = ("ALTO", "MEDIO", "BAIXO")

# Horizonte de aproveitamento da ideia.
HORIZONTES = (
    "HACKATHON",          # serve para a competicao, e so
    "PRODUTO",            # nao ganha hackathon, mas vira negocio real
    "HACKATHON_E_PRODUTO",  # serve para os dois
    "NENHUM",             # nao serve para nada
)

_CAMPOS = {
    "dominio_negocio": DOMINIOS_NEGOCIO,
    "funcao_negocio": FUNCOES_NEGOCIO,
    "potencial_produto_real": POTENCIAL_PRODUTO,
    "horizonte": HORIZONTES,
    "risco_tecnico": RISCO_TECNICO,
}


def validar(campo: str, valor: str) -> str:
    permitidos = _CAMPOS[campo]
    if valor not in permitidos:
        raise ValueError(
            f"{campo}: valor invalido {valor!r}.\nPermitidos:\n  - "
            + "\n  - ".join(permitidos)
        )
    return valor


def _markdown() -> str:
    linhas = [
        "# Taxonomia de negocio do banco de ideias",
        "",
        "> Arquivo GERADO. Nao edite a mao -- a fonte e `scripts/taxonomia.py`.",
        "> Regenerar: `python3 scripts/taxonomia.py --markdown > references/taxonomia-negocio.md`",
        "",
        "Vocabulario controlado: `registrar_ideia.py` rejeita qualquer valor fora destas",
        "listas. Se nenhum termo servir, adicione-o em `scripts/taxonomia.py` e regenere",
        "este arquivo -- nunca improvise um rotulo novo no JSON da ideia.",
        "",
        "## Dominio de negocio (setor onde a dor vive)",
        "",
        "Escolha exatamente um. `Transversal` so quando a dor independe de setor.",
        "",
    ]
    linhas += [f"- {v}" for v in DOMINIOS_NEGOCIO]
    linhas += [
        "",
        "## Funcao de negocio (TOGAF Business Function)",
        "",
        "Capacidade que o agente executa ou apoia, conforme a decomposicao de Business",
        "Function da Business Architecture do TOGAF (ADM Fase B). Escolha de 1 a 3, da",
        "mais central para a menos central. Funcao e capacidade, nao departamento: se a",
        "ideia automatiza cobranca, a funcao e `Gestao Financeira e Contabil`, mesmo que",
        "na empresa isso caia no time de vendas.",
        "",
    ]
    linhas += [f"- {v}" for v in FUNCOES_NEGOCIO]
    linhas += [
        "",
        "## Potencial de produto real",
        "",
        "- **ALTO** — cliente pagante identificavel e dor recorrente; sobrevive sem o edital.",
        "- **MEDIO** — dor real, mas monetizacao ou canal ainda indefinidos.",
        "- **BAIXO** — so faz sentido como demo de competicao.",
        "",
        "## Risco tecnico",
        "",
        "Julgado sobre a arquitetura DESCRITA, pela rubrica de `framework-pilares.md`.",
        "Na duvida entre dois niveis, escolha o MAIOR (o inverso da regra das notas).",
        "",
        "- **ALTO** - multiagentes com scraping, escrita em sistema externo (ex.: orgao",
        "  publico), tempo real, ou ativo de dado ainda nao entregue.",
        "- **MEDIO** - um ou dois agentes, function calling de leitura, integracoes com",
        "  API estavel e documentada.",
        "- **BAIXO** - RAG simples ou fluxo fixo, sem integracao externa de escrita.",
        "",
        "A recompensa potencial NAO e insumo: e derivada das notas dos Pilares 1 e 4",
        "por `scorecard.recompensa_potencial()`. O cruzamento risco x recompensa sai da",
        "matriz `scorecard.MATRIZ_RISCO`.",
        "",
        "## Horizonte",
        "",
        "- **HACKATHON** — serve para a banca, mas nao se sustenta como negocio.",
        "- **PRODUTO** — nao ganha o edital (pouco brilho de agente), mas vira negocio real.",
        "- **HACKATHON_E_PRODUTO** — serve para os dois. Prioridade maxima.",
        "- **NENHUM** — nao serve para nenhum dos dois. Arquive e siga.",
        "",
        "O horizonte e ortogonal ao status: uma ideia REPROVADA no framework pode ter",
        "horizonte PRODUTO e continuar valiosa. E exatamente por isso que o banco guarda",
        "as reprovadas em vez de descarta-las.",
    ]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    if "--markdown" in sys.argv:
        sys.stdout.write(_markdown())
    else:
        for campo, valores in _CAMPOS.items():
            print(f"{campo}:")
            for v in valores:
                print(f"  - {v}")
