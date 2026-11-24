# Matriz afirmação e evidência de D1

Corte: 24/11/2026. Código integrado: develop `557e5982bcecc1bbc3ca9dbab350406bbd15dc8f`; PR #31 incorpora `4a01910`. Resultado histórico e leitura atual do código são evidências diferentes. Os arquivos científicos privados e artefatos de treino v4 não foram recebidos para reprodução.

| Afirmação | Classe | Fonte e versão | Limite e ação editorial |
|---|---|---|---|
| Integração de pressão implementada | Código verificado | `src/uav_euler2d/validation.py`, `integrate_surface`, SHA 557e598; apêndice A | Verifica consistência entre arquivos, não erro de discretização; corrigir futuro verbal do capítulo 5 |
| Nós representam faces exportadas | Código verificado | `graph.py`, `build_surface_graph`, SHA 557e598; apêndice B | Centros não são endpoints; distinguir da formulação ideal por vértices |
| S3 usa 31/7/8 convergidos | Registro histórico e protocolo | `notes/euler2d-s3-experimental-protocol.md`; `PROJECT_STATE.md`, checkpoint 23/10 | Não reescrever manifesto; preservar `c0015`; não aplicar proporções genéricas 70/15/15 |
| Seed S3 é 202604 | Registro histórico | `notes/euler2d-s3-results-exploratory.md`, 13/10/2026 | Seed 42 pertence ao planejamento/novas operações, não à regeneração do split |
| Ridge tem métricas exploratórias | Resultado histórico não reexecutado | Apêndice C; notas S3, 13/10 | Manter os seis registros da tabela e suas limitações; nenhum número novo nesta revisão |
| GNN S3 não foi treinada | Registro histórico específico | `gnn.py` e executor S3; checkpoint 23/10 | Não generalizar a afirmação a toda atividade de João Pedro |
| GNN v4/GPR integrados | Integração verificada | PR #31, merge 557e598, 20/11 | Integração e checks não validam métricas da campanha |
| v4 usa não convergidos e cinco partes | Código e relato | `rede_grafos_v4_freada.py`; PDF do autor, pp. 4–5, 17–20 | População e supervisão diferem de S3; escores de desenvolvimento selecionam checkpoint |
| Teste foi consultado na v2 | Relato do autor | PDF `A rede em grafos v4, do zero.pdf`, p. 5; blob da PR #31 | Autor declara ausência de seleção baseada no teste; cronologia/artefatos pendentes. Não afirmar teste nunca consultado |
| Há experiência AG em andamento | Relato do autor | Mesmo PDF, p. 25 | Código e artefatos não integram a PR; não declarar ganho ou equivariância comprovados |
| Identidade algébrica implica equivariância | Hipótese não demonstrada | Capítulo 6; descritores numéricos de `graph.py` | Definir leis de transformação e testes próprios; não inferir propriedade da arquitetura |
| GPR interpola exatamente e conhece todo erro físico | Generalização indevida | Código `RBF + WhiteKernel`; Rasmussen e Williams (2006) | Regressão com ruído não garante interpolação; variância condicionada não substitui incerteza CFD |
| PR #16 é base atual do pipeline | Estado histórico superado | README e `notes/scope-migration-audit.md` | Foi fechada sem merge e arquivada; S1–S3 são a infraestrutura aceita |

O PDF incorporado tem SHA-256 `355f39089d7733e1823a252b2ef6dd0523458f207a8123858535161d8c48a82b`. Seus relatos são atribuídos ao pesquisador; a revisão editorial não os transforma em novas execuções verificadas.
