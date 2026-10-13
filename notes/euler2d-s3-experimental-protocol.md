# S3 — protocolo experimental de baselines e GNN

## Unidade e particionamento

Cada observação experimental é um `case_id`. Nós da superfície não são
observações independentes. O protocolo usa somente os casos `success` e lê as
partições existentes no `split_manifest.json`: 31 treino, 7 validação e 8
teste. O caso `c0015` permanece no teste.

## Entradas e alvos

`FeatureSpec` define explicitamente as entradas pré-solver:

```text
m, p, t, mach_inf, alpha_deg
```

Os alvos de referência são `CL` e `CD`. `Cp`, pressão superficial e
coeficientes calculados a partir da solução não podem ser selecionados como
entrada. A seleção é verificada em tempo de execução para impedir vazamento.

## Modelos

1. `train_mean`: preditor de referência constante, ajustado somente no treino.
2. `ridge_geometry`: regressão linear regularizada, com padronização calculada
   somente no treino e solução determinística sem `scikit-learn`.
3. `surface_gnn`: pequena rede opcional em PyTorch, com mensagem média entre
   vizinhos de contorno e pooling global. PyTorch não é dependência obrigatória;
   quando ausente, a execução registra a inviabilidade do ambiente em vez de
   produzir resultado artificial.

As métricas são MAE e RMSE por alvo e por partição. Seeds, features, alvos,
contagens, disponibilidade da GNN e tempo são gravados pelo CLI.

## Continuidade geométrica

Para cada aresta de contorno, o protocolo mede a distância entre centros das
faces consecutivas e a compara ao comprimento dos segmentos. Como o Parquet
não contém endpoints nem conectividade volumétrica, esse é um diagnóstico de
continuidade, não uma prova de que duas faces compartilham uma aresta.

O sinal da área orientada pelos centros é registrado somente como diagnóstico.
`contour_index` define uma ordem de exportação dirigida; essa convenção não é
interpretada como orientação física, sentido do escoamento ou normal externa.

## Execução reproduzível

```powershell
$env:PYTHONPATH = "src"
python scripts/run_s3_experiment.py C:\caminho\dataset_euler_2d --output s3-results.json
```

O arquivo de resultados é um artefato local e não inclui os arquivos Parquet.

## Critério de interpretação

Os resultados são exploratórios. Diferenças pequenas, especialmente em apenas
oito casos de teste, não sustentam superioridade científica. Se a GNN não for
executável no ambiente documentado, a comparação deve permanecer entre os
baselines e a limitação deve ser reportada.
