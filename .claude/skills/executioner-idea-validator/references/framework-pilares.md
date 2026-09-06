# Framework Executioner — 4 Pilares

Régua de 1 a 5 por pilar. Seja rigoroso: a nota é o **piso** da evidência apresentada,
não o teto do potencial imaginado. Empate entre duas notas → fica a menor.

## Pesos

| Pilar | Dimensão | Peso |
|---|---|---|
| 1 | Dor Real e Validação | 0.30 (altíssimo) |
| 2 | Centralidade e Complexidade do Agente | 0.30 (altíssimo) |
| 3 | Defensibilidade (ativo próprio / dados) | 0.25 (médio-alto) |
| 4 | Escala Nacional e Potencial de Mercado | 0.15 (médio) |

Média ponderada = `0.30·P1 + 0.30·P2 + 0.25·P3 + 0.15·P4`.

Se um pilar for `INSUFICIENTE`, **não** há média: o veredicto é `INSUFICIENTE` e a
resposta cobra o dado que falta. Nunca renormalize pesos para "salvar" a nota.

## Pilar 1 — Dor Real e Validação

| Nota | Critério |
|---|---|
| 1–2 | Dor genérica ("pequenos empresários precisam de ajuda"), sem nenhuma evidência. |
| 3 | Há artigos ou senso comum, mas ZERO entrevistas com usuários reais. |
| 4 | Pelo menos 3 conversas ou prints com potenciais clientes reclamando; a perda financeira mensal do cliente é mensurável. |
| 5 | B2B com ticket médio mapeado + carta de intenção (LOI) ou piloto confirmado com empresa real. |

## Pilar 2 — Centralidade e Complexidade do Agente

| Nota | Critério |
|---|---|
| 1–2 | Chatbot de FAQ com RAG simples (buscar texto em PDF e devolver). Zero autonomia. |
| 3 | Um único agente com 1 function calling (ex.: consultar API de clima). |
| 4 | Orquestração de 2 agentes em série (triagem → análise) com estado compartilhado. |
| 5 | Multiagentes com papéis distintos (Pesquisador, Validador, Executor), loops de reflexão/crítica interna e decisão autônoma sobre qual ferramenta chamar. |

Teste decisivo: **se o agente for removido e um CRUD com regra fixa resolver o mesmo
problema, a nota é no máximo 2.**

## Pilar 3 — Defensibilidade (ativo próprio / dados)

| Nota | Critério |
|---|---|
| 1–2 | Só dados públicos (IBGE, Wikipedia, dados abertos do governo). |
| 3 | API pública paga (OpenAI, Google Maps) que qualquer um assina. |
| 4 | Dataset privado estruturado (ex.: histórico de manutenção de uma fábrica parceira) ou integração com sistema proprietário via API fechada. |
| 5 | Conhecimento de domínio tão específico (ex.: 50+ variáveis de cálculo tributário estadual) que um engenheiro comum levaria 6 meses para entender a lógica — fosso natural. |

## Pilar 4 — Escala Nacional e Potencial de Mercado

| Nota | Critério |
|---|---|
| 1–2 | Resolve problema de um único bairro ou município. |
| 3 | Problema nacional, mas sem plano de distribuição / go-to-market. |
| 4 | Problema claramente nacional (logística de entregas, inadimplência bancária) e a solução usa dados abertos nacionais para provar que funciona em qualquer UF. |
| 5 | Agnóstica de região, com modelo de negócio (BMC) prevendo receita recorrente (SaaS) e CAC baixo. |

## Faixas de veredicto

| Média ponderada | Veredicto |
|---|---|
| ≥ 4.0 | **APROVADA** — vai para o backlog. |
| 3.5 – 3.9 | **REPROVADA**, mas com cirurgia obrigatória: está a um gargalo da aprovação. |
| < 3.5 | **REPROVADA / DESCARTE** — nomeie a falha crítica que derrubou a nota. |

## Matriz risco vs recompensa (qualitativa)

Avaliação ortogonal à nota, calculada assim:

- **Recompensa potencial** — DERIVADA das notas, não julgada de novo
  (`scorecard.recompensa_potencial`): **ALTA** se Dor ≥ 4 **e** Escala ≥ 4
  (ex.: LOI + problema nacional); **BAIXA** se Dor ≤ 2 (só achismo);
  **MEDIA** no resto.
- **Risco técnico** — julgado sobre a arquitetura descrita. **ALTO**: multiagentes com
  scraping, escrita em sistema externo, tempo real ou dado de terceiro ainda não
  entregue. **MEDIO**: um ou dois agentes, function calling de leitura, APIs estáveis.
  **BAIXO**: RAG simples ou fluxo fixo, sem escrita externa. Na dúvida entre dois
  níveis, escolha o **maior** — o inverso da regra das notas.
- **Veredito** — cruzamento determinístico (`scorecard.MATRIZ_RISCO`):

| | Recompensa ALTA | Recompensa MEDIA | Recompensa BAIXA |
|---|---|---|---|
| **Risco BAIXO** | Barbada — execute já. | Vale o custo. | Esforço pequeno, retorno pequeno. |
| **Risco MEDIO** | Vale a pena. | Aposta calculada. | Provavelmente furada. |
| **Risco ALTO** | Vale a pena. | Arriscada — só avance com mitigação explícita. | Furada. |

O veredito da matriz **não altera a média nem o status** — ele qualifica a decisão de
executar. Uma APROVADA com "Arriscada" avança com mitigação; uma REPROVADA com
"Barbada" continua reprovada.

## PAI e Death Knell

Toda avaliação termina com dois compromissos verificáveis:

- **PAI (Plano de Ação Imediato)** — a ÚNICA ação das próximas 48h. Uma tarefa
  concreta e verificável, não uma direção ("validar o mercado" não é PAI;
  "entrevistar 3 gestores de logística até sexta" é).
- **Death Knell (sinal de morte)** — condição objetiva que, não cumprida até uma data
  (máximo 7 dias após a avaliação), enterra a ideia. Sem death knell, ideia morna
  sobrevive para sempre no backlog consumindo atenção. Vencido o prazo sem a condição,
  reavalie usando o fato como evidência negativa — normalmente derruba o pilar que a
  condição sustentava.
