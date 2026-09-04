# Taxonomia de negocio do banco de ideias

> Arquivo GERADO. Nao edite a mao -- a fonte e `scripts/taxonomia.py`.
> Regenerar: `python3 scripts/taxonomia.py --markdown > references/taxonomia-negocio.md`

Vocabulario controlado: `registrar_ideia.py` rejeita qualquer valor fora destas
listas. Se nenhum termo servir, adicione-o em `scripts/taxonomia.py` e regenere
este arquivo -- nunca improvise um rotulo novo no JSON da ideia.

## Dominio de negocio (setor onde a dor vive)

Escolha exatamente um. `Transversal` so quando a dor independe de setor.

- Agronegocio
- Construcao e Imobiliario
- Educacao
- Energia e Utilities
- Financeiro e Bancario
- Juridico
- Logistica e Transporte
- Manufatura e Industria
- Midia e Entretenimento
- Recursos Humanos e Servicos Profissionais
- Saude
- Seguros
- Setor Publico
- Tecnologia e SaaS
- Telecomunicacoes
- Turismo e Hospitalidade
- Varejo e E-commerce
- Transversal

## Funcao de negocio (TOGAF Business Function)

Capacidade que o agente executa ou apoia, conforme a decomposicao de Business
Function da Business Architecture do TOGAF (ADM Fase B). Escolha de 1 a 3, da
mais central para a menos central. Funcao e capacidade, nao departamento: se a
ideia automatiza cobranca, a funcao e `Gestao Financeira e Contabil`, mesmo que
na empresa isso caia no time de vendas.

- Estrategia e Planejamento
- Marketing e Geracao de Demanda
- Vendas e Gestao de Canais
- Gestao de Clientes e Relacionamento
- Atendimento e Suporte ao Cliente
- Desenvolvimento de Produto e Servico
- Operacoes e Entrega de Servico
- Cadeia de Suprimentos e Logistica
- Manufatura e Producao
- Suprimentos e Compras
- Gestao de Ativos e Manutencao
- Gestao Financeira e Contabil
- Gestao de Riscos, Compliance e Auditoria
- Juridico e Contratos
- Gestao de Pessoas
- Gestao de Dados e Informacao
- Tecnologia da Informacao

## Potencial de produto real

- **ALTO** — cliente pagante identificavel e dor recorrente; sobrevive sem o edital.
- **MEDIO** — dor real, mas monetizacao ou canal ainda indefinidos.
- **BAIXO** — so faz sentido como demo de competicao.

## Horizonte

- **HACKATHON** — serve para a banca, mas nao se sustenta como negocio.
- **PRODUTO** — nao ganha o edital (pouco brilho de agente), mas vira negocio real.
- **HACKATHON_E_PRODUTO** — serve para os dois. Prioridade maxima.
- **NENHUM** — nao serve para nenhum dos dois. Arquive e siga.

O horizonte e ortogonal ao status: uma ideia REPROVADA no framework pode ter
horizonte PRODUTO e continuar valiosa. E exatamente por isso que o banco guarda
as reprovadas em vez de descarta-las.
