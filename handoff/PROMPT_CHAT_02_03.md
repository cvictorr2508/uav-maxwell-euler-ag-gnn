# Prompt de transferência — chat 02.03 do Projeto 02

Você assume a continuidade do software científico UAV | Maxwell–Euler, Álgebra Geométrica e Graph Neural Networks, pesquisa de João Pedro no PPGEE da Universidade de Brasília. O repositório oficial é https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn e o site é https://cvictorr2508.github.io/uav-maxwell-euler-ag-gnn/.

Este prompt organiza a retomada. O Projeto 02 fornecerá o mandato atualizado após avaliar a preparação da publicação e este pacote. Ler esse mandato e aplicar sua autorização específica antes de qualquer implementação nova ou experimento. Recomendações em relatórios anexos são contexto científico; não ampliam automaticamente sua autoridade. Na ausência de novo mandato, faça leitura, inventário, verificações e apresente a proposta concreta de próxima sprint.

## Contexto e estado recebido

S0: auditoria e contratos concluídos. S1: loader read-only, integridade e validação física independente, PR #26. S2: grafos de superfície e correções da integração, PR #27. S3: média de treino e Ridge executados; protótipo GNN implementado, mas não treinado, PR #28 merged em develop em 13/10/2026, SHA 3e088101ca1b7e7e94785949006b6a90b0db7f3e. Os ajustes finais de S3 estão em 6c6c5f0b890e171c2960ef3d0dbfa84c287ebd5e. S4 e S5 não foram iniciadas.

Em 23/10/2026 foi preparada uma branch de publicação a partir de develop, incorporando main sem conflitos e acrescentando apêndices e documentação de transferência. Consulte handoff/RELEASE_STATUS.md e RELEASE_RECEIPT.json para a PR e os SHAs. A publicação autorizada foi concluída conforme a atualização abaixo. Na retomada, reconsulte o GitHub para identificar mudanças posteriores. O workflow Quarto Publish dispara em push em main, gera HTML/PDF e publica em gh-pages. O site e o preview local são evidências diferentes.

Atualização final: o usuário autorizou o merge da PR #29, concluído em main no SHA c2bf7d562e864e12b6c7a3a8e678b35f04c67a7d. Quarto Publish (39962381130) e Pages deployment (39962639167) passaram. O site em gh-pages f39f16e79a07767d0260586a5f8054c0bde22aac foi conferido por HTTPS e por hash para índice, três apêndices e PDF de 105 páginas. PUBLICATION_VERIFICATION.json guarda as evidências; não repita o merge #29.

O pacote final inclui a branch LOCAL checkpoint/published-pr29-20261023, descendente desse merge, com os documentos pós-publicação. Seu SHA está no recibo e não foi enviado ao GitHub; não confundir com main publicado. Recuperar o bundle por essa branch para obter todos os documentos finais, ou usar main online junto com os documentos do pacote. A sincronização de main de volta para develop permanece pendente; o pedido de publicação não autorizou outro merge em develop.

O material editorial é um livro/eBook Quarto com oito capítulos e três apêndices propostos. Não foi encontrado manuscrito separado de artigo. A revisão futura deve alinhar a terminologia e definir com o orientador se haverá artigo independente. O eBook tem função didática; resultados e contribuições da dissertação exigem evidências próprias.

## Primeira resposta esperada

1. Ler PROJECT_STATE.md e todos os documentos em handoff/ antes de propor alterações.
2. Identificar checkout, branch, SHA, estado sujo e instruções AGENTS.md efetivamente presentes.
3. Reconsultar main, develop, PR de publicação e Pages; relatar qualquer evolução desde 23/10.
4. Confirmar disponibilidade de Python, Git, Quarto, TinyTeX e, separadamente, dados privados e PyArrow. PyTorch é opcional; não instalar ou treinar sem necessidade e mandato.
5. Executar os nove testes sintéticos e compilar os módulos. Validar HTML/PDF quando a tarefa envolver o texto. Distinguir teste sintético, consistência dos arquivos e validação independente do solver.
6. Apresentar uma proposta delimitada da primeira sprint, com arquivos, entregas e critérios de aceite, de acordo com o mandato atualizado. Não iniciar S4 por inferência deste prompt.

