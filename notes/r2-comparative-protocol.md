# R2 Protocolo comparativo de krigagem e GNN

Versão `r2-euler2d-v1`, 24/11/2026. Destinatários: orientador e João Pedro. O escopo metodológico está fechado para implementação e revisão: comparar previsões de CL/CD em Euler 2D, preservando média e Ridge como controles e avaliando Cp da GNN separadamente. A solicitação desta entrega autoriza revisão e preparação; **não autoriza merge, instalação, treinamento, avaliação preditiva do teste ou novas simulações**.

O contrato numérico está em [r2-kriging-gnn-v1.json](../configs/experiments/r2-kriging-gnn-v1.json). Seus limites são decisões de planejamento, não medições de hardware ou resultados. A campanha depende das evidências E1 e do aceite específico descrito no [checklist de execução](../handoff/R2_EXECUTION_CHECKLIST.md). O código R1 continua sendo infraestrutura legada de desenvolvimento; R3/R4 ainda devem implementar este protocolo.

## Pergunta e alcance científico

Pergunta primária: quais erros por caso e custos apresentam GPR e GNN de superfície para CL/CD, nas mesmas partições convergidas e no domínio verificado? A tarefa secundária é prever Cp nas faces de parede. A comparação avalia dois sistemas com representações e supervisão diferentes: GPR recebe parâmetros geométricos e coeficientes; GNN recebe geometria discretizada e aprende também Cp. Um ganho da GNN não isolaria o efeito da arquitetura.

Não há hipótese de superioridade, equivalência ou margem física de 1% assumida. O arrasto é o observável invíscido definido nos arquivos, sem componente viscosa presumida. Cp superficial não permite avaliar campos volumétricos nem resíduos completos de Euler. Maxwell, 3D, AG como ablação, POD, multifidelidade, co-krigagem, aprendizado ativo e otimização geométrica ficam fora desta campanha.

## População e partições

- Unidade de erro: `case_id`. Nós e faces não são réplicas independentes. Todos os casos de uma `geometry_id` ficam na mesma partição.
- População primária: somente `success`, **31 treino, 7 validação, 8 teste**, lidos do manifesto original. Contagens divergentes bloqueiam a campanha; o aviso do validador genérico não basta para aceitar outro banco.
- `non_converged` e `failed` permanecem no inventário e no diagnóstico E1. Não são usados em ajuste, normalização, seleção ou métricas preditivas desta campanha. Snapshot final e média de janela permanecem distintos.
- Nenhum novo split, fold ou refit em treino+validação. A seed histórica S3 `202604` continua vinculada aos resultados históricos. As seeds novas não reconstroem partições.
- `c0015` permanece no teste. A análise principal inclui os oito casos. Não haverá ranking ou métrica agregada sem `c0015` nesta versão; sua ressalva de malha acompanha o erro individual. Uma sensibilidade posterior exige protocolo separado.

E1 deve verificar domínio, identidade geométrica, duplicatas físicas entre IDs, status, semântica de CL/CD, localização de Cp e convenções de normalização. O agrupamento por ID, sozinho, não detecta duas geometrias iguais com nomes diferentes. Parâmetros repetidos com malhas diferentes permanecem no mesmo grupo, sem alterar silenciosamente o manifesto; um vazamento detectado bloqueia a alegação de generalização e exige decisão documentada.

## Entradas e condições operacionais

Os limites geométricos fixos são m em [0, 0.04], p em [0.20, 0.60] e t em [0.08, 0.16], conforme domínio declarado no contrato S0 e transformação legada. E1 precisa confirmar a parametrização e os limites com o gerador. Valor fora do domínio não será truncado nem excluído para melhorar resultados: bloqueia o protocolo até revisão.

Esta versão exige **Mach, ângulo de ataque e corda constantes e finitos nos 46 casos elegíveis**, com corda positiva e Mach não negativo. Os valores efetivos serão obtidos dos metadados e registrados no inventário privado; não se presume Mach 0.8, ângulo 2 graus ou corda de 1 m por herança do script. Variação exige condicionamento dos dois sistemas e emenda anterior a qualquer ajuste. Essa restrição limita o estudo a geometrias no regime confirmado.

| Modelo | Entradas em inferência | Supervisão no treino | Saídas |
|---|---|---|---|
| Média e Ridge | m, p, t, Mach, ângulo e corda pré-solver, conforme `FeatureSpec` S3 | CL/CD | CL/CD |
| GPR | m, p, t; condições constantes verificadas como contrato | CL/CD, um GP independente por alvo | CL/CD e desvio-padrão condicionado |
| GNN v4 convencional | Sete atributos de nó e cinco de aresta da R1 | Cp; CL/CD usados apenas na seleção em validação | Cp; CL/CD por integração |

