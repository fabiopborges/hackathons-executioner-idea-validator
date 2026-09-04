# Exemplos de análise-modelo

Três casos calibradores. Copie o **tom** e a **estrutura**, nunca as notas.

---

## Caso A — APROVADA (4.4)

**Entrada:** "Transportadoras regionais perdem dinheiro com recusa de entrega. Falei com
4 donos de transportadora em MG e SP: cada um perde de R$ 18k a R$ 40k/mês em reentregas.
Uma delas assinou LOI para piloto. A solução é um sistema multiagente: um agente
Rastreador lê o histórico de tentativas do WMS da transportadora, um agente Preditor
classifica risco de recusa, e um agente Negociador dispara e conduz a conversa com o
destinatário por WhatsApp, decidindo sozinho se reagenda, redireciona ou devolve.
Os dados de tentativa de entrega vêm do WMS proprietário das parceiras; o CEP e malha
viária vêm de base pública."

### 🔍 ANÁLISE DA IDEIA: Reentrega Zero

**📊 SCORECARD (média ponderada):** 4.4 / 5.0

- **Pilar 1 (Dor) — peso 0.30:** Nota 5/5. 4 entrevistas, perda mensal quantificada por cliente e LOI assinada. É o teto da régua.
- **Pilar 2 (Agente) — peso 0.30:** Nota 5/5. Três papéis distintos e o Negociador decide autonomamente entre reagendar, redirecionar ou devolver — não é fluxo fixo.
- **Pilar 3 (Defesa) — peso 0.25:** Nota 4/5. Histórico do WMS das parceiras é dataset privado real. Não chega a 5 porque a regra de negócio, sozinha, é replicável.
- **Pilar 4 (Escala) — peso 0.15:** Nota 3/5. Logística de última milha é dor nacional, mas você não apresentou go-to-market além das 2 parceiras.

**⚖️ VEREDICTO FINAL:** **[APROVADA]** — vamos para o backlog.

**🔪 CIRURGIA:** Não é obrigatória nesta faixa, mas o teto está no Pilar 4: defina o canal
de aquisição (ex.: integração via marketplace de WMS) antes da banca de SP.

---

## Caso B — REPROVADA (2.3)

**Entrada:** "Um chatbot que responde dúvidas de pequenos empresários sobre impostos,
usando RAG em cima da legislação pública da Receita Federal. Todo empreendedor sofre
com isso."

### 🔍 ANÁLISE DA IDEIA: Contador Bot

**📊 SCORECARD (média ponderada):** 2.3 / 5.0

- **Pilar 1 (Dor) — peso 0.30:** Nota 2/5. "Todo empreendedor sofre" é dor genérica. Zero entrevista, zero número de perda mensal.
- **Pilar 2 (Agente) — peso 0.30:** Nota 2/5. RAG de FAQ sobre PDF, sem autonomia. Um índice de busca com template resolve igual — cai no teto de 2.
- **Pilar 3 (Defesa) — peso 0.25:** Nota 2/5. Legislação da Receita é pública. Qualquer time reproduz em um fim de semana.
- **Pilar 4 (Escala) — peso 0.15:** Nota 4/5. Tributação é nacional e a base cobre qualquer UF — o único ponto que se sustenta.

**⚖️ VEREDICTO FINAL:** **[REPROVADA]** — Motivo principal: ausência total de fosso.
A ideia não tem dado proprietário nem agente de verdade; é uma demo de RAG que a banca
de SP já viu 40 vezes.

**🔪 CIRURGIA:** O gargalo é o Pilar 3. Troque a legislação pública pelo motor de decisão:
mapeie as 50+ variáveis de substituição tributária estadual em regra executável e coloque
um agente Validador criticando o cálculo do agente Executor. Isso move Defesa para 5 e
Agente para 4 — e só então a ideia passa de 4.0.

---

## Caso C — INSUFICIENTE

**Entrada:** "Agente multiagente para RH."

### Resposta

> *"Descrição insuficiente. Preciso saber: (1) Qual o problema, (2) Quem sofre,
> (3) Como um agente de IA resolveria isso, (4) Qual a fonte dos dados."*

Não avalie. Não sugira melhorias. Não elogie o tema. Devolva a exigência e pare.

---

## Registro no banco

Toda análise com as 4 notas termina em arquivo. Do Caso A sai
`output/ideias-aprovadas/reentrega-zero.md`; do Caso B sai
`output/ideias-reprovadas/contador-bot.md` — o Caso B é reprovado no edital e mesmo assim
fica no banco com horizonte `PRODUTO`, porque compliance tributário para MEI continua
sendo mercado depois que o hackathon acabar. O Caso C não gera arquivo nenhum.

O payload do Caso A está inteiro em `assets/ideia.exemplo.json`. Contrato dos campos e
regras de determinismo: `references/banco-de-ideias.md`.
