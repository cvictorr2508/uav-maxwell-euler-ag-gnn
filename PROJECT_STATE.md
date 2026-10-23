# Projeto 02 — estado de transferência

Checkpoint: 23/10/2026 (America/Sao_Paulo). Destino: chat 02.03 do Projeto 02 e Codex em outra máquina. Este arquivo é um estado verificado, não um novo mandato científico. O Projeto 02 atualizará o mandato após avaliar esta entrega. O chat de origem ficará sem atividade até pelo menos 16/11/2026; essa data não agenda uma retomada automática.

## Fonte de verdade e publicação

- Repositório: https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn
- Pages: https://cvictorr2508.github.io/uav-maxwell-euler-ag-gnn/
- develop observado: 3e088101ca1b7e7e94785949006b6a90b0db7f3e.
- main publicado: c2bf7d562e864e12b6c7a3a8e678b35f04c67a7d (merge da PR #29).
- gh-pages publicado: f39f16e79a07767d0260586a5f8054c0bde22aac.
- Branch de publicação: codex/release-s3-handoff-20261023, baseada em develop e contendo o merge de main. A divergência inicial era de sete commits exclusivos de develop e dois merges exclusivos de main; a integração local foi sem conflitos.
- PR #29: https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/pull/29 — merged em main após autorização explícita do usuário em 23/10/2026. Head aprovado: 3a6e0d1934b417b627970185eb87816241a81f78; checks test e render aprovados.
- Quarto Publish, run 39962381130, e Pages deployment, run 39962639167: success. A página inicial, os três apêndices e o PDF foram verificados por HTTPS, comparando os bytes aos blobs de gh-pages. O PDF publicado tem 105 páginas.
- PUBLICATION_VERIFICATION.json e RELEASE_RECEIPT.json do pacote registram SHA de origem, deployment, URLs e hashes.
- O pacote pós-publicação usa a branch LOCAL checkpoint/published-pr29-20261023, descendente do merge em main, para atualizar os documentos e o empacotador. Seu commit não foi enviado ao GitHub e não é o commit publicado. O bundle permite recuperá-lo. Os documentos dentro do snapshot remoto de main ainda registram a preparação pré-merge; usar o estado final deste pacote na retomada.
- O workflow Quarto Publish publica em gh-pages após push em main. Pages usa a raiz de gh-pages. Não é necessário criar infraestrutura nova.
- A sincronização de main de volta para develop continua pendente de autorização própria. develop remoto permanece em 3e088101ca1b7e7e94785949006b6a90b0db7f3e. A atualização documental local não cria outra PR nem modifica as branches remotas.

## Escopo científico

Mestrado de João Pedro no PPGEE/UnB: representações matemáticas de Maxwell e Euler em Álgebra Geométrica; representação de malhas e contornos em grafos; aprendizado e validação reprodutível. A primeira fase computacional utiliza perfis NACA com Euler 2D. Maxwell permanece fundamentação matemática, com benchmark independente ainda necessário para qualquer alegação experimental. O eBook Quarto e os resultados da dissertação são artefatos distintos. Não se presume vantagem de GNN, AG, equivariância ou multifidelidade.

O artefato editorial encontrado é um livro/eBook Quarto com index.qmd e oito capítulos, não um manuscrito independente de artigo. A versão publicada preserva esses capítulos e acrescenta três apêndices técnicos de revisão baseados nos resultados aceitos. O chat 02.03 deverá confirmar com o Projeto 02 o destino editorial de um eventual artigo autônomo.

## Sprints e evidências

| Etapa | Estado | Evidência |
|---|---|---|
| S0 | Concluída | Contratos em notes/ e realinhamento acadêmico |
| S1 | Concluída com ressalvas | PR #26; merge 84645da47d08415a842fce0c60a5da62272b02f9 |
| S2 | Concluída | PR #27; merge 84a178cde05008ba2bdf259ec47f7d68ee89a671 |
| S3 | Concluída operacionalmente; GNN protótipo não treinado | PR #28; merge 3e088101ca1b7e7e94785949006b6a90b0db7f3e |
| Ajustes finais S3 | Integrados | 6c6c5f0b890e171c2960ef3d0dbfa84c287ebd5e; barreira de validação e semântica de --run-gnn |
| S4 | Não iniciada | Requer avaliação e mandato atualizado |
| S5 | Não iniciada | Generalização e reprodutibilidade após protocolo aprovado |

Os checks Python e Quarto do merge S3 em develop foram verificados como success. A suíte sintética contém nove testes. O pacote registra separadamente as verificações desta transferência, sem atribuir novas execuções a 13/10.

## Dados e resultados aceitos

60 casos: 46 success, oito non_converged, seis failed; 54 superfícies. Referência convergida fixa: 31 treino, sete validação, oito teste. Não reescrever split_manifest.json. c0015 permanece no teste com ressalva de malha. Vários case_id podem referenciar a mesma geometry_id; geometrias devem ser disjuntas para alegações de generalização geométrica.

Entradas Ridge: m, p, t, mach_inf, alpha_deg, chord_ref_m. Alvos: CL e CD. Cp, pressão e coeficientes Fluent são referências e não entradas preditivas. Padronização só no treino; Ridge alpha=1,0. Seed reportada da execução histórica: 202604. A diretriz geral de seed 42 não autoriza alterar o split herdado.

| Modelo, teste (8 casos) | MAE CL | RMSE CL | MAE CD | RMSE CD |
|---|---:|---:|---:|---:|
| Média de treino | 0,16352 | 0,18885 | 0,02466 | 0,02729 |
| Ridge | 0,02588 | 0,03020 | 0,00264 | 0,00299 |

Resultados de 13/10/2026, exploratórios. Sem evidência de superioridade geral. Não há resultado de treino GNN. --run-gnn só verifica disponibilidade e informa training_executed=false. O executor bloqueia métricas experimentais se validate_dataset registrar erros; avisos dos casos não convergidos permanecem avisos.

## Limitações para a continuidade

1. A GNN usa atributos geométricos dos nós, mas ainda não recebe condições globais como Mach e ângulo de ataque. Corrigir a assimetria informacional antes de comparação Ridge/GNN autorizada.
2. O dataset não fornece endpoints nem topologia volumétrica. A continuidade por distância entre centros e comprimentos é diagnóstico, não prova topológica. contour_index não define orientação física.
3. Proveniência Fluent, qualidade das malhas, causas das falhas e sensibilidade a refinamento exigem consolidação. Não repetir a campanha indiscriminadamente.
4. Nove testes sintéticos não cobrem toda corrupção possível; denominadores e parâmetros inválidos podem provocar exceções no validador. Registrar e delimitar futuras correções, sem alegar robustez universal.
5. A GNN protótipo não tem protocolo completo de inferência/avaliação ou equivalência de orçamento. Registro histórico de versões/hardware/tempo ainda é incompleto.
6. Os capítulos 5–6 contêm planejamento anterior à implementação S1–S3. Os apêndices tornam os resultados acessíveis; a harmonização editorial completa continua pendente.
7. Documentos antigos em notes/ mencionam PR #16 como draft; README e scope-migration-audit registram seu fechamento sem merge e arquivo em tags. Preservar o histórico e corrigir contradições na sprint documental.
8. Dados privados, PDFs internos e arquivos Fluent não integram o Git nem o pacote público. A transferência privada desses insumos é uma tarefa separada.

## Entrada para retomada

Ler handoff/README.md, handoff/PROMPT_CHAT_02_03.md, handoff/RESUME_GUIDE.md, handoff/COMPLETION_PLAN.md, handoff/DECISIONS_AND_OPEN_ISSUES.md e handoff/EXTERNAL_ASSETS.md. Antes de alterar software ou iniciar experimentos, obter o mandato atualizado do Projeto 02. Toda situação remota deste checkpoint deve ser reconsultada na nova máquina.
