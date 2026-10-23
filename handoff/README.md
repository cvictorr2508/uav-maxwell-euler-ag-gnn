# Pacote de continuidade — Projeto 02 / chat 02.03

Data de referência: 23/10/2026. A pausa do chat de origem está prevista até pelo menos 16/11/2026; não depende dele a preparação da outra máquina. A sequência de trabalho futura depende do mandato atualizado do Projeto 02.

## Ordem de leitura

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

O Git bundle anuncia a branch LOCAL checkpoint/published-pr29-20261023 e as referências observadas de origin/main e origin/develop. O checkpoint local inclui os documentos atualizados e o empacotador compatível com uma PR já mesclada; não foi enviado ao GitHub. Os recibos distinguem seu SHA do commit c2bf7d5 publicado em main. Para continuar esse estado completo, clonar o bundle pela branch de checkpoint e depois consultar o remoto. Um clone online de main recupera o código publicado, mas seus documentos ainda descrevem a preparação da PR; consultar também os documentos atualizados deste pacote.

Os fontes e o bundle contêm histórico público do repositório; nenhuma restauração de componentes antigos implica aceitação científica. Não enviar credenciais, .env, tokens, perfis de navegador, ambientes virtuais ou dumps privados. O PDF de acompanhamento e o dataset não acompanham o pacote.