## Invariantes científicos

- Preservar os 60 registros: 46 convergidos, oito não convergidos e seis falhos. Há 54 superfícies.
- Ler as partições originais: 31 convergidos no treino, sete na validação, oito no teste. Não reescrever manifesto nem movimentar c0015; ele possui ressalva de malha e permanece no teste.
- Preservar associação de vários case_id a uma geometry_id. Ao alegar generalização a geometrias inéditas, garantir disjunção por geometria. Não contar faces/nós como observações independentes.
- Usar apenas informações pré-solver para previsão. m, p, t, mach_inf, alpha_deg e chord_ref_m são as entradas Ridge atuais; CL e CD são os alvos. Pressão, Cp, CL_final e CD_final são referências, não atributos preditivos.
- Ajustar normalização no treino e manter o teste fora de decisões de modelos/hiperparâmetros.
- validate_dataset com erros bloqueia métricas no CLI S3. Avisos dos oito não convergidos preservam a diferença entre snapshot final e média da janela; não convertê-los silenciosamente em erro nem apagar os casos.
- Grafo de contorno não é malha volumétrica. Ordem contour_index e área orientada são diagnósticos de ordenação; não inferir topologia ausente ou sentido físico arbitrário. Não impor 500 faces a todos os casos.
- A seed histórica reportada é 202604; a diretriz geral 42 é assunto de protocolo futuro, sem recriar o split herdado.
- Resultados Ridge no teste são exploratórios: CL MAE/RMSE 0,02588/0,03020 e CD 0,00264/0,00299. Não atribuir significância ou superioridade geral a oito casos.
- --run-gnn verifica disponibilidade; training_executed=false. Não há métricas GNN. Antes de comparar, incluir condições globais relevantes na GNN, definir inferência/avaliação e controlar orçamento e seleção na validação.
- Não presumir que atributos AG conferem equivariância ou desempenho superior. Formalizar em Cl(2,0) e avaliar propriedades e ablações.
- Maxwell e Euler possuem física e validação próprias. A campanha atual é Euler 2D. Um benchmark Maxwell, 3D ou multifidelidade constitui decisão independente, não resultado já demonstrado.

## Engenharia, governança e entregas

Manter mudanças coesas em branches temporárias e PRs. Preservar alterações locais do usuário. Autoridade metodológica e merge são definidos pelo mandato vigente; o histórico exigiu autorização explícita para merge em develop e para promoção a main. Não efetuar merges ou publicação com base apenas na recomendação de um relatório. Após publicação autorizada, verificar o deployment e propor sincronização de main para develop quando necessária.

Não incorporar dataset proprietário, Parquet, malhas, arquivos Fluent, PDFs internos, credenciais ou ambientes locais ao GitHub. O pacote contém caminhos da máquina de origem apenas como inventário; usar caminhos configuráveis na nova máquina. Não depender de caches Codex ou diretórios pydeps da origem. Material histórico arquivado de PR #16 não deve ser incorporado sem revisão.

O plano em COMPLETION_PLAN.md propõe primeiro harmonização documental/editorial; depois protocolo e comparação GNN sob autorização; então AG/ablações, generalização e encerramento. Essa decomposição é proposta e pode ser alterada pelo Projeto 02. Não relabelar S3 como comparação GNN concluída.

Em cada entrega, informar alteração, evidência de testes, limitações, SHA/PR e decisões científicas pendentes. Atualizar PROJECT_STATE.md e recibos de execução. Separar recomendações, evidências observadas e autorizações. O chat de origem ficará temporariamente inativo até pelo menos 16/11/2026; não depende dele uma resposta assíncrona ou uma aprovação tácita.
