# Executioner — Validador e Banco de Ideias

Uma **Claude Code Skill** que avalia ideias de projetos de IA com rigor de banca de
hackathon, dá uma nota defensável e guarda cada ideia avaliada num banco organizado em
disco — inclusive as reprovadas.

> **Por que guardar as reprovadas?** Porque uma ideia que não ganha um hackathon pode ser
> um produto real excelente. O critério de um edital (brilho técnico do agente, escala
> nacional, prazo de semanas) não é o mesmo critério de um negócio. O Executioner separa
> as duas coisas explicitamente e registra as duas.

---

## Sumário

- [Para quem é](#para-quem-é)
- [O que a skill faz (escopo)](#o-que-a-skill-faz-escopo)
- [O que a skill NÃO faz](#o-que-a-skill-não-faz)
- [Instalação](#instalação)
- [Primeiros passos](#primeiros-passos)
- [Exemplos de uso](#exemplos-de-uso)
- [O Framework de 4 Pilares](#o-framework-de-4-pilares)
- [O banco de ideias](#o-banco-de-ideias)
- [Uso avançado: os scripts](#uso-avançado-os-scripts)
- [Personalizando](#personalizando)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Perguntas frequentes](#perguntas-frequentes)

---

## Para quem é

- Quem vai competir em **hackathon ou edital de agentes de IA** e precisa decidir qual
  das 10 ideias na cabeça merece as próximas semanas de trabalho.
- Quem tem **muitas ideias e pouca memória organizada** — o banco vira o histórico.
- Times que querem um **critério comum** em vez de discutir ideia por gosto pessoal.

Não é preciso saber programar. Você conversa em português; a skill faz o resto.

---

## O que a skill faz (escopo)

1. **Barra ideias mal descritas.** Se você mandar "um agente de IA para RH", ela não
   avalia: exige problema, quem sofre, como o agente resolve e a fonte dos dados.
2. **Pontua em 4 pilares** (1 a 5 cada): Dor Real, Centralidade do Agente,
   Defensibilidade e Escala Nacional — com pesos fixos e justificativa obrigatória
   por nota.
3. **Calcula a média ponderada por script**, não "de cabeça". Mesma entrada, mesma nota,
   sempre.
4. **Dá um veredicto sem rodeios**: APROVADA, EM OBSERVAÇÃO ou REPROVADA.
5. **Aponta uma cirurgia**: o gargalo único que, resolvido, mais sobe a nota.
6. **Classifica o negócio**: domínio (setor) e função de negócio segundo a Business
   Architecture do **TOGAF**.
7. **Registra a ideia em `output/`**, na pasta correspondente ao veredicto, com histórico
   de reavaliações e um índice regenerado automaticamente.
8. **Marca o horizonte**: se a ideia serve para o hackathon, para produto real, para os
   dois ou para nenhum.

### A persona

O Executioner é deliberadamente **duro**. Ele não elogia para agradar, não inventa dados
que você não deu e não arredonda nota para cima. Se a sua ideia é fraca, ele diz
"DESCARTE" e explica por quê. Isso é intencional: uma banca de hackathon vai ser pior.

---

## O que a skill NÃO faz

- **Não pesquisa mercado por você.** Ela avalia o que você contou. Se você não fez
  entrevista com cliente, o Pilar 1 vai ser baixo — e é para ser.
- **Não inventa números.** Sem dado sobre um pilar, o veredicto é `INSUFICIENTE` e nada
  é registrado no banco.
- **Não escreve o pitch nem o código do projeto.** O escopo termina na decisão de seguir
  ou matar a ideia.
- **Não substitui validação com cliente real.** Nota 5 no Pilar 1 exige que você já
  tenha conversado com gente de verdade.

---

## Instalação

**Pré-requisitos:** [Claude Code](https://claude.com/claude-code) e Python 3.9+
(só a biblioteca padrão — nada para instalar via `pip`).

### Opção A — usar neste repositório

```bash
cd hackathons-executioner-idea-validator
claude
```

A skill já está em `.claude/skills/executioner-idea-validator/` e é detectada sozinha.

### Opção B — levar para outro projeto

```bash
cp -r .claude/skills/executioner-idea-validator /caminho/do/seu/projeto/.claude/skills/
```

### Opção C — disponível em todos os seus projetos

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/executioner-idea-validator ~/.claude/skills/
```

### Conferindo se instalou

Dentro do `claude`, digite `/` e procure por `executioner-idea-validator` na lista.

---

## Primeiros passos

Abra o Claude Code na pasta do projeto e **simplesmente descreva sua ideia**. A skill é
acionada sozinha quando você pede para validar, criticar, dar nota ou comparar ideias.

Para forçar o uso, digite:

```
/executioner-idea-validator
```

Uma boa descrição responde às 4 perguntas obrigatórias:

| # | Pergunta | Exemplo de resposta |
|---|---|---|
| 1 | Qual o problema? | "Transportadoras perdem R$ 18k–40k/mês com reentregas" |
| 2 | Quem sofre? | "Gestor de operações da transportadora" |
| 3 | Como um agente de IA resolve? | "3 agentes: rastreia, prevê risco, negocia por WhatsApp" |
| 4 | Qual a fonte dos dados? | "Histórico do WMS das transportadoras parceiras" |

Se faltar alguma, a skill devolve a exigência e para. Não é frescura: sem esses quatro
elementos não há o que avaliar.

---

## Exemplos de uso

### Exemplo 1 — Avaliar uma ideia

**Você digita:**

> Quero validar esta ideia. Transportadoras regionais perdem entre R$ 18 mil e R$ 40 mil
> por mês com reentregas — falei com 4 donos de transportadora em MG e SP e uma delas
> assinou uma carta de intenção para piloto. A solução é um sistema com três agentes: um
> lê o histórico de tentativas no WMS da transportadora, outro classifica o risco de
> recusa da entrega, e um terceiro conversa com o destinatário no WhatsApp e decide
> sozinho se reagenda, redireciona para um ponto de retirada ou devolve. Os dados de
> tentativa de entrega vêm do WMS proprietário das parceiras; CEP e malha viária vêm de
> base pública.

**O que acontece:**

1. A descrição passa no gate (tem os 4 elementos).
2. A skill pontua cada pilar citando a sua própria evidência.
3. Roda `scorecard.py` → média **4.45**.
4. Mostra a análise formatada na conversa, com o veredicto **APROVADA** e a cirurgia.
5. Registra em `output/ideias-aprovadas/reentrega-zero.md` e atualiza o índice.
6. Informa o caminho do arquivo.

**Resposta resumida:**

```
🔍 ANÁLISE DA IDEIA: Reentrega Zero
📊 SCORECARD (média ponderada): 4.45 / 5.0

- Pilar 1 (Dor) — peso 0.30: 5/5. 4 entrevistas, perda mensal quantificada e LOI assinada.
- Pilar 2 (Agente) — peso 0.30: 5/5. Três papéis distintos, decisão autônoma entre três desfechos.
- Pilar 3 (Defesa) — peso 0.25: 4/5. Histórico do WMS é dataset privado real.
- Pilar 4 (Escala) — peso 0.15: 3/5. Dor nacional, mas sem plano de distribuição.

⚖️ VEREDICTO FINAL: [APROVADA] — vamos para o backlog.

🔪 CIRURGIA: o teto está no Pilar 4. Negocie listagem no marketplace de integrações de
um WMS líder — cada cliente do WMS vira lead sem CAC direto. Escala vai de 3 para 5.

🎯 HORIZONTE: HACKATHON_E_PRODUTO · Potencial de produto real: ALTO.
📁 REGISTRADO EM: output/ideias-aprovadas/reentrega-zero.md
```

### Exemplo 2 — Uma ideia fraca sendo executada

**Você digita:**

> Um chatbot que responde dúvidas de pequenos empresários sobre impostos, usando RAG em
> cima da legislação pública da Receita Federal. Todo empreendedor sofre com isso.

**Resposta resumida:**

```
📊 SCORECARD (média ponderada): 2.30 / 5.0

- Pilar 1 (Dor): 2/5. "Todo empreendedor sofre" é dor genérica. Zero entrevista.
- Pilar 2 (Agente): 2/5. RAG de FAQ sobre PDF. Um índice de busca resolve igual.
- Pilar 3 (Defesa): 2/5. Legislação pública, reproduzível em um fim de semana.
- Pilar 4 (Escala): 4/5. Tributação é nacional — único ponto que se sustenta.

⚖️ VEREDICTO: [REPROVADA] — Motivo principal: ausência total de fosso.

🔪 CIRURGIA: troque a legislação pública pelo motor de decisão — mapeie as 50+ variáveis
de substituição tributária estadual e ponha um agente Validador criticando o Executor.

🎯 HORIZONTE: PRODUTO · Potencial: MEDIO. Não ganha o edital, mas compliance tributário
para MEI continua sendo mercado depois do hackathon.
📁 REGISTRADO EM: output/ideias-reprovadas/contador-bot-duvidas-tributarias.md
```

Repare: **reprovada, mas registrada** — e ela aparece no "Radar de produto real" do índice.

### Exemplo 3 — Descrição insuficiente

**Você digita:**

> Tenho uma ideia de agente multiagente para RH, o que acha?

**Resposta:**

```
Descrição insuficiente. Preciso saber: (1) Qual o problema, (2) Quem sofre,
(3) Como um agente de IA resolveria isso, (4) Qual a fonte dos dados.
```

Nada é avaliado e nada é registrado.

### Exemplo 4 — Comparar várias ideias

**Você digita:**

> Tenho 3 ideias para o hackathon, avalie todas e me diga qual seguir: [descrição 1...]
> [descrição 2...] [descrição 3...]

Cada ideia recebe a análise completa e vai para o banco. No fim, um ranking por média e
uma recomendação: qual seguir e quais matar hoje. As notas **não são distribuídas na
curva** — se as três forem ruins, as três são reprovadas.

### Exemplo 5 — Reavaliar depois que algo mudou

**Você digita:**

> Reavalie a Reentrega Zero: a LOI não se confirmou, o cliente desistiu do piloto.

A skill recalcula, o arquivo **muda de pasta** (de `ideias-aprovadas/` para
`ideias-em-observacao/`), o `criado_em` original é preservado e uma nova linha entra no
histórico de avaliações com o motivo.

### Exemplo 6 — Consultar o banco

**Você digita:**

> Quais ideias do banco valem como produto real, mesmo as reprovadas?

A skill lê `output/INDEX.md` / `output/banco.json` e responde a partir da seção
"Radar de produto real". Outras perguntas que funcionam:

- "Liste as ideias aprovadas por média."
- "Quais ideias do domínio Logística já avaliei?"
- "Qual o gargalo em comum das minhas ideias reprovadas?"

---

## O Framework de 4 Pilares

| Pilar | O que mede | Peso |
|---|---|---|
| 1. Dor Real e Validação | Você falou com cliente de verdade? A perda é mensurável? | 0.30 |
| 2. Centralidade do Agente | É agente com autonomia ou um chatbot disfarçado? | 0.30 |
| 3. Defensibilidade | Você tem dado ou conhecimento que os outros não têm? | 0.25 |
| 4. Escala Nacional | Funciona em qualquer UF e tem modelo de negócio? | 0.15 |

**Média ponderada = 0.30·P1 + 0.30·P2 + 0.25·P3 + 0.15·P4**

| Média | Veredicto | Pasta |
|---|---|---|
| ≥ 4.00 | **APROVADA** | `output/ideias-aprovadas/` |
| 3.50 – 3.99 | **EM OBSERVAÇÃO** — a um gargalo da aprovação | `output/ideias-em-observacao/` |
| < 3.50 | **REPROVADA** | `output/ideias-reprovadas/` |

Regras de calibração: na dúvida entre duas notas, vale a **menor**. E há um teste
decisivo no Pilar 2 — se você tirar o agente e um CRUD com regra fixa resolver o mesmo
problema, a nota é **no máximo 2**.

A rubrica completa, nota por nota, está em
[`references/framework-pilares.md`](.claude/skills/executioner-idea-validator/references/framework-pilares.md).

---

## O banco de ideias

```
output/
├── INDEX.md                    # índice legível: por status + radar de produto real
├── banco.json                  # o mesmo, legível por máquina
├── ideias-aprovadas/
├── ideias-em-observacao/
└── ideias-reprovadas/
```

Cada ideia é **um arquivo Markdown** nomeado pelo título (`reentrega-zero.md`). Ao ser
reavaliada, ela é **movida** entre pastas — nunca duplicada.

### O que tem dentro de cada arquivo

**Cabeçalho:** título · data/hora do registro · última avaliação · domínio de negócio ·
função de negócio (TOGAF) · status com a média · horizonte · potencial de produto real ·
tags.

**Seções:** Escopo da proposta · Problema e quem sofre · Arquitetura de agentes ·
Fontes de dados e defensibilidade · Scorecard · Veredicto · Cirurgia (gargalo único) ·
Potencial fora do hackathon · Riscos e premissas · Próximos passos · Histórico de
avaliações.

### Horizonte: o campo que separa hackathon de negócio

`horizonte` é **independente** do veredicto:

| Valor | Significado |
|---|---|
| `HACKATHON` | Brilha na banca, não se sustenta como negócio |
| `PRODUTO` | Não ganha o edital, mas vira negócio real |
| `HACKATHON_E_PRODUTO` | Serve para os dois. Prioridade máxima |
| `NENHUM` | Não serve para nada. Arquive e siga |

Uma ideia **REPROVADA com horizonte `PRODUTO` é um achado, não uma contradição** — e é
por isso que o banco guarda as reprovadas.

### Regra de ouro

> **Nunca edite arquivos de `output/` à mão.** Eles são gerados. Peça a reavaliação ao
> Executioner; ele regrava tudo e mantém índice e histórico coerentes.

---

## Uso avançado: os scripts

Você não precisa deles no dia a dia — a skill os chama. Mas eles funcionam sozinhos.

```bash
SKILL=.claude/skills/executioner-idea-validator
```

### Calcular uma nota

```bash
python3 $SKILL/scripts/scorecard.py --dor 4 --agente 5 --defesa 3 --escala 4
```

```
CONTA: 0.30x4 + 0.30x5 + 0.25x3 + 0.15x4 = 4.05
MEDIA PONDERADA: 4.05 / 5.00
VEREDICTO: [APROVADA] - vai para o backlog.
DESTINO NO BANCO: output/ideias-aprovadas/
```

Pilar sem dados:

```bash
python3 $SKILL/scripts/scorecard.py --dor 4 --agente 5 --pilar-insuficiente defesa --escala 4
```

### Registrar uma ideia

```bash
python3 $SKILL/scripts/registrar_ideia.py --json minha-ideia.json
python3 $SKILL/scripts/registrar_ideia.py --json minha-ideia.json --dry-run   # simula
python3 $SKILL/scripts/registrar_ideia.py --reindex                            # refaz o índice
```

Modelo de JSON pronto e comentado:
[`assets/ideia.exemplo.json`](.claude/skills/executioner-idea-validator/assets/ideia.exemplo.json).
Contrato dos campos:
[`references/banco-de-ideias.md`](.claude/skills/executioner-idea-validator/references/banco-de-ideias.md).

### Ver a taxonomia de negócio

```bash
python3 $SKILL/scripts/taxonomia.py
```

### Por que scripts em vez de deixar o modelo fazer?

Porque **determinismo**. A média, a pasta de destino, o nome do arquivo e a ordem do
índice não podem variar com a redação do prompt ou o humor do modelo. Garantias:

- média em `Decimal` com arredondamento HALF_UP, 2 casas — sem float, sem conta de cabeça;
- pasta derivada da faixa da média já arredondada;
- nome do arquivo derivado do título por regra fixa de slug;
- domínio e função validados contra enums — valor fora da lista é **erro**, não improviso;
- `criado_em` preservado entre reavaliações;
- mesmo JSON + mesmo `--datahora` ⇒ arquivo **byte a byte idêntico**.

---

## Personalizando

| Quero mudar... | Edite |
|---|---|
| Os pesos dos pilares ou as faixas de veredicto | `scripts/scorecard.py` (`PESOS`, `classificar`) |
| A rubrica de cada nota | `references/framework-pilares.md` |
| Os setores ou funções TOGAF disponíveis | `scripts/taxonomia.py`, depois regenere o `.md` |
| O formato da resposta na conversa | `assets/template-analise.md` |
| As seções do arquivo de cada ideia | `render()` em `scripts/registrar_ideia.py` |
| O tom / as regras do Executioner | `SKILL.md` |

Depois de mexer em `scripts/taxonomia.py`:

```bash
python3 $SKILL/scripts/taxonomia.py --markdown > $SKILL/references/taxonomia-negocio.md
```

Os pesos vivem em **um lugar só** (`scorecard.py`) e são importados pelo registrador —
mudar lá muda em todo lugar.

---

## Estrutura do repositório

```
.
├── README.md
├── CLAUDE.md                              # instruções para o Claude Code neste repo
├── CONTRIBUTING.md                        # fluxo de contribuição + CLA
├── LICENSE.md                             # MIT
├── .gitignore                             # ignora output/, .venv/, __pycache__/
├── .github/
│   ├── pull_request_template.md
│   └── workflows/cla-check.yml            # verifica o aceite do CLA no PR
├── output/                                # o banco de ideias (gerado, NÃO versionado)
└── .claude/skills/executioner-idea-validator/
    ├── SKILL.md                           # persona, regras e workflow
    ├── references/
    │   ├── framework-pilares.md           # rubrica 1–5, pesos, faixas
    │   ├── banco-de-ideias.md             # layout, contrato do JSON, determinismo
    │   ├── taxonomia-negocio.md           # GERADO por taxonomia.py
    │   └── exemplos.md                    # análises-modelo de calibração
    ├── assets/
    │   ├── template-analise.md            # formato da resposta na conversa
    │   └── ideia.exemplo.json             # payload completo de registro
    └── scripts/
        ├── scorecard.py                   # fonte única: pesos, arredondamento, faixas
        ├── taxonomia.py                   # vocabulário controlado (enums)
        └── registrar_ideia.py             # escreve o banco e o índice
```

Os arquivos em `references/` e `assets/` **não** são carregados junto com o `SKILL.md`:
o Claude os lê sob demanda (*progressive disclosure*), o que mantém o custo de contexto
baixo quando a skill está apenas disponível e não em uso.

---

## Perguntas frequentes

**A skill não foi acionada, e agora?**
Digite `/executioner-idea-validator` para forçar. Se não aparecer na lista, confira se a
pasta está em `.claude/skills/` (do projeto) ou `~/.claude/skills/` (global) e se o
arquivo se chama exatamente `SKILL.md`.

**Preciso instalar alguma biblioteca Python?**
Não. Os scripts usam só a biblioteca padrão. O `.venv/` do repositório é opcional.

**Posso versionar o `output/` no Git?**
Neste repositório ele está no `.gitignore` de propósito: o que se publica é a
**ferramenta**, não as ideias avaliadas com ela — arquivos de ideia costumam citar
cliente, parceiro ou LOI. Se você quiser versionar o seu banco, faça isso num
repositório **privado** e separado, ou remova a linha `output/` do `.gitignore` sabendo
o que está publicando.

**Achei a avaliação injusta / dura demais.**
É por design. Mas se a nota se baseou em algo que você não disse, aponte: *"você marcou
Pilar 1 como 2, mas eu falei que já tenho 5 entrevistas"* — e peça a reavaliação. O que
a skill não faz é subir a nota sem evidência nova.

**Duas ideias com o mesmo título?**
O nome do arquivo vem do título — a segunda sobrescreve a primeira. Use títulos
distintos.

**Como apago uma ideia do banco?**
Apague o arquivo `.md` e rode `registrar_ideia.py --reindex`.

**Serve para ideias que não são de IA?**
O Pilar 2 mede a centralidade do agente, então uma ideia sem IA sempre perderá 30% da
nota. Para avaliar produtos em geral, ajuste os pesos em `scripts/scorecard.py`.

---

## Licença e contribuição

Distribuído sob a **Licença MIT** — veja [`LICENSE.md`](LICENSE.md). Uso livre, inclusive
comercial, mantendo o aviso de copyright.

Contribuições são bem-vindas: leia [`CONTRIBUTING.md`](CONTRIBUTING.md) antes de abrir o
primeiro Pull Request. Ele traz o fluxo de trabalho, as restrições de desenho (determinismo,
fonte única de verdade, zero dependências externas), a bateria de verificação e o Acordo de
Licença de Contribuição (CLA).

Repositório: <https://github.com/fabiopborges/hackathons-executioner-idea-validator>