Os atributos GNN são x/c, y/c, s/c, normal x/y, comprimento da face/c e lado; nas arestas, deslocamento x/y/c, distância entre centros/c, produto escalar e produto exterior das normais. Há duas direções do contorno, sem arestas volumétricas. Os produtos entre normais são descritores numéricos já presentes na v4; esta campanha não é uma ablação AG nem demonstra equivariância.

Cp, pressões, coeficientes e valores de células adjacentes não entram nas features. IDs, status e diagnósticos não entram na rede. E1 deve confirmar que a geometria e a malha superficial são disponíveis antes da solução, sem adaptação guiada por campos do solver. Se isso não for verificável, limitar explicitamente a interpretação e bloquear a afirmação de inferência exclusivamente pré-solver.

## Modelos e seleção

Cada candidato ajusta somente os 31 casos de treino. A validação de sete casos seleciona hiperparâmetros e checkpoints; seus escores são de desenvolvimento. A seleção não usa custo, erro de teste, Cp de validação como critério alternativo ou preferências posteriores por casos.

Para cada alvo t em {CL, CD}, definir s_t como o desvio-padrão amostral dos 31 alvos de treino, limitado inferiormente a 1e-8. O critério comum é **J = (RMSE_val(CL)/s_CL + RMSE_val(CD)/s_CD)/2**. Registrar as duas escalas. Assim, o arrasto não é suprimido pela escala da sustentação. MAE/RMSE não normalizados continuam sendo os resultados principais por alvo.

### Média e Ridge

Uma média de treino, com dois alvos. Ridge usa os seis atributos históricos e alpha em {0.1, 1, 10}, sem regularizar intercepto, com padronização populacional do treino conforme implementação S3. Escolher um alpha conjunto pelo menor J; diferenças até 1e-12 usam o menor alpha. Não substituir as métricas históricas pelo novo ajuste.

### Krigagem por regressão gaussiana

Dois candidatos de kernel, cada um com GP independente para CL e CD: `ConstantKernel * RBF_ARD + WhiteKernel` e `ConstantKernel * Matern_ARD(nu=2.5) + WhiteKernel`. Escolher **uma família conjunta para os dois alvos** pelo menor J; diferença até 1e-12 favorece RBF. A alternativa Matérn é uma escolha limitada deste protocolo, sem presumir desempenho melhor.

Transformar m,p,t pelos limites físicos fixos, sem ajustar esses limites nos dados de validação. `normalize_y=True` usa estatísticas dos alvos de treino conforme a versão fixada do scikit-learn. Amplitude inicial 1, comprimentos iniciais [0.5,0.5,0.5], ruído inicial 1e-3; limites de cada hiperparâmetro [1e-5,1e5], alpha numérico 1e-10, otimizador L-BFGS-B, dez reinícios adicionais e seed 42. São **quatro ajustes GP e até 44 partidas de otimização**. Não ampliar limites, reinícios, jitter ou kernels após ver os erros. Não convergência do otimizador é registrada; predições finitas e fatoração válida são necessárias, sem ocultar avisos.

