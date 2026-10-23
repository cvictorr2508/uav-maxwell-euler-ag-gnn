# Pacote de continuidade — Projeto 02 / chat 02.03

Data de referência: 23/10/2026. A pausa do chat de origem está prevista até pelo menos 16/11/2026; não depende dele a preparação da outra máquina. A sequência de trabalho futura depende do mandato atualizado do Projeto 02.

## Ordem de leitura

Consultar primeiro DOCUMENTS_TO_TRANSFER.md, que lista integralmente os documentos a repassar ao chat 02.03.

1. PROJECT_STATE.md: situação técnica e científica, evidências e restrições.
2. RELEASE_STATUS.md: branch, PR e mecanismo de publicação.
3. PROMPT_CHAT_02_03.md: texto integral para iniciar a continuidade.
4. RESUME_GUIDE.md: preparação e verificação da outra máquina.
5. COMPLETION_PLAN.md: etapas restantes, entregas e critérios de aceite.
6. DECISIONS_AND_OPEN_ISSUES.md: decisões já tomadas e escolhas pendentes.
7. EXTERNAL_ASSETS.md: materiais privados necessários e transferência separada.
8. PROJECT_02_MANDATE_INPUT.md: subsídios para o Projeto 02 emitir o mandato atualizado.

## Composição do pacote externo

O diretório de entrega inclui estes documentos, um recibo de release consultado no GitHub, evidências locais de testes/build, uma cópia dos fontes versionados em ZIP e um Git bundle da branch de publicação. O bundle permite recuperar o código sem autenticação; o clone do GitHub e a consulta ao estado atual continuam preferíveis. Uma cópia renderizada HTML/PDF é fornecida quando o build local for aprovado. SHA256SUMS.json permite verificar os arquivos transportados.

O recibo externo é deliberadamente separado do commit: o SHA final de um commit e o estado posterior dos seus checks não podem ser gravados dentro desse mesmo commit sem referência circular. Revalidar a PR e Pages na retomada.

## Estado final da publicação

A PR #29 foi mesclada com autorização e o site foi verificado. O pacote pós-publicação acrescenta PUBLICATION_VERIFICATION.json, CHECKPOINT_FINAL.md e published-book/ com uma cópia exata do PDF servido. rendered-book/ continua sendo o preview local validado anteriormente.

## Edição de encerramento após sincronização

Usar a edição ENCERRAMENTO, que substitui para a continuidade as edições de preparação e PUBLICADO, preservadas como histórico. A sincronização main→develop e a incorporação dos documentos anteriormente locais foram autorizadas; SYNC_VERIFICATION.json registra a PR, o merge e os checks finais. O pacote é gerado a partir do develop remoto integrado. O bundle permite clonar a branch develop diretamente; repository-source.zip corresponde a esse mesmo commit. Não é necessário recuperar uma branch exclusivamente local para obter o prompt, o planejamento ou o guia revisados.

main continua no commit c2bf7d5 publicado em Pages. develop contém essa história e a revisão documental adicional; SHAs diferentes são esperados. O recibo distingue publicação, sincronização e commit empacotado. Os documentos completos do chat 02.03 estão listados em DOCUMENTS_TO_TRANSFER.md, incluindo o mandato atualizado que o Projeto 02 ainda deverá emitir separadamente.

Os fontes e o bundle contêm histórico público do repositório; nenhuma restauração de componentes antigos implica aceitação científica. Não enviar credenciais, .env, tokens, perfis de navegador, ambientes virtuais ou dumps privados. O PDF de acompanhamento e o dataset não acompanham o pacote.
