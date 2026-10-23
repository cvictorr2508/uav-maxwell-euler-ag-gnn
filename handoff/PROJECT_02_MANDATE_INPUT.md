# Subsídios para o mandato atualizado — Projeto 02

Este documento é um roteiro para a decisão do Projeto 02, não uma autorização emitida pelo Codex. Preencher e aprovar no Projeto 02; anexar a decisão ao chat 02.03 junto com PROMPT_CHAT_02_03.md.

## Evidências disponíveis para a decisão

- PROJECT_STATE.md identifica S0–S3, commits aceitos e limitações científicas.
- A PR de publicação promove o software S1–S3 e acrescenta apêndices de revisão; RELEASE_STATUS.md e o recibo externo fornecem URL/SHA/checks.
- Há nove testes sintéticos, validação real com zero erros e oito avisos preservados. Não há treino GNN novo ou alterações de dados/partições.
- COMPLETION_PLAN.md propõe revisão documental/editorial, qualidade/proveniência, comparação GNN, AG/ablações e encerramento.

## Decisões a explicitar no novo mandato

1. Identificador e versão do mandato, responsável científico e data.
2. Artefato prioritário e objetivo da próxima sprint: eBook/artigo/dissertação ou protocolo experimental.
3. Arquivos/etapas autorizados, entregas, limites e critérios de aceite.
4. Decisão sobre merge da PR para main e publicação Pages; sincronização posterior com develop.
5. Autonomia para branches, commits, testes e PRs; quem aprova merges em develop/main.
6. Se e quando haverá autorização para dependências/treino GNN, condições operacionais, orçamento, seeds e avaliação final do teste.
7. Custódia/acesso ao dataset e aos documentos Fluent na outra máquina.
8. Procedimento de avaliação científica, incluindo resultados negativos ou inviabilidade de comparação com a amostra disponível.

## Restrições históricas a preservar ou revisar explicitamente

Dados originais e partições são preservados; c0015 fica no teste; dados privados não entram no GitHub; teste não seleciona hiperparâmetros; AG/GNN não têm superioridade presumida; Maxwell experimental exige benchmark próprio. O planejamento proposto não autoriza S4, novas simulações, treinamento ou publicação.

## Encaminhamento

Entregar à outra máquina: pacote ZIP e hash externo, mandato atualizado aprovado, prompt do chat 02.03 e acesso privado aos insumos necessários. O chat de origem estará temporariamente sem atividade até pelo menos 16/11/2026; não usar silêncio como aprovação.
