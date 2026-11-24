# R1 — infraestrutura para preparação experimental

R1 refatora a contribuição de João Pedro integrada na PR #31. A arquitetura v4 (32 canais, seis camadas GINE, sete entradas de nó e cinco de aresta) e o kernel GPR RBF/WhiteKernel são preservados. O PDF original permanece como documento histórico anterior à refatoração; seus números e referências a linhas não são resultados desta versão.

## Preparar sem treinamento

Com o dataset privado fora do checkout:

```powershell
$env:PYTHONPATH = 'src'
python -m uav_euler2d.kriging C:\dados\dataset_euler_2d
python -m uav_euler2d.rede_grafos_v4_freada C:\dados\dataset_euler_2d
```

Os comandos executam o validador comum, preservam o manifesto e exibem um resumo com `training_executed=false`. Não criam modelos nem resultados preditivos. A preparação GNN também verifica a exportação compartilhada de atributos e registra os diagnósticos de contorno. Diagnósticos por centros não provam topologia e seu alinhamento é heurístico; a validade estrutural/física do dataset permanece uma barreira separada.

Importar os módulos ou consultar `--help` não lê arquivos científicos, importa PyTorch/scikit-learn ou ajusta modelos. A leitura real de Parquet requer PyArrow; a exportação de arrays requer NumPy. Não há instalação automática.

## Campanhas permanecem separadas

`--execute` é uma ação explícita, exige `--output` apontando para diretório novo fora dos originais e continua dependente de autorização científica de protocolo/orçamento. R1 não executa essa opção. Os scripts restringem ajustes aos casos `success`, conforme a referência canônica; não convergidos permanecem no inventário e na validação, fora do ajuste. Não há opção implícita para misturar snapshots e médias.

A v4 conserva cinco partes de **desenvolvimento**, sem acessar o teste para ajustar modelos. Esse procedimento e sua população diferem dos experimentos históricos com não convergidos e da referência fixa S3. O esqueleto refatorado não é uma autorização ou validação do protocolo E2. A seleção do checkpoint permanece baseada na validação; resultados são identificados como `development_selected_checkpoint`, sem regra automática de empate ou afirmação de generalização independente.

Os modelos geométricos atuais exigem Mach e ângulo constantes, verificados nos casos selecionados. Variação dessas condições requer condicionamento e protocolo próprios. Comprimentos e integração usam a corda e o ângulo de cada caso. A seed histórica S3 `202604`, as partições e `c0015` não são reescritos.

## Inferência e rastreabilidade

- A exportação compartilhada permite ausência completa de Cp para inferência e rejeita rótulos parciais, valores não finitos e entradas incompletas em qualquer nó.
- O diagnóstico aceita ambos os sentidos de percurso com normais externas consistentes; geometria não finita produz falha explícita.
- O artefato GPR contém modelo, ordem de atributos, limites de transformação, alvo e condições. `kriging.predict_cl` reaplica essa transformação e confere o domínio operacional.
- Checkpoints GNN contêm `state_dict`, normalizações de nós/arestas/Cp, layout de atributos, configuração, melhor época, IDs de treino/validação, hashes e ambiente. `load_checkpoint` e `predict_cp` conferem o contrato para inferência sem rótulos.
- Os pesos antigos sem pré-processamento não são completados por suposição; o carregador rejeita formatos sem o novo contrato. Guardam-se originais e respectivas evidências separadamente.
- Estatísticas são ajustadas apenas no treino de cada parte. Sua implementação agora é explícita na biblioteca padrão, com cálculo amostral e tratamento de variância nula; pequenas diferenças numéricas em relação ao cálculo float32 histórico não implicam reprodução das métricas anteriores.
- O diretório de saída não pode existir previamente nem ficar sob o dataset. Hashes e metadados são privados quando incluem IDs ou caminhos de dados restritos; não adicionar artefatos de execução ao Git por rotina.

## Verificação e limites

Executar `python -m unittest discover -s tests -v`, com `PYTHONPATH=src`, e `python -m compileall -q src tests scripts`. Os testes provam bloqueio antes de ML/saídas, importação sem efeitos, preservação de partições, contratos de inferência, normalização e regressões geométricas. Os testes de arrays requerem NumPy; um teste opcional verifica forward e checkpoint com pesos **não treinados** se PyTorch/PyG já estiverem presentes.

Na preparação local de R1 não há PyTorch/PyG/scikit-learn no runtime utilizado. O teste opcional de forward/checkpoint não substitui uma validação real com essas bibliotecas e dados; sua execução fica pendente de ambiente autorizado. Nenhum resultado preditivo ou ganho científico é produzido por esta PR.
