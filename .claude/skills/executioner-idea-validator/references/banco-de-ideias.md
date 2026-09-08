# Banco de ideias — contrato de persistência

Toda ideia avaliada vira um arquivo. **Nada se perde**: uma ideia reprovada para o
edital pode ser exatamente o produto real que sobrevive ao hackathon, e o banco existe
para que essa distinção fique registrada em vez de morrer na conversa.

## Layout

```
output/
├── INDEX.md                    # gerado: índice por status + quadro comparativo + radar
├── banco.json                  # gerado: mesmo conteúdo, legível por máquina
├── ideias-aprovadas/           # média ponderada ≥ 4.00 e demonstrável em 3 min
├── ideias-em-observacao/       # 3.50 – 3.99 (a um gargalo da aprovação)
├── ideias-nao-demonstraveis/   # ≥ 4.00, mas não demonstrável em 3 min offline
└── ideias-reprovadas/          # < 3.50
```

Um arquivo por ideia: `<slug-do-titulo>.md`. A ideia **muda de pasta** quando é
reavaliada e troca de faixa — o arquivo é movido, não duplicado, e o histórico de
avaliações vai junto.

## Garantias de determinismo

Só `registrar_ideia.py` escreve no banco. Nunca crie ou edite arquivos de `output/` à
mão — isso quebra o índice e o histórico.

| Elemento | Regra determinística |
|---|---|
| Recompensa e veredito da matriz | derivados por `scorecard.py` das notas e do risco — nunca julgados duas vezes |
| Categoria/Decisão do quadro | derivadas do status (🟢 Avançar / 🟡 Observar / 🟠 Resolver Demo / 🔴 Arquivar) |
| Nome do arquivo | slug do título: NFKD → ASCII → minúsculas → `[^a-z0-9]+` vira `-` → 60 chars |
| Pasta | faixa da média **já arredondada**, conforme `framework-pilares.md` |
| Média | `Decimal`, HALF_UP, 2 casas — sem float, sem aritmética do modelo |
| Seções | ordem fixa no template; nenhuma é opcional |
| Taxonomia | enums de `scripts/taxonomia.py`; valor fora da lista é erro, não improviso |
| Índice | ordenado por média desc., depois por slug asc. |
| `criado_em` | preservado entre reavaliações; só `atualizado_em` muda |
| Tags | normalizadas para minúsculas e ordenadas; só `[a-z0-9-]`, até 30 chars |
| Sanitização | idempotente sobre todo texto: controle/invisíveis removidos, escalares em linha única, `#`/`---`/`\|` no início de linha de bloco neutralizados, células e links escapados |
| Colisão de slug | títulos diferentes com o mesmo slug → erro; o arquivo existente não é tocado |
| Índice tolerante | arquivo com frontmatter inválido é pulado com `AVISO` em stderr, nunca derruba o `--reindex` |

Mesmo JSON + mesmo `--datahora` ⇒ arquivo byte a byte idêntico.

## Cabeçalho informativo de cada ideia

Título · Data/hora do registro · Última avaliação · Domínio de negócio ·
Função de negócio (TOGAF) · Status (com a média) · Horizonte ·
Potencial de produto real · Risco vs recompensa (com o veredito da matriz) ·
Demonstrável em 3 min (SIM/NAO) ·
Decisão (🟢 Avançar / 🟡 Observar / 🟠 Resolver Demo / 🔴 Arquivar) ·
Death knell (condição + prazo) · Tags.

## Seções do corpo

1. **Escopo da proposta** — o que entra e o que fica de fora do MVP.
2. **Problema e quem sofre** — dor e persona que paga a conta.
3. **Arquitetura de agentes** — papéis, autonomia e ferramentas; é a evidência do Pilar 2.
4. **Fontes de dados e defensibilidade** — o que é proprietário e o que é público; Pilar 3.
5. **Scorecard** — nota, peso e justificativa por pilar, com a média.
6. **Veredicto** — status e a conta explícita.
7. **Matriz risco vs recompensa** — recompensa derivada das notas, risco técnico
   julgado pela rubrica, veredito determinístico da matriz.
