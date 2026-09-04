# Contribuindo com o projeto

Obrigado pelo interesse em contribuir com o **hackathons-executioner-idea-validator**.

Este documento tem duas partes:

1. **[Como contribuir](#como-contribuir)** — o fluxo prático de trabalho.
2. **[Acordo de Licença de Contribuição (CLA)](#acordo-de-licença-de-contribuição-cla)** — os termos jurídicos que se aplicam a toda contribuição enviada ao projeto.

Ao enviar uma contribuição, você declara que leu e aceita integralmente o CLA da Parte 2. **Leia-o antes de abrir seu primeiro Pull Request.**

---

## Como contribuir

### Antes de começar

- Abra uma *issue* descrevendo o problema ou a proposta antes de investir tempo em código. Isso evita trabalho duplicado e alinha o escopo.
- Entenda o que este repositório entrega: a **skill** `executioner-idea-validator` (persona, framework de avaliação e scripts), **não** as ideias avaliadas com ela. O banco em `output/` é gerado localmente e fica fora do versionamento.
- Contribuições que alteram a régua de avaliação — pesos, faixas de veredicto ou a rubrica dos pilares — mudam o resultado de toda ideia já avaliada. Elas serão discutidas pelo mérito do critério, não pela conveniência de encaixar um caso específico.

### Restrições de desenho (não negociáveis)

Estas regras existem para que a avaliação seja auditável e reprodutível. Um PR que as viole será recusado por princípio de desenho, não por mérito técnico.

1. **Determinismo.** Mesma entrada + mesmo `--datahora` deve produzir arquivo **byte a byte idêntico**. A média usa `Decimal` com arredondamento `HALF_UP` em 2 casas — nunca `float`, nunca conta feita pelo modelo.
2. **Fonte única de verdade.** Pesos, arredondamento e faixas vivem em `scripts/scorecard.py`; os enums de domínio, função TOGAF e horizonte vivem em `scripts/taxonomia.py`. Importe deles — não recopie o número nem a lista.
3. **Zero dependências externas.** Só a biblioteca padrão do Python (3.9+). A skill precisa rodar em qualquer máquina sem `pip install`.
4. **Arquivos gerados não se editam à mão.** `references/taxonomia-negocio.md` é regenerado por script, e tudo em `output/` é escrito exclusivamente por `registrar_ideia.py`.
5. **`SKILL.md` enxuto.** É o único arquivo sempre carregado em contexto. Detalhe vai para `references/`, lido sob demanda.

Todas estão detalhadas em [`CLAUDE.md`](CLAUDE.md).

### Fluxo de trabalho

1. Faça um *fork* do repositório e crie um *branch* a partir da `main`.
2. Implemente a mudança, mantendo as convenções já existentes no código e na documentação ao redor.
3. Rode a bateria de verificação abaixo e cole o resultado no PR.
4. Mantenha a documentação em sincronia. Uma mudança de comportamento quase sempre toca mais de um arquivo — a matriz de sincronização está em [`CLAUDE.md`](CLAUDE.md#ao-alterar-a-skill-mantenha-em-sincronia).
5. Abra um Pull Request descrevendo **o que muda**, **por quê**, e quais **suposições e trade-offs** estão por trás da escolha.

### Verificação antes de abrir o PR

Nunca teste contra `output/`: é o banco real de quem estiver rodando. Use um diretório descartável e `--datahora` fixo.

```bash
SKILL=.claude/skills/executioner-idea-validator
TMP=$(mktemp -d)

# 1. Cálculo — confira as três faixas e suas fronteiras (>=4.00, 3.50-3.99, <3.50)
python3 $SKILL/scripts/scorecard.py --dor 4 --agente 5 --defesa 3 --escala 4

# 2. Registro
python3 $SKILL/scripts/registrar_ideia.py --json $SKILL/assets/ideia.exemplo.json \
  --output-dir $TMP --datahora "2026-01-01T00:00:00-03:00"

# 3. Idempotência — os dois md5 têm de ser iguais
md5sum $TMP/ideias-aprovadas/reentrega-zero.md
python3 $SKILL/scripts/registrar_ideia.py --json $SKILL/assets/ideia.exemplo.json \
  --output-dir $TMP --datahora "2026-01-01T00:00:00-03:00" >/dev/null
md5sum $TMP/ideias-aprovadas/reentrega-zero.md

# 4. Transição de faixa — baixe as notas e confirme que o arquivo MUDA de pasta,
#    preservando criado_em e acumulando o histórico

# 5. Validação — enum inválido e nota fora de 1–5 devem sair com exit 2

rm -rf $TMP
```

Se você mexeu em `scripts/taxonomia.py`, regenere a referência e inclua o resultado no commit:

```bash
python3 $SKILL/scripts/taxonomia.py --markdown > $SKILL/references/taxonomia-negocio.md
```

### Nunca envie no PR

- Arquivos de `output/` — nem os seus, nem como exemplo. Ideias avaliadas são material estratégico de quem as escreveu.
- Ideias reais de terceiros, dados de clientes, nomes de parceiros ou conteúdo de LOI dentro de exemplos ou testes. Para exemplo, use `assets/ideia.exemplo.json`, que é fictício.
- Credenciais, chaves de API ou `.claude/settings.local.json`.

### O que esperar

A revisão pode pedir ajustes de escopo, de nomenclatura ou de aderência às restrições de desenho. Não há prazo garantido de resposta, e não há obrigação de aceitar qualquer contribuição (ver Cláusula 7 do CLA).

---

## Acordo de Licença de Contribuição (CLA)

*Contributor License Agreement — versão 1.0*

Este Acordo estabelece os termos sob os quais Você concede direitos sobre suas Contribuições ao Projeto. Ele existe para garantir segurança jurídica a todos os usuários do Projeto: sem ele, o Mantenedor não teria certeza de possuir os direitos necessários para distribuir o Projeto sob a licença MIT.

Este Acordo **não transfere a titularidade** dos seus direitos autorais. Você continua sendo o autor e o titular da sua Contribuição, e permanece livre para usá-la como quiser, inclusive em outros projetos. O que Você concede é uma **licença** de uso, nos termos abaixo.

### 1. Definições

**1.1.** **"Projeto"** significa o repositório de software `hackathons-executioner-idea-validator` e todos os artefatos nele contidos, incluindo código-fonte, documentação, definições de agentes, skills, scripts e arquivos de configuração.

**1.2.** **"Mantenedor"** significa Fabio Borges, titular dos direitos autorais do Projeto, e seus sucessores ou cessionários.

**1.3.** **"Você"** ou **"Contribuidor"** significa a pessoa física ou jurídica que envia uma Contribuição ao Projeto e que aceita os termos deste Acordo.

**1.4.** **"Contribuição"** significa qualquer obra original de autoria, incluindo código-fonte, documentação, correções, traduções, testes, exemplos ou quaisquer modificações e acréscimos a obras preexistentes do Projeto, que seja intencionalmente submetida por Você ao Projeto para inclusão. Para os fins deste Acordo, "submetida" significa qualquer forma de comunicação eletrônica, verbal ou escrita enviada ao Mantenedor ou aos canais oficiais do Projeto, incluindo — sem limitação — Pull Requests, *patches*, *issues* contendo código, e mensagens em listas ou fóruns de discussão do Projeto. Exclui-se expressamente qualquer comunicação que Você identifique de forma clara e destacada, por escrito, como **"Não é uma Contribuição"**.

### 2. Concessão de licença de direitos autorais

Sujeito aos termos deste Acordo, Você concede ao Mantenedor e aos destinatários do software distribuído pelo Projeto uma licença de direitos autorais **perpétua, mundial, não exclusiva, gratuita, isenta de royalties e irrevogável** para:

a) reproduzir, preparar obras derivadas, exibir publicamente, executar publicamente, sublicenciar e distribuir a sua Contribuição e as obras derivadas dela;

b) incorporar a sua Contribuição ao Projeto e distribuí-la como parte integrante deste;

c) **relicenciar** a sua Contribuição sob a Licença MIT, nos termos da Cláusula 9 deste Acordo.

