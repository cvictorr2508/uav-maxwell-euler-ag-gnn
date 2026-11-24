# R2 Parecer de revisão das PRs 32 e 33

Revisão de 24/11/2026, sobre `develop` base `557e5982bcecc1bbc3ca9dbab350406bbd15dc8f`. O parecer se limita à preparação documental e técnica; não é aprovação de merge nem de campanha experimental. Não houve ajuste de modelos, instalação de dependências ou acesso novo a dados privados.

## Resultado da revisão

| PR e versão revisada | Parecer no escopo de preparação | Limite para a campanha |
|---|---|---|
| [32 R0](https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/pull/32), `8485b6f59468ca553d4d7ee15809aa77603c4c67` | Favorável após ajuste editorial; dez arquivos documentais, sem alteração das seis linhas de métricas históricas | Evidência v4/AG e materiais CFD ainda não reproduzidos; não promove resultados a aceitos |
| [33 R1](https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/pull/33), `d411cb1fecd3076dedfce354c8cc42af973e373b` | Favorável como infraestrutura de preparação após correção do contrato de escoamento | Integração real Torch/PyG/scikit-learn/dataset privado pendente; CLI legado não implementa R2 |

## Achados corrigidos nas próprias branches

**P2 editorial na R0.** Os acréscimos aos capítulos e apêndices expunham números de PR, tarefas R1 e estados internos de desenvolvimento na narrativa científica, em conflito com `notes/editorial-scientific-guidelines.md`, item 1. O commit `8485b6f` mantém esses registros nas notas e handoff e usa datas, comportamento da implementação e limites de evidência no eBook. Não altera fatos científicos ou tabela histórica. A base documental continua distinguindo dados históricos, implementação auditada e resultados relatados pelo autor.

**P2 no contrato salvo da R1.** `predict_cp` iterava sobre o dicionário salvo de condições. Se esse dicionário fosse vazio, a comparação não verificava Mach nem ângulo; uma inferência fora do regime poderia prosseguir. O commit `d411cb1` exige exatamente os dois campos finitos, Mach não negativo e rejeita booleanos, chaves ausentes ou excedentes. Aplica a mesma validação ao carregamento GNN e ao artefato GPR. O teste de regressão cobre oito contratos inválidos e bloqueio antes da chamada do modelo. Isso não altera o kernel, a arquitetura ou parâmetros treinados.

## Verificações

R0: revisão do diff dos dez arquivos, histórico/partições preservados, nenhuma chave bibliográfica ausente, HTML/PDF recompilados com execução científica e instalação automática desabilitadas. Inspeção visual de tabelas, equações, ressalvas e referências nas páginas afetadas; 106 páginas. Os artefatos locais desta revisão têm nomes separados dos recibos anteriores. [Checks do commit revisado](https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/commit/8485b6f59468ca553d4d7ee15809aa77603c4c67/checks).

R1: 30 testes locais, 29 aprovados e um pulado por ausência de PyTorch/PyG. Em ambiente sem site-packages, 27 aprovados e três pulados por dependências opcionais. Compilação e `git diff --check` aprovados. O CI de biblioteca padrão também passou, com os mesmos três testes opcionais pulados. Nenhum teste ajusta modelos. [Checks do commit revisado](https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/commit/d411cb1fecd3076dedfce354c8cc42af973e373b/checks).

O teste opcional com pesos aleatórios não foi executado localmente e não constitui integração validada com dados científicos. Os checks verdes verificam somente o ambiente e os caminhos efetivamente exercitados.

## Diferenças entre R1 e o protocolo fechado R2

| Comportamento legado em R1 | Decisão R2 a implementar em R3/R4 |
|---|---|
| GPR isolado prevê apenas CL; outro comparador interno ajusta CL/CD | Um executor GPR comum com dois alvos, RBF/Matérn limitados e artefato completo |
| v4 junta treino/validação para cinco partes de desenvolvimento | Treino 31 e validação 7 fixos, sem CV nem refit em 38 |
| Seleção de época por Cp e MSE agrupada por nós | Loss por caso ponderada por comprimento; seleção por J conjunto CL/CD e parada explícita |
| Uma seed 42, teto de épocas, sem limitador global de recursos | Seeds 42/43/44, teto por slot e global, ledger e falhas contabilizadas |
| Verificação de condições somente nos casos selecionados de desenvolvimento | Constância de Mach/ângulo/corda verificada nos metadados dos 46 success |
| Validador comum lê superfícies/rótulos de todas as partições | Auditoria de custódia separada da vista de modelagem; teste histórico registrado |
| Diretório novo e metadados protegem saídas | Congelamento de artefatos e autorização própria antes da pontuação final |

As diferenças são requisitos deliberados de R2, não afirmações de que R1 já os executa. Não chamar `--execute` dos scripts legados para produzir a comparação fechada. Nenhum dado, teste ou orçamento é aprovado por uma opção de linha de comando.

## Pendências que permanecem explícitas

E1 depende dos arquivos e da cronologia sob custódia de João Pedro. A transferência ENCERRAMENTO, as versões científicas anteriores e o ambiente de ML não foram reconstruídos nesta máquina. Os templates vazios não substituem evidências. Condições operacionais variáveis, duplicatas físicas entre partições ou semântica incompatível de alvos exigem decisão anterior à campanha.

O orçamento de oito horas é um envelope conservador fixado para a proposta, não uma medição de viabilidade. Um piloto futuro autorizado poderá concluir inviabilidade dentro dos limites; não libera automaticamente GPU, outra máquina, mais seeds ou ajustes. O teste permanece exposto historicamente, incluindo métricas S3 e consulta v2 relatada. Nenhuma revisão atual recupera sua condição de teste nunca visto.

Próximas entregas: implementar R3 e R4 conforme o [protocolo](r2-comparative-protocol.md), resolver E1, validar ambiente sem otimização e submeter o pacote concreto para autorização específica. Após este parecer, o orientador autorizou o encerramento de R1/R2 e o merge das PRs #33/#34 em develop. A PR #33 foi integrada em `495f551d6252b8fa6cf02e8b9803ef1740d991d6`; a integração de #34 será conferida após os checks da nova base. R0/#32 continua separada, em rascunho. O [registro de encerramento](../handoff/R1_R2_CLOSURE.md) delimita o aceite e as pendências.
