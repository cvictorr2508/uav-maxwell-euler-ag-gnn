# Plano detalhado proposto para conclusão

Versão de planejamento de 23/10/2026. A sequência será aprovada ou ajustada pelo Projeto 02. Esforços são relativos; não há datas de execução prometidas. O objetivo é concluir uma primeira fase Euler 2D cientificamente interpretável e consolidar texto e apêndices, com hipóteses e limitações explícitas.

## P0 — promoção editorial e transferência (pedido atual)

Entrada: develop com S1–S3 aceitas, main com merges de publicação anteriores. Entrega: uma PR de release para main, três apêndices navegáveis, PROJECT_STATE e este pacote. Verificações: teste/compilação, build HTML/PDF, ausência de dados privados e referência a SHAs/PRs.

Aceite: PR de promoção com checks aprovados, publicação autorizada e verificada, sincronização de retorno com checks aprovados, documentos completos e pacote recuperável em outra máquina.

Atualização P0: merge da PR #29 autorizado e concluído em main c2bf7d5; Quarto Publish e Pages deployment aprovados; índice, apêndices e PDF verificados no site. O usuário autorizou também a sincronização de retorno a develop e a revisão integral dos documentos. O pacote de encerramento registra essa integração em SYNC_VERIFICATION.json e recupera o develop remoto integrado. O mandato das próximas etapas será emitido pelo Projeto 02; nenhuma sprint experimental adicional foi iniciada.

## D1 — harmonização da documentação e do artigo/eBook

Dependência: mandato atualizado e estado remoto revalidado. Prioridade alta; escopo documental, sem novos experimentos.

1. Confrontar capítulos 5–6 com implementações S1–S3 e apêndices. Substituir afirmações de trabalho futuro já implementado por descrições sustentadas, preservando propostas ainda não executadas.
2. Consolidar a distinção entre artigo, eBook e dissertação; definir artefato editorial e público com o orientador.
3. Corrigir referências históricas conflitantes a PR #16 e realinhamento; preservar tags e conteúdo histórico como registro.
4. Documentar a exceção de seed 202604 e as partições herdadas; não recomputá-las para se ajustar a uma diretriz geral.
5. Mapear cada afirmação empírica a relatório/JSON/versão; completar origem dos parâmetros e unidades. Revisar bibliografia IEEE, tipos matemáticos e hipóteses de Maxwell/Euler.
6. Rever autoria, contribuição e licença do texto antes de distribuição acadêmica final. A licença MIT do código não resolve automaticamente a licença editorial.

Entregas: matriz afirmação–evidência, capítulos/apêndices harmonizados, lista de pendências. Aceite: Quarto HTML/PDF aprovado; links/citações válidos; nenhuma alegação de treino GNN, ganho AG ou Maxwell experimental sem evidência. Revisão científica do texto antes de merge/publicação autorizados.

## E1 — qualidade e proveniência dos dados

Dependência: acesso autorizado aos arquivos científicos. Consolidar versões Fluent, malhas, condições de contorno, parâmetros numéricos, convergência, origem do dataset derivado e hashes. Avaliar c0015 sem removê-lo do teste. Diagnosticar oito não convergidos e seis falhos. Selecionar geometrias para sensibilidade de malha somente se a inspeção justificar e houver autorização para simular.

Entregas: inventário privado, relatório de proveniência e de limitações públicas sem dados proprietários. Aceite: diferenças entre snapshot/média e inconsistência física tratadas explicitamente; parâmetros positivos e IDs rastreáveis; nenhuma campanha inteira repetida por conveniência. A insuficiência de arquivos deve constar como limitação, sem invenção retrospectiva.

## E2 — protocolo comparativo Ridge versus GNN convencional

Dependências: avaliação E1 e aprovação metodológica. Esta etapa complementa a evidência ausente na S3 e deve anteceder ablações AG, mesmo se a numeração futura das sprints mudar.