O WhiteKernel torna este um modelo de regressão, sem garantia de interpolação exata. O desvio-padrão preditivo depende do kernel, ruído estimado e hiperparâmetros ajustados; não inclui automaticamente erro CFD nem incerteza dos próprios hiperparâmetros. Essa distinção segue a [documentação oficial de GPR](https://scikit-learn.org/stable/modules/gaussian_process.html). O fundamento estatístico está em [Rasmussen e Williams](https://gaussianprocess.org/gpml/).

### GNN de superfície

Uma arquitetura: encoders MLP com SiLU, largura 32, seis camadas GINE com contexto global e LayerNorm, decoder escalar de Cp. Sem busca de largura/profundidade, dropout, ensemble ou cabeça global nova. As seeds fixas são **42, 43 e 44**. A seed 42 é primária; as outras duas medem estabilidade e não podem substituí-la por apresentarem menor erro.

Normalizações de nós, arestas e Cp são ajustadas exclusivamente nos grafos de treino e persistidas. Manter as estatísticas amostrais da R1 e o indicador de lado sem padronização. Cp é a única variável da loss de treino: para cada caso, média do erro quadrático de Cp normalizado ponderada pelos comprimentos de face; a loss do lote é a média desses valores por caso. Assim, mais faces não criam maior peso experimental por rotina.

AdamW: learning rate 1e-3, weight decay 0.01, lote 8; CosineAnnealingLR com T_max=1500 e eta_min=1e-5. Máximo 1500 épocas por seed. Avaliar J nos sete casos a cada época, integrando Cp desnormalizado com as normais, os comprimentos, o ângulo e a corda do caso. Guardar o primeiro checkpoint e depois somente melhorias de J superiores a 1e-6; parar após 150 épocas consecutivas sem tal melhoria. Não selecionar o menor Cp-RMSE como caminho alternativo.

Cada seed preserva seu checkpoint e preprocessing de treino. Sem refit nos 38 casos e sem escolher uma seed vencedora. Falha da seed 42 impede uma conclusão primária GNN, mesmo se outra seed terminar. Instabilidade numérica, NaN ou estouro de recursos invalidam a execução; atingir a paciência é uma conclusão normal. O teto de tempo não transforma um checkpoint parcial em resultado completo.

## Política do teste e congelamento

O documento integrado de João Pedro relata consulta ao teste na v2 (p. 5); S3 também contém métricas de teste previamente reportadas. O histórico disponível não reconstrói toda influência dessas consultas. Os oito casos são um **teste histórico com exposição prévia, para avaliação retrospectiva descritiva**. Congelar agora impede novas escolhas, mas não restaura um holdout nunca visto. Uma avaliação confirmatória independente exigiria benchmark novo e autorização própria, fora deste orçamento.

Durante desenvolvimento, a vista de modelagem contém só treino/validação. O custodiante pode ler teste para integridade, proveniência e validação física, registrando acesso; não fornece resíduos, gráficos de Cp ou rankings ao processo de seleção. O validador R1 lê referências de todas as partições: é ferramenta de auditoria, **não uma barreira de acesso ao teste**. R3/R4 devem separar a vista de modelagem da auditoria completa. Ler IDs, contagens e condições pré-solver para conferir a partição é permitido.

Antes de revelar qualquer predição/erro novo do teste, o [registro de congelamento](../templates/r2-freeze-record.json) deve identificar protocolo/configuração e SHAs, inventário e manifesto, ambiente/hardware, todos os candidatos e falhas, alpha/kernel selecionados, três checkpoints GNN, transformações, regras de métricas e autorizações. O custodiante confere hashes, estado limpo do código e orçamento consumido. Rejeitar campos obrigatórios vazios; os templates deste commit não constituem recibos preenchidos.

Após aceite específico da avaliação final, uma passagem em lote calcula, nos mesmos oito casos, as previsões oficiais da média, Ridge selecionado, par GPR selecionado e três GNNs, com uma abertura de rótulos para pontuação. São **seis sistemas, 96 valores escalares CL/CD**, além dos Cp das três GNNs. Não executar kernels perdedores no teste. Salvar predições e hashes em arquivo privado antes de inspecionar erros. Calcular todos os resumos desse arquivo não é novo treinamento ou nova consulta adaptativa. Cronometragem repetida usa cópias das entradas sem rótulos, sem novas escolhas ou pontuações.

Depois da abertura, nenhuma mudança de seed, arquitetura, kernel, tolerância, exclusão de caso ou processamento pode alegar o mesmo teste como independente. Erro de implementação comprovado recebe incidente com causa, diff e resultados anteriores preservados; uma correção requer revisão e eventual nova autorização, identificada como reavaliação exposta. Repetição técnica exata antes de revelar métricas requer registro; não é licença para selecionar a melhor tentativa.

O risco de viés na avaliação após seleção é tratado por [Cawley e Talbot](https://www.jmlr.org/papers/v11/cawley10a.html). O procedimento atual limita novas decisões, sem eliminar a limitação histórica de exposição e amostra.

## Métricas e interpretação

CL/CD: MAE e RMSE por alvo, resíduos assinados e erros absolutos por caso, todos com n explícito. Guardar predições sem recortar CD negativo. Reportar diferenças pareadas GNN menos GPR no mesmo caso e, descritivamente, diferenças de MAE/RMSE. Para GNN, a tabela primária usa seed 42 e apresenta também todas as seeds, mediana, mínimo e máximo; essas três seeds não elevam n=8 a n=24.

Cp: MAE ponderada por comprimento e RMSE ponderada por comprimento por caso, depois médias sobre os casos, com as três seeds separadas. Sem misturar uma média de RMSEs com uma RMSE global. Integrar também Cp de referência para registrar a discrepância superfície–CL/CD; esse diagnóstico não é erro de discretização nem modifica o alvo do GP.

Incerteza GPR: registrar média, desvio-padrão de observação com WhiteKernel, intervalos gaussianos pontuais de 90% e 95% (multiplicadores 1.644853626951 e 1.959963984540), largura e contagens de cobertura, na validação e na avaliação final autorizada. Sem recalibrar com os oito testes, sem tratar cobertura empírica de oito casos como calibração provada e sem intervalo conjunto CL/CD. Se sigma=0, resíduo padronizado é nulo quando o erro é zero e indefinido nos demais casos; não dividir por zero. A GNN não recebe intervalo probabilístico nesta versão; dispersão entre seeds é estabilidade de otimização.

Não usar MAPE, erro dividido por média possivelmente nula, teste de significância, bootstrap, margem de equivalência ou ranking universal. Uma diferença numérica não prova superioridade, equivalência ou utilidade operacional. Resultados negativos, execuções inviáveis e limites da amostra são resultados reportáveis.

## Orçamento fechado

Perfil de referência: uma máquina local, **CPU somente, um processo de ajuste e uma thread computacional**, sem jobs paralelos, GPU, cloud paga ou treinamento distribuído. Teto global: **8 horas de parede e 8 horas de núcleo CPU**, prevalecendo o primeiro atingido; RSS máximo do processo e filhos 8 GiB; saídas privadas até 2 GiB. O tempo de parede é a soma das execuções sequenciais ativas, incluindo preparação e encerramento; espera por decisões e trabalho humano de custódia não consomem esse teto computacional. Limites são tetos, não estimativas de duração. Medir CPU e threads inclui bibliotecas BLAS e subprocessos.

| Etapa | Limite | Ajustes máximos |
|---|---|---|
| E1 computacional, preflight e verificações sem treino | 30 min | 0 |
| Média e três alphas Ridge | 5 min no total | 4 |
| Dois kernels por dois alvos GPR | 10 min por ajuste, 40 min no total | 4, até 44 partidas de otimizador |
| Piloto técnico GNN, seed 42, somente treino | 10 épocas ou 10 min | 1, pesos descartados |
| GNN 42, 43 e 44 | 1500 épocas ou 120 min por seed | 3 |
| Congelamento, inferência e relatório final | 15 min | 0 |
| Margem global para encerramento | 20 min | 0 |
| **Total** | **480 min** | **12 ajustes; até 4510 épocas GNN incluindo piloto** |

O piloto futuro mede tempo/memória e verifica o caminho, sem avaliar validação/teste nem modificar arquitetura. Reiniciar do zero a seed 42 após descartar seus pesos. A preparação atual não executa esse piloto. Se a previsão de execução ultrapassar tetos, encerrar e reportar inviabilidade; mudar máquina, threads, épocas ou orçamento exige versão nova anterior ao ajuste principal. Uma configuração parcial não é promovida a campanha completa.

Falhas e tentativas abortadas consomem seus slots e tempo. Não há retries de ajuste fora dos 12 slots, não se reaproveita folga para mais candidatos e não se aumenta orçamento automaticamente. Registrar durações de preparação, ajuste, inferência fria e aquecida, número de nós/arestas, versões, parâmetros e memória. Para inferência aquecida, usar cinco warmups sem rótulos e vinte repetições no lote congelado; são medições de tempo, não novas decisões de modelo. Não comparar custo com CFD sem tempos CFD verificáveis.

## Condições para execução e entregas seguintes

E1 permanece **pendente de insumos privados**. O [template de inventário](../templates/r2-e1-inventory.json) exige hashes, origem, versões, convergência, janela/snapshot, malha de c0015 e cronologia de uso do teste. Ausências ficam explícitas. O orientador pode aceitar limitações históricas justificadas; não pode convertê-las em arquivos ou medições reconstruídos por suposição. Contaminação entre partições, alvos incompatíveis ou entradas pós-solver bloqueiam o escopo primário até decisão própria.

R3 unifica GPR CL/CD, candidatos, seleção e artefatos. R4 adapta a GNN ao split fixo, loss por caso, seleção J, parada e budgets. Antes do primeiro ajuste, exigir teste real sem otimização de forward/checkpoint e inferência sem Cp, permutação de nós com arestas remapeadas, integração com referências, importação sem efeitos e proteção dos originais. Fixar versões de Python/NumPy/PyArrow/scikit-learn/joblib/PyTorch/PyG e hardware no ambiente efetivamente disponível; não inventar lockfile histórico nem instalar pacotes por esta entrega.

A autorização posterior deve referenciar a versão e hash do protocolo, o aceite E1, SHAs de R1/R3/R4, ambiente, tetos e responsáveis. Uma segunda autorização libera a avaliação final depois do congelamento. Merge e publicação continuam decisões separadas. A conclusão de R2 é um plano concreto revisável, sem resultados preditivos novos.
