# UAV | Maxwell–Euler, Álgebra Geométrica e Graph Neural Networks

Repositório de pesquisa acadêmica do Programa de Pós-Graduação em Engenharia Elétrica (PPGEE), Universidade de Brasília. O estudo investiga representações matemáticas das equações de Euler e Maxwell, Álgebra Geométrica (AG), geometria de malhas e métodos de aprendizado profundo em grafos.

## Questões científicas

- **Q1 — Matemática:** quais propriedades de Euler e Maxwell podem ser representadas de modo consistente em Álgebra Geométrica, preservando hipóteses, tipos matemáticos e equações de conservação?
- **Q2 — Grafos:** quais informações geométricas de domínios e malhas são preservadas por diferentes representações e atributos de Graph Neural Networks (GNNs)?
- **Q3 — Verificação:** como avaliar integridade dos dados, consistência física, generalização, reprodutibilidade e custos de pipelines que combinam métodos numéricos e aprendizado de máquina?

## Delimitação

O desenvolvimento de software concentra-se em **problemas acadêmicos independentes e não militares**, como escoamentos 2D de referência, geometria de malhas, propagação eletromagnética, experimentos sintéticos e benchmarks públicos. O estudo teórico de espalhamento eletromagnético integra a fundamentação física; não constitui uma cadeia de otimização de retorno radar, redução de detectabilidade ou integração de objetivos aeronáuticos de furtividade. Nenhum ganho de AG ou GNN é presumido sem validação empírica.

Geometrias UAV podem servir como contexto *civil* ilustrativo; o objeto central é a metodologia matemática e computacional, não o projeto ou a otimização de uma aeronave.

## Desenvolvimento reproduzível

```text
Equações e hipóteses → discretização / malha → descritores em AG
                                    ↓
                         grafos e datasets
                                    ↓
                  baselines de regressão / GNN
                                    ↓
                     verificação e validação
                                    ↓
                análise de erros e recursos
```

O eBook científico é escrito em **Quarto**. Conteúdo pedagógico do eBook e resultados específicos da dissertação são distinguidos. Referências bibliográficas utilizam estilo numérico IEEE.

- `main`: conteúdo estável e revisado;
- `develop`: integração após revisão de PRs;
- branches de trabalho: alterações delimitadas, com revisão e verificações proporcionais.

Consulte [o contrato científico de escopo](notes/research-scope-2026-10-13.md), [as diretrizes científicas](notes/editorial-scientific-guidelines.md) e [a proposta de contrato dos dados Euler 2D](notes/euler2d-dataset-contract.md).

## Continuidade do trabalho

A mudança de escopo preserva o histórico Git para fins de rastreabilidade. Documentos e branches antigos **não** são evidências de que resultados científicos foram verificados. A PR #16 foi encerrada sem merge e sua branch antiga foi excluída após o realinhamento. O código e seu histórico permanecem disponíveis na tag `archive/academic-realignment-2026-10-13/feature/ch5-2d-data-ga-pipeline`, para eventual reutilização somente após revisão científica.

## Licença

O código existente está sob licença MIT. A licença do eBook e de outros conteúdos acadêmicos requer confirmação específica antes de redistribuição.