A licença ora concedida é irrevogável a partir do momento da submissão, ressalvado o disposto na Cláusula 10.2.

### 3. Concessão de licença de patente

Sujeito aos termos deste Acordo, Você concede ao Mantenedor e aos destinatários do software distribuído pelo Projeto uma licença de patente **perpétua, mundial, não exclusiva, gratuita, isenta de royalties e irrevogável** para produzir, encomendar a produção, usar, oferecer à venda, vender, importar e de outra forma transferir a sua Contribuição, isoladamente ou em combinação com o Projeto.

Esta concessão aplica-se exclusivamente às reivindicações de patente que Você seja titular ou possa licenciar e que sejam necessariamente infringidas pela sua Contribuição isoladamente, ou pela combinação da sua Contribuição com o Projeto ao qual ela foi submetida.

Caso Você inicie litígio de patente contra qualquer parte, alegando que o Projeto ou uma Contribuição nele incorporada constitui infração direta ou contributiva de patente, as licenças de patente concedidas por este Acordo a essa parte serão automaticamente extintas na data do ajuizamento.

### 4. Declarações e garantias do Contribuidor

Ao submeter uma Contribuição, Você declara e garante que:

**4.1. Autoria.** A Contribuição é obra original de sua autoria, integralmente criada por Você, ou Você detém os direitos necessários para submetê-la nos termos deste Acordo.