Definir tarefa global CL/CD; geometrias e condições pré-solver equivalentes; normalização só no treino; seed e orçamento fixados antes de avaliar teste. Acrescentar condicionamento Mach/ângulo de ataque e referências físicas relevantes à GNN. Documentar diferenças inevitáveis entre parâmetros geométricos globais do Ridge e atributos locais da superfície.

Preparar ambiente PyTorch local controlado apenas quando aprovado. Implementar inferência/avaliação e salvar configuração, versões, hardware, tempo, contagem de parâmetros e métricas por caso. Validar permutação dos nós e semântica de arestas conforme a arquitetura. Selecionar checkpoints/hiperparâmetros usando somente validação; orçamento pequeno, sem busca extensa ou distribuição.

Entregas: protocolo aprovado antes do teste final; código/testes; relatório com MAE/RMSE por alvo, erros por caso, custo e limitações. Aceite: mesmas partições 31/7/8 e c0015; nenhuma dependência de referência pós-solver; resultados reproduzíveis ou inviabilidade documentada. Não usar consistência física de campo quando apenas CL/CD forem previstos. Oito casos de teste limitam inferências; evitar rankings conclusivos.

## S4 — AG e ablações, condicionada

Dependência: comparação convencional interpretável e aprovação científica específica. Formalizar objetos em Cl(2,0), unidades, orientação, normalização e transformação sob rotações/reflexões. Distinguir vetores, bivetores, multivetores e tensores. Usar somente geometria disponível; não inferir endpoints/topologia faltante.

Comparar a mesma GNN com e sem atributos AG, alterando um mecanismo por vez e mantendo informação e orçamento comparáveis. Caso haja afirmação de equivariância, estabelecer lei de transformação e testes próprios. Não adotar arquitetura multivetorial complexa antes de demonstrar necessidade.

Entregas: definição matemática, testes algébricos e relatório de ablação. Aceite: qualquer ganho ou ausência de ganho sustentado pelos resultados; não confundir representação compacta com menor complexidade ou custo.

## S5 — generalização, recursos e reprodutibilidade

Dependência: modelos e protocolo aprovados. Examinar generalização por geometria, sensibilidade a condições e remalhamento apenas onde existirem dados. Preservar o teste fixo; qualquer nova campanha ou benchmark exige decisão própria. Não denominar cross-validation ou remalhamento como realizados se não foram executados.

Reproduzir uma execução em ambiente limpo e, se viável, em segunda máquina. Registrar versões, seeds, configuração, hashes de dados, tempo de preparação/treino/inferência/verificação, memória e CPU/GPU. Distinguir ausência de dados de falha de modelo. Avaliar incerteza com método compatível com poucas geometrias e declarar limites; intervalos ou repetições não criam novas observações independentes.

Aceite: outra pessoa consegue reproduzir os resultados com acesso autorizado aos dados; mudanças de ambiente são rastreadas; não há seleção no teste nem extrapolação 2D→3D sem benchmark próprio.

## F — síntese científica e encerramento da primeira fase

Consolidar metodologia de simulação, dados/malhas/grafos, modelos, protocolo, resultados, discussão e limitações na dissertação. Atualizar o artigo/eBook conforme o destino editorial escolhido. Maxwell pode continuar como fundamentação matemática; sua inclusão experimental requer benchmark próprio e orçamento autorizado. Multifidelidade/3D são extensões condicionais, não bloqueadores automáticos da conclusão Euler 2D.

Entregas: texto revisado, apêndices, matriz de contribuições demonstradas/hipóteses, pacote reprodutível e publicação aprovada. O orientador decide se a amostra/qualidade permitem comparação interpretável. Se não permitirem, concluir com infraestrutura verificada e limitações justificadas, em vez de produzir conclusões artificiais.

## Critérios transversais

Cada etapa deve conter escopo e critérios de aceite, PR coesa, testes proporcionais, revisão científica e decisão explícita sobre merge. Mudanças metodológicas, dados originais, partições, novas simulações e publicação não são autorizadas por este planejamento. Atualizar o estado e o guia ao final de cada etapa aceita.
