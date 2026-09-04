# Banco de ideias — contrato de persistência

Toda ideia avaliada vira um arquivo. **Nada se perde**: uma ideia reprovada para o
edital pode ser exatamente o produto real que sobrevive ao hackathon, e o banco existe
para que essa distinção fique registrada em vez de morrer na conversa.

## Layout

```
output/
├── INDEX.md                    # gerado: índice por status + quadro comparativo + radar
├── banco.json                  # gerado: mesmo conteúdo, legível por máquina
├── ideias-aprovadas/           # média ponderada ≥ 4.00
├── ideias-em-observacao/       # 3.50 – 3.99 (a um gargalo da aprovação)
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
| Categoria/Decisão do quadro | derivadas do status (🟢 Avançar / 🟡 Observar / 🔴 Arquivar) |
| Nome do arquivo | slug do título: NFKD → ASCII → minúsculas → `[^a-z0-9]+` vira `-` → 60 chars |
| Pasta | faixa da média **já arredondada**, conforme `framework-pilares.md` |
| Média | `Decimal`, HALF_UP, 2 casas — sem float, sem aritmética do modelo |
| Seções | ordem fixa no template; nenhuma é opcional |
| Taxonomia | enums de `scripts/taxonomia.py`; valor fora da lista é erro, não improviso |
| Índice | ordenado por média desc., depois por slug asc. |
| `criado_em` | preservado entre reavaliações; só `atualizado_em` muda |
| Tags | normalizadas para minúsculas e ordenadas |

Mesmo JSON + mesmo `--datahora` ⇒ arquivo byte a byte idêntico.

## Cabeçalho informativo de cada ideia

Título · Data/hora do registro · Última avaliação · Domínio de negócio ·
Função de negócio (TOGAF) · Status (com a média) · Horizonte ·
Potencial de produto real · Risco vs recompensa (com o veredito da matriz) ·
Decisão (🟢 Avançar / 🟡 Observar / 🔴 Arquivar) · Death knell (condição + prazo) · Tags.

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

# reprodutibilidade em teste
... registrar_ideia.py --json ideia.json --datahora "2026-09-04T00:30:00-03:00"
```

O JSON é montado a partir da avaliação; o modelo em `assets/ideia.exemplo.json` traz
todos os campos preenchidos.

### Campos do JSON

| Campo | Tipo | Obrigatório |
|---|---|---|
| `titulo` | string | sim |
| `dominio_negocio` | enum (taxonomia) | sim |
| `funcao_negocio` | lista de 1–3 enums TOGAF, da mais central para a menos | sim |
| `escopo_proposta`, `problema`, `quem_sofre` | string | sim |
| `arquitetura_agentes`, `fontes_dados`, `gargalo` | string | sim |
| `notas` | `{dor, agente, defesa, escala}`, inteiros 1–5 | sim |
| `justificativas` | uma frase por pilar | sim |
| `horizonte`, `potencial_produto_real` | enum (taxonomia) | sim |
| `risco_tecnico` | enum `ALTO`/`MEDIO`/`BAIXO` (taxonomia) | sim |
| `pai` | string — a única ação das próximas 48h | sim |
| `death_knell` | `{condicao, prazo}` com prazo `YYYY-MM-DD` (máx. 7 dias) | sim |
| `justificativa_horizonte` | string | recomendado |
| `justificativa_risco_tecnico` | string | recomendado |
| `riscos`, `proximos_passos` | listas não vazias | sim |
| `tags` | lista de strings | não |
| `observacao_revisao` | string, entra no histórico | não |

## Quando NÃO registrar

- Qualquer pilar `INSUFICIENTE`. Sem as 4 notas não há registro — cobre o dado e pare.
- Ideia barrada no gate de entrada (descrição com menos de 3 linhas).
- Rascunho que o usuário ainda está reformulando na mesma conversa: registre a versão
  final, não cada iteração.