**4.2. Titularidade e legitimidade.** Você é legalmente habilitado a conceder as licenças previstas nas Cláusulas 2 e 3, e essas concessões não violam nem conflitam com qualquer direito de terceiros, contrato, acordo de confidencialidade ou obrigação a que Você esteja sujeito.

**4.3. Ausência de violação.** A Contribuição não viola direitos autorais, marcas, patentes, segredos de negócio, direitos de personalidade ou quaisquer outros direitos de propriedade intelectual ou industrial de terceiros, e não incorpora código sujeito a licença incompatível com a Licença MIT.

**4.4. Vínculo empregatício ou contratual.** Caso Você tenha criado a Contribuição no curso de relação de emprego, prestação de serviços ou vínculo acadêmico cujos termos atribuam a titularidade da obra ao empregador, contratante ou instituição, Você declara que: (i) obteve autorização expressa dessa entidade para submeter a Contribuição sob os termos deste Acordo; ou (ii) essa entidade renunciou formalmente a seus direitos sobre a Contribuição.

**4.5. Dados e informações confidenciais.** A Contribuição não contém credenciais, segredos, dados pessoais de terceiros, informação confidencial ou material sujeito a dever de sigilo. Para os fins desta cláusula, incluem-se expressamente ideias de negócio de terceiros, dados de clientes, nomes de parceiros e conteúdo de cartas de intenção eventualmente presentes em exemplos, testes ou arquivos do banco de ideias.

### 5. Conteúdo de terceiros

Caso a sua Contribuição inclua, no todo ou em parte, obra de terceiro que não seja de sua autoria, Você deverá **identificá-la de forma clara e destacada** no corpo do Pull Request, informando: a origem, o autor e a licença aplicável ao material. Contribuições que incorporem material de terceiro sem essa identificação poderão ser recusadas ou removidas do Projeto a qualquer tempo, sem aviso prévio.

### 6. Ausência de garantias

Salvo o disposto expressamente na Cláusula 4, a Contribuição é fornecida **"NO ESTADO EM QUE SE ENCONTRA"** (*as is*), sem garantias de qualquer natureza, expressas ou implícitas, incluindo — sem limitação — garantias de comercialização, adequação a uma finalidade específica, ausência de defeitos ou não violação de direitos.

Você não assume, por força deste Acordo, qualquer obrigação de prestar suporte, manutenção, atualizações ou correções relativas à sua Contribuição.

### 7. Ausência de obrigação de incorporação

O Mantenedor não tem qualquer obrigação de aceitar, incorporar, publicar, manter ou distribuir a sua Contribuição, e poderá, a seu exclusivo critério e a qualquer tempo, modificá-la, substituí-la ou removê-la do Projeto. A aceitação de uma Contribuição não gera expectativa de direito quanto a contribuições futuras.

### 8. Atribuição e créditos

O Mantenedor preservará os avisos de direitos autorais existentes e o registro de autoria das Contribuições no histórico de versionamento do Projeto, conforme a obrigação de manutenção do aviso de copyright prevista na Licença MIT.

