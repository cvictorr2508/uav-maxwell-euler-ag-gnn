# Auditoria de migração de escopo — S2-R0

**Data de referência:** 13/10/2026 · **Branch:** `refactor/academic-research-scope-2026` → `develop` · **Natureza:** revisão do conteúdo corrente com preservação de histórico Git.

## Contexto e decisão

O repositório renomeado `cvictorr2508/uav-maxwell-euler-ag-gnn` deixa de orientar sua narrativa e seu planejamento à aplicação anteriormente contemplada. O objeto atual é Maxwell, Euler, Álgebra Geométrica, grafos de malhas, aprendizado e validação em problemas acadêmicos independentes. A aprovação científica de cada capítulo continua sendo responsabilidade do orientador.

A nova identidade não constitui uma conclusão experimental, nem transforma um dataset anterior em benchmark validado. Esta PR não altera `main`, não altera a PR #16 e não faz publicação do eBook.

## Inventário de componentes

| Classe | Componentes | Tratamento nesta refatoração |
| --- | --- | --- |
| A — matemáticos reutilizáveis | Álgebra Geométrica, geometria discreta, Maxwell/Euler, fundamentos GNN, dados e bibliografia pertinente | Preservados ou recontextualizados nos capítulos ativos. |
| B — identidade/documentação | README, índice, metadados, estrutura dos Capítulos 1–8, notas, decisões e objetivos | Realinhados às questões Q1/Q2/Q3; capítulos 6 e 8 passam a tratar de validação, não de aplicação integrada. |
| C — fora do escopo atual | Objetivos de projeto vinculados à combinação de características aerodinâmicas e retorno eletromagnético, descrições de aplicações anteriores e código especializado de branches legadas | Excluídos do conteúdo ativo, sem reescrever o histórico Git. A PR #16 continua pendente de triagem. |

## Alterações de arquitetura documental

- Atualização de `README.md`, `index.qmd`, `_quarto.yml`, `CITATION.cff`.
- Substituição de conteúdos de contexto, objetivos, treinamento e extensão 3D por formulações acadêmicas.
- Renomeação de `chapters/06_optimization.qmd` para `chapters/06_validation_2d.qmd`.
- Renomeação de `chapters/08_optimization_3d.qmd` para `chapters/08_validation_3d.qmd`.
- Revisão de capítulos de matemática e física, sem imputar ganhos de representação aos modelos.
- Bibliografia atualizada para literatura científica pertinente; obras removidas continuam recuperáveis no histórico.
- Remoção de `src/ucav_aerostealth/__init__.py`, que era um placeholder vazio em `develop`; a implementação genérica do pacote continua somente na PR #16, ainda não integrada.

## Riscos e limitações

**PR #16:** permanece com arquivos e nomenclatura do trabalho anterior, ainda em draft. Não integrar automaticamente. Propor reaproveitamento seletivo de rotinas genéricas apenas depois de avaliação de código e objetivos, possivelmente em nova branch científica.

**Histórico e GitHub Pages:** commits, discussões e branches anteriores são evidências históricas. Uma PR para `develop` não modifica `main` nem `gh-pages`. A publicação só ocorrerá mediante decisão separada.

**Dataset e resultados anteriores:** contratos de dados e relatórios S1 são referências de procedência e não substituem verificação do solver. Não criar resultados sintéticos rotulados como reais.

**Propriedade intelectual:** eBook e dissertação possuem escopos e processos de aprovação distintos; João Pedro mantém responsabilidade pela pesquisa e validação das contribuições.

## Critérios de aceite

- [ ] Todas as fontes correntes estão livres da identidade e objetivos aplicativos anteriores, resguardados os registros históricos do Git.
- [ ] Q1, Q2 e Q3 estão consistentes no README, índice, contrato científico e Capítulo 1.
- [ ] Citações Quarto possuem chaves presentes na bibliografia; metadados e caminhos resolvem.
- [ ] Render Quarto (HTML e PDF) sem erros, ou impedimento documentado e corrigido.
- [ ] Ausência de mudanças nos workflows além do necessário para a compilação.
- [ ] Nenhuma alteração de resultados, dados brutos e PR #16; nenhum merge automático em `main`.

## Próximo marco

Avaliação do contrato e revisão da PR de realinhamento; depois, encaminhar ao Codex auditoria de **somente leitura** do código genérico da PR #16 e planejar benchmarks científicos independentes. O resultado dessa auditoria não é presumido aqui.

## Transição concluída — verificação de 13/10/2026

A PR #22 foi integrada em `develop`. A PR #16 foi encerrada **sem merge** e sua branch `feature/ch5-2d-data-ga-pipeline` foi excluída. As 11 branches de desenvolvimento existentes durante a transição tiveram suas pontas preservadas por tags sob `archive/academic-realignment-2026-10-13/`, e a correspondência exata de seus SHAs foi confirmada diretamente no GitHub.

O workflow de transição arquivou os commits, excluiu as branches e criou a PR #25 (`develop` → `main`). O job terminou com falha HTTP 403 ao tentar criar a tag adicional `completed`, **após** as operações principais. A inexistência dessa tag foi registrada; os 11 arquivos de tags históricos foram verificados individualmente, e a lista atual de branches contém somente `main`, `develop` e `gh-pages`. O workflow administrativo e seu script foram eliminados de `develop`.

Os metadados em `README.md`, `_quarto.yml` e `CITATION.cff` utilizam a identidade e o endereço GitHub vigentes. `CITATION.cff` ainda reflete a autoria de software previamente declarada; eventuais contribuições e crédito acadêmico de João Pedro dependem de confirmação editorial, sem atribuição automática nesta transição.

A PR #25 permanece proposta de publicação. Seu merge em `main` e a execução de GitHub Pages exigem aprovação posterior; nenhuma comprovação numérica de S1 foi produzida pela refatoração.
