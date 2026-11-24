# Encerramento das entregas R1 e R2

Decisão de 24/11/2026: o orientador solicitou verificar o encerramento de R1/R2 e integrar suas PRs em develop. O aceite cobre a infraestrutura de preparação e o protocolo fechado. Treinamento, instalação de dependências, nova avaliação preditiva do teste, novas simulações e publicação permanecem fora dessa autorização.

| Entrega | Critério de encerramento | Registro |
|---|---|---|
| R1, PR #33 | Infraestrutura revisada, importação sem ajuste, validação comum, contratos de inferência e testes proporcionais | Merge em develop `495f551d6252b8fa6cf02e8b9803ef1740d991d6`, após test/render aprovados |
| R2, PR #34 | Protocolo/configuração, política do teste, orçamento e formulários privados definidos e revisados | Encerramento autorizado, integração após checks sobre a base R1. O estado e SHA finais constam na [PR #34](https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/pull/34) |

O protocolo `r2-euler2d-v1` mantém 31/7/8 success, c0015 no teste, escolha somente pela validação, GPR RBF/Matérn, GNN 42/43/44 com seed primária 42 e envelope de oito horas. O JSON especifica a campanha e não inicia execução. A autorização de integração fica limitada às PRs #33/#34 em develop, sem abranger R0/#32, main ou futuras PRs.

## Pendências transferidas às próximas entregas

- E1: receber e aceitar inventário privado, proveniência CFD, condições constantes, malha de c0015 e cronologia de uso do teste. E1 não está concluída.
- R3: unificar o GPR de dois alvos, candidatos, seleção J, incerteza e artefatos.
- R4: adaptar GNN ao treino/validação fixos, loss por caso, seleção J, parada, seeds e limites de recursos.
- Antes de ajustar modelos: validar o ambiente real de ML, versões/hardware e integração sem otimização, incluindo forward/checkpoint, permutação e inferência sem rótulos. Os testes opcionais ausentes não são promovidos a aprovados.
- A campanha exige autorização específica; a pontuação final exige novo aceite após congelamento. O teste continua histórico com exposição prévia.

R0/#32 permanece em rascunho. Os documentos dessa PR registram o corte anterior à integração R1/R2. O histórico científico e as métricas S3 permanecem preservados. Encerrar R1/R2 não conclui E1, E2, S4 ou S5.