Este Acordo não cria obrigação de atribuição adicional em materiais promocionais, documentação ou obras derivadas, além daquela exigida pela Licença MIT. Ficam ressalvados os direitos morais de autor que, nos termos da legislação aplicável, sejam irrenunciáveis.

### 9. Licença de saída (MIT)

Toda Contribuição aceita e incorporada ao Projeto será licenciada e distribuída aos usuários finais sob a **Licença MIT**, nos exatos termos do arquivo [`LICENSE.md`](LICENSE.md) deste repositório, sem termos ou restrições adicionais.

Você concorda que sua Contribuição seja distribuída sob essa licença e reconhece que, uma vez publicada, ela poderá ser usada por terceiros para quaisquer fins, inclusive comerciais, nos limites da Licença MIT.

### 10. Vigência e alterações

**10.1.** Este Acordo entra em vigor, para cada Contribuição, no momento de sua submissão, e permanece vigente por prazo indeterminado quanto às Contribuições já submetidas.

**10.2.** O Mantenedor poderá publicar novas versões deste Acordo. Novas versões aplicam-se exclusivamente a Contribuições submetidas após sua publicação, **não retroagindo** às Contribuições anteriores, que permanecem regidas pela versão vigente à época de sua submissão.

**10.3.** Você poderá cessar de contribuir a qualquer momento. A cessação não afeta as licenças já concedidas sobre Contribuições anteriormente submetidas, que permanecem irrevogáveis nos termos das Cláusulas 2 e 3.

**10.4.** Você compromete-se a notificar o Mantenedor, por escrito e sem demora injustificada, caso tome conhecimento de qualquer fato que torne inexata ou incompleta qualquer declaração prestada na Cláusula 4.

### 11. Disposições gerais

**11.1. Independência das cláusulas.** A eventual invalidade ou inexequibilidade de qualquer cláusula deste Acordo não prejudica a validade das demais, que permanecem em pleno vigor.

**11.2. Integralidade.** Este Acordo constitui o entendimento integral entre as partes quanto às Contribuições, prevalecendo sobre quaisquer entendimentos anteriores sobre o mesmo objeto.

**11.3. Lei aplicável e foro.** Este Acordo é regido pelas leis da República Federativa do Brasil, em especial pela Lei nº 9.610/1998 (Direitos Autorais) e pela Lei nº 9.609/1998 (Programas de Computador). Fica eleito o foro da Comarca de **SÃO PAULO/SP**, com renúncia a qualquer outro, por mais privilegiado que seja, para dirimir controvérsias decorrentes deste Acordo.

---

## Como aceitar este Acordo

A aceitação se dá por **qualquer** das formas abaixo:

- **Preenchimento do modelo de Pull Request** *(forma padrão)* — marque as três caixas da seção "📜 Acordo de Contribuição e Licenciamento" do modelo carregado automaticamente ao abrir o PR. A marcação dessas caixas constitui aceitação integral deste Acordo, e não apenas dos itens ali listados.

- **Declaração no Pull Request** — inclua no corpo do PR a seguinte linha:

  > Li e aceito integralmente os termos do CLA descrito em `CONTRIBUTING.md` deste repositório.

- **Assinatura no commit** — inclua no rodapé da mensagem de commit:

  ```text
  Signed-off-by: Seu Nome <seu@email.com>
  ```

  A assinatura atesta que Você leu o CLA, aceita seus termos e atende às declarações da Cláusula 4.

Pull Requests sem qualquer uma dessas formas de aceitação não serão incorporados até que a aceitação seja registrada.

**Verificação automática.** O fluxo `Aceite do CLA` (em `.github/workflows/cla-check.yml`) confere, a cada abertura ou edição de Pull Request, se as três declarações da seção de licenciamento estão marcadas. Enquanto não estiverem, a verificação falha e indica no resumo da execução exatamente qual declaração falta. Basta editar o corpo do PR e marcá-la — a verificação roda novamente sozinha.

---

## Dúvidas

Dúvidas sobre o processo de contribuição ou sobre os termos deste Acordo podem ser encaminhadas por meio de uma *issue* no repositório.
