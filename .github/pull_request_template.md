## 📝 Descrição do Pull Request
<!-- Descreva de forma clara e concisa o que este PR faz e qual problema ele resolve. -->

## 🎯 Tipo de Alteração
<!-- Marque com um "x" a opção que se aplica (ex: [x]). -->
- [ ] 🐛 Correção de bug (bug fix)
- [ ] ✨ Nova funcionalidade (feature)
- [ ] ⚖️ Mudança na régua de avaliação (pesos, faixas ou rubrica dos pilares)
- [ ] 🗂️ Mudança no formato do banco de ideias ou na taxonomia de negócio
- [ ] ⚡ Melhoria de performance ou refatoração
- [ ] 📚 Atualização de documentação

## 🧪 Como isso foi testado?
<!-- Rode a bateria de CONTRIBUTING.md em um diretório descartável (mktemp -d), nunca contra output/. -->
- **Configuração de teste utilizada:** <!-- Ex: Python 3.13 (somente stdlib), Linux -->
- **Comando ou script executado:** <!-- Ex: registrar_ideia.py --json assets/ideia.exemplo.json --output-dir $TMP --datahora "2026-01-01T00:00:00-03:00" -->
- **Resultado esperado:**

### Verificações obrigatórias
- [ ] **Determinismo**: rodei o registro duas vezes com o mesmo `--datahora` e os dois `md5sum` bateram.
- [ ] **Faixas**: conferi as fronteiras de veredicto afetadas (`>=4.00`, `3.50–3.99`, `<3.50`), se mexi em `scorecard.py`.
- [ ] **Sem dependências novas**: a mudança usa apenas a biblioteca padrão do Python.
- [ ] **Gerados regenerados**: se mexi em `taxonomia.py`, rodei `--markdown` e commitei o `references/taxonomia-negocio.md` atualizado.
- [ ] **Documentação em sincronia**: atualizei os arquivos indicados na matriz de `CLAUDE.md`.
- [ ] **Sem `output/` no diff**: nenhum arquivo do banco de ideias foi incluído neste PR.

## 📜 Acordo de Contribuição e Licenciamento
<!-- Ao enviar este PR, você concorda com as diretrizes do projeto. -->
> Ao marcar as caixas abaixo, você declara que leu e aceita **integralmente** o [Acordo de Licença de Contribuição (CLA)](/CONTRIBUTING.md#acordo-de-licença-de-contribuição-cla) deste repositório, e não apenas os itens listados aqui.

- [ ] Confirmo que este código é de minha autoria ou que possuo os direitos para compartilhá-lo.
- [ ] Entendo e concordo que minha contribuição será distribuída sob a mesma **Licença MIT** deste projeto.
- [ ] Garanto que não incluí nenhuma chave de API, senha, credencial privada nem ideia de negócio de terceiro no material enviado.

## 🔗 Issues Relacionadas
<!-- Se este PR resolve alguma Issue aberta, mencione o número dela aqui (ex: Closes #12). -->
Closes #