8. **Cirurgia — gargalo único** — a alavanca que mais move a nota. Obrigatória sempre,
   inclusive em ideia aprovada (aí é o teto a atacar).
9. **Plano de ação imediato (48h)** — a única tarefa das próximas 48 horas.
10. **Death knell** — condição objetiva + prazo (máx. 7 dias) que enterra a ideia.
11. **Potencial fora do hackathon** — horizonte e potencial de produto real. É a seção que
   justifica manter reprovadas no banco.
12. **Riscos e premissas** — o que derruba a ideia se der errado.
13. **Próximos passos** — ações concretas, ordenadas.
14. **Histórico de avaliações** — data, média, status e observação de cada rodada.

## Uso

```bash
# registrar/atualizar (a partir do JSON da avaliação)
python3 .claude/skills/executioner-idea-validator/scripts/registrar_ideia.py --json ideia.json

# conferir o destino sem gravar
... registrar_ideia.py --json ideia.json --dry-run

# reconstruir INDEX.md e banco.json
... registrar_ideia.py --reindex

# reprodutibilidade em teste (flags de teste exigem EXECUTIONER_TEST=1)
EXECUTIONER_TEST=1 ... registrar_ideia.py --json ideia.json --output-dir /tmp/x \
  --datahora "2026-09-05T00:00:00-03:00"
```

`--output-dir` fora do diretório atual e `--datahora` só funcionam com
`EXECUTIONER_TEST=1`; `.claude/` e `.git/` nunca são destino. Texto com padrão de
injeção de prompt bloqueia o registro (exit 2) — veja `seguranca-prompt.md`.

O JSON é montado a partir da avaliação; o modelo em `assets/ideia.exemplo.json` traz
todos os campos preenchidos.

### Campos do JSON

| Campo | Tipo | Obrigatório | Limite |
|---|---|---|---|
| `titulo` | string, linha única | sim | 120 chars |
| `dominio_negocio` | enum (taxonomia) | sim | — |
| `funcao_negocio` | lista de 1–3 enums TOGAF, da mais central para a menos | sim | 3 |
| `escopo_proposta`, `problema`, `quem_sofre` | string (bloco) | sim | 4000 chars |
| `arquitetura_agentes`, `fontes_dados`, `gargalo` | string (bloco) | sim | 4000 chars |
| `notas` | `{dor, agente, defesa, escala}`, inteiros 1–5 | sim | — |
| `justificativas` | uma frase por pilar | sim | 500 chars cada |
| `horizonte`, `potencial_produto_real` | enum (taxonomia) | sim | — |
| `risco_tecnico` | enum `ALTO`/`MEDIO`/`BAIXO` (taxonomia) | sim | — |
| `demoavel` | enum `SIM`/`NAO` (taxonomia) — demonstrável em 3 min offline? | sim | — |
| `pai` | string (bloco) — a única ação das próximas 48h | sim | 4000 chars |
| `death_knell` | `{condicao, prazo}`; prazo `YYYY-MM-DD` real, de 0 a 7 dias após a avaliação | sim | condição 500 chars |
| `justificativa_horizonte` | string (bloco) | recomendado | 4000 chars |
| `justificativa_risco_tecnico` | string (bloco) | recomendado | 4000 chars |
| `riscos`, `proximos_passos` | listas não vazias de linhas únicas | sim | 10 itens, 500 chars cada |
| `tags` | lista de `[a-z0-9-]` | não | 10 tags, 30 chars cada |
| `observacao_revisao` | string, entra no histórico | não | 500 chars |

## Quando NÃO registrar

- Qualquer pilar `INSUFICIENTE`. Sem as 4 notas não há registro — cobre o dado e pare.
- Ideia barrada no gate de entrada (descrição com menos de 3 linhas).
- Rascunho que o usuário ainda está reformulando na mesma conversa: registre a versão
  final, não cada iteração.
