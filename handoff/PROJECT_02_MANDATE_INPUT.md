# Subsídios para o mandato atualizado — Projeto 02

Este documento é um roteiro para a decisão do Projeto 02, não uma autorização emitida pelo Codex. Preencher e aprovar no Projeto 02; anexar a decisão ao chat 02.03 junto com PROMPT_CHAT_02_03.md.

## Evidências disponíveis para a decisão

- PROJECT_STATE.md identifica S0–S3, commits aceitos e limitações científicas.
- A PR #29 promoveu o software S1–S3 e acrescentou apêndices de revisão; merge autorizado em main c2bf7d5, workflow e site verificados. RELEASE_STATUS.md e os recibos externos fornecem URL/SHA/checks e evidências de publicação.
- Há nove testes sintéticos, validação real com zero erros e oito avisos preservados. Não há treino GNN novo ou alterações de dados/partições.
- COMPLETION_PLAN.md propõe revisão documental/editorial, qualidade/proveniência, comparação GNN, AG/ablações e encerramento.
- A sincronização main→develop e a incorporação dos documentos anteriormente locais foram autorizadas; o pacote de encerramento registra a PR e os checks finais em SYNC_VERIFICATION.json.

## Decisões a explicitar no novo mandato

1. Identificador e versão do mandato, responsável científico e data.
2. Artefato prioritário e objetivo da próxima sprint: eBook/artigo/dissertação ou protocolo experimental.
3. Arquivos/etapas autorizados, entregas, limites e critérios de aceite.
4. Registrar a publicação da PR #29 e a sincronização de retorno autorizada, com os documentos revisados em develop. Definir governança para merges e publicações futuras.
5. Autonomia para branches, commits, testes e PRs; quem aprova merges em develop/main.
6. Se e quando haverá autorização para dependências/treino GNN, condições operacionais, orçamento, seeds e avaliação final do teste.
7. Custódia/acesso ao dataset e aos documentos Fluent na outra máquina.
8. Procedimento de avaliação científica, incluindo resultados negativos ou inviabilidade de comparação com a amostra disponível.

## Restrições históricas a preservar ou revisar explicitamente

Dados originais e partições são preservados; c0015 fica no teste; dados privados não entram no GitHub; teste não seleciona hiperparâmetros; AG/GNN não têm superioridade presumida; Maxwell experimental exige benchmark próprio. O planejamento proposto não autoriza S4, novas simulações, treinamento ou publicação.

## Encaminhamento

Entregar à outra máquina: edição ENCERRAMENTO do ZIP e hash externo, documentos listados em DOCUMENTS_TO_TRANSFER.md, mandato atualizado aprovado, prompt do chat 02.03 e acesso privado aos insumos necessários. O chat de origem estará temporariamente sem atividade até pelo menos 16/11/2026; não usar silêncio como aprovação.
