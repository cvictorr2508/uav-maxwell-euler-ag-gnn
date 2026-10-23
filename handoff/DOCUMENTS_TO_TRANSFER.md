# Documentos completos para o chat 02.03

Usar a edição ENCERRAMENTO do pacote. O ZIP completo contém os documentos abaixo, código, evidências e material de revisão. As edições de preparação e PUBLICADO são históricas e não precisam ser reenviadas. Extrair em pasta curta no Windows, por exemplo C:\uav.

## Documentos a anexar ou disponibilizar ao chat 02.03

| Ordem | Arquivo no pacote | Finalidade |
|---|---|---|
| 1 | Mandato atualizado do Projeto 02, entregue separadamente | Autoriza escopo, entregas, autonomia e critérios das próximas sprints. Ainda será emitido pelo Projeto 02; este pacote não o substitui |
| 2 | handoff/PROMPT_CHAT_02_03.md | Prompt detalhado para iniciar o chat; colar seu conteúdo como mensagem inicial junto com o mandato |
| 3 | PROJECT_STATE.md | Estado técnico e científico, evidências, partições, métricas históricas, restrições e limitações |
| 4 | CHECKPOINT_FINAL.md | Estado final observado, commits e situação das operações no encerramento |
| 5 | handoff/COMPLETION_PLAN.md | Plano detalhado até a conclusão: revisão editorial, proveniência, GNN, AG/ablações, generalização e síntese |
| 6 | handoff/RESUME_GUIDE.md | Passos para preparar a outra máquina, recuperar develop, validar dados e reproduzir testes/build |
| 7 | handoff/DECISIONS_AND_OPEN_ISSUES.md | Decisões aceitas, ressalvas técnicas e escolhas científicas ainda abertas |
| 8 | handoff/PROJECT_02_MANDATE_INPUT.md | Subsídios para o Projeto 02 redigir e aprovar o novo mandato; não é autorização |
| 9 | handoff/EXTERNAL_ASSETS.md | Insumos científicos externos, caminhos históricos, dependências e transferência privada |
| 10 | handoff/RELEASE_STATUS.md | Histórico da publicação e da sincronização, com referência aos recibos finais |
| 11 | handoff/README.md | Visão geral do pacote, ordem de leitura e distinção entre artefatos |
| 12 | handoff/DOCUMENTS_TO_TRANSFER.md | Este inventário completo |

Os arquivos Markdown são documentos legíveis; não dependem do Codex antigo. O prompt, o planejamento e o guia estão integralmente incluídos e revisados, não apenas mencionados por links.

## Evidências a manter disponíveis

- RELEASE_RECEIPT.json: SHA empacotado, referência de publicação, branches observadas e checks.
- SYNC_VERIFICATION.json: PR main→develop, merge, checks da PR e do commit integrado, ancestralidade e preservação dos fontes científicos.
- PUBLICATION_VERIFICATION.json: Quarto Publish, Pages deployment, revisão de gh-pages e conferência HTTP do índice, apêndices e PDF.
- LOCAL_VERIFICATION.json: verificações locais anteriores, explicitamente datadas; não as confundir com os checks finais da sincronização.
- SHA256SUMS.json e scripts/verify_transfer.py: integridade dos arquivos extraídos.
- Arquivo externo com sufixo .zip.sha256.json: hash do ZIP transportado.
- DATASET_SHA256.json: hashes dos arquivos privados do dataset; não contém o dataset.

O relatório de verificação final do ZIP e do clone offline é entregue ao lado do ZIP porque é produzido depois de sua geração. Repassá-lo como evidência complementar.

## Código e texto para a outra máquina

- repository.bundle: histórico e branch develop integrada; usar o guia para recuperar o checkout.
- repository-source.zip: snapshot dos mesmos fontes sem metadados Git; alternativa de leitura.
- published-book/: cópia exata do PDF publicado, para revisão do artigo/eBook e dos apêndices.
- rendered-book/: preview HTML/PDF local da revisão anterior; a evidência do site publicado está separada.
- Endereço do site: https://cvictorr2508.github.io/uav-maxwell-euler-ag-gnn/.

O chat 02.03 precisa de acesso ao código, seja pelo ZIP/bundle, seja pelo clone do GitHub. Não é necessário enviar cada arquivo de código como anexo avulso.

## Materiais a repassar separadamente, por canal autorizado

Para revisar recomendações científicas: relatório de acompanhamento do Projeto 02 de 13/10/2026 e relatório S1. Para reproduzir validação real: dataset derivado Euler 2D completo, com os manifestos e Parquet. Para auditoria do solver: malhas e arquivos/configurações Fluent sob custódia do pesquisador. Esses materiais não estão no GitHub nem no ZIP; consultar EXTERNAL_ASSETS.md. Não enviar credenciais ou ambientes da máquina antiga.

## Sequência de encaminhamento

Primeiro, o Projeto 02 avalia os documentos e emite o mandato atualizado. Depois, encaminhar ao chat 02.03 o mandato, o prompt e o ZIP ENCERRAMENTO com seu hash, destacando PROJECT_STATE, planejamento e guia. Se a interface não permitir ao chat abrir ZIP, anexar separadamente os documentos da primeira tabela e disponibilizar o bundle ao Codex da outra máquina. Confirmar leitura antes de iniciar implementação nova.
