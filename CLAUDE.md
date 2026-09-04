# CLAUDE.md

Orientações para o Claude Code trabalhando **neste repositório**.

## O que é este repo

Não é uma aplicação: é a **skill `executioner-idea-validator`** mais o banco de ideias
que ela produz. O produto entregue são o `SKILL.md`, seus arquivos de apoio e os três
scripts Python. Visão geral para humanos: `README.md`.

```
.claude/skills/executioner-idea-validator/   # a skill (o produto deste repo)
output/                                      # o banco de ideias (100% gerado)
```

## Duas modalidades de trabalho

Antes de agir, identifique em qual delas o pedido cai.

**1. Usar a skill** — o usuário traz uma ideia para avaliar.
Invoque `executioner-idea-validator` e siga o `SKILL.md` à risca: gate de entrada,
pontuação com evidência citada, `scorecard.py`, resposta no template, cirurgia,
`registrar_ideia.py`. Não avalie "no olho" nem escreva o arquivo da ideia à mão.

**2. Evoluir a skill** — o usuário quer mudar o framework, os scripts ou os textos.
Aí valem as regras de manutenção abaixo.

## Regras de manutenção

### Fonte única de verdade

| Conceito | Vive em | Nunca duplique em |
|---|---|---|
| Pesos, arredondamento, faixas de veredicto | `scripts/scorecard.py` | nenhum outro `.py` |
| Enums de domínio / função TOGAF / horizonte | `scripts/taxonomia.py` | JSON, prompts, `.md` |
| Rubrica 1–5 de cada pilar | `references/framework-pilares.md` | `SKILL.md` |

`registrar_ideia.py` **importa** de `scorecard.py` e `taxonomia.py`. Se precisar de um
peso ou de uma faixa, importe — não recopie o número.

### Arquivos gerados — não edite à mão

- `references/taxonomia-negocio.md` → regenere:
  ```bash
  python3 scripts/taxonomia.py --markdown > references/taxonomia-negocio.md
  ```
- `output/**` inteiro (incluindo `INDEX.md` e `banco.json`) → só `registrar_ideia.py`
  escreve ali. Para consertar o índice: `registrar_ideia.py --reindex`.

### Determinismo é requisito, não preferência

Qualquer mudança nos scripts precisa preservar:

- média em `Decimal` com HALF_UP e 2 casas — **nunca** `float`, nunca conta feita pelo modelo;
- pasta de destino derivada da faixa da média já arredondada;
- nome do arquivo derivado do título pela regra de slug (NFKD → ASCII → minúsculas);
- ordenação do índice: média desc., depois `id` asc.;
- `criado_em` preservado entre reavaliações;
- mesmo JSON + mesmo `--datahora` ⇒ saída byte a byte idêntica.

Se uma alteração quebrar qualquer um destes pontos, ela está errada — reformule.

### Dependências

Só biblioteca padrão do Python (3.9+). **Não adicione dependências externas**: a skill
precisa rodar em qualquer máquina com Python, sem `pip install`.

### Estilo

Textos da skill em **português**, tom direto (é a persona do Executioner). Código e
mensagens de erro dos scripts em **ASCII sem acentos**, para não depender de locale do
terminal; o conteúdo gerado nos arquivos `.md` pode ter acentos normalmente.

Erro de validação deve dizer o que fazer, não só o que está errado. Compare:
`notas.defesa: esperado inteiro de 1 a 5 (recebido None). Pilar sem dados = veredicto
INSUFICIENTE: NAO registre no banco.`

## Como testar uma alteração

Use `--datahora` fixo e um diretório descartável — **nunca teste contra `output/`**,
o banco real do usuário.

```bash
SKILL=.claude/skills/executioner-idea-validator
TMP=$(mktemp -d)

# 1. cálculo
python3 $SKILL/scripts/scorecard.py --dor 4 --agente 5 --defesa 3 --escala 4

# 2. registro
python3 $SKILL/scripts/registrar_ideia.py --json $SKILL/assets/ideia.exemplo.json \
  --output-dir $TMP --datahora "2026-01-01T00:00:00-03:00"

# 3. idempotência: rodar de novo tem de dar o MESMO md5
md5sum $TMP/ideias-aprovadas/reentrega-zero.md
python3 $SKILL/scripts/registrar_ideia.py --json $SKILL/assets/ideia.exemplo.json \
  --output-dir $TMP --datahora "2026-01-01T00:00:00-03:00" >/dev/null
md5sum $TMP/ideias-aprovadas/reentrega-zero.md

# 4. transição de faixa: baixe as notas e confirme que o arquivo MUDA de pasta,
#    preservando criado_em e acumulando o historico

# 5. validação: enum inválido e nota fora de 1–5 devem sair com exit 2
```

Ao mexer em `scorecard.py`, confira as três faixas (≥4.00, 3.50–3.99, <3.50) e as
fronteiras exatas.

## Ao alterar a skill, mantenha em sincronia

Uma mudança de comportamento quase sempre toca mais de um arquivo:

- mudou pesos/faixas → `scorecard.py`, `references/framework-pilares.md`,
  `assets/template-analise.md`, seções do `README.md`;
- mudou campos do JSON → `registrar_ideia.py`, `assets/ideia.exemplo.json`,
  `references/banco-de-ideias.md`;
- mudou seções do arquivo de ideia → `render()`, `references/banco-de-ideias.md`, `README.md`;
- mudou o gatilho de acionamento → a `description` do frontmatter do `SKILL.md`.

O frontmatter do `SKILL.md` (`name` + `description`) é o que decide se a skill é
acionada. Mantenha a `description` em terceira pessoa e carregada de gatilhos concretos.

## Git

- Remote: `https://github.com/fabiopborges/hackathons-executioner-idea-validator.git` (branch `main`).
- **`output/` está no `.gitignore`.** O repositório publica a ferramenta, não as ideias
  avaliadas — arquivos de ideia citam cliente, parceiro e LOI. Nunca use `git add -f`
  para forçar um arquivo do banco para dentro do repositório: `.gitignore` não
  desversiona o que já foi rastreado, e o conteúdo ficaria no histórico público.
- Também ignorados: `.venv/`, `__pycache__/`, `*.pyc`, `.claude/settings.local.json`.
- Ao abrir PR, o fluxo `.github/workflows/cla-check.yml` exige as três caixas de aceite
  do CLA marcadas no corpo do PR (palavras-chave: *autoria*, *MIT*, *credencial*). Se
  mexer no texto do `pull_request_template.md`, preserve essas palavras nas três linhas
  ou o check quebra.

## Limites

- `SKILL.md` é o que fica sempre em contexto: mantenha-o enxuto (~100 linhas) e empurre
  detalhe para `references/`, lido sob demanda.
- Não registre ideia com pilar `INSUFICIENTE` nem ideia barrada no gate de entrada.
- Não invente dado que o usuário não forneceu para "completar" uma avaliação — a regra
  número 2 da skill vale também para você ao operá-la.
