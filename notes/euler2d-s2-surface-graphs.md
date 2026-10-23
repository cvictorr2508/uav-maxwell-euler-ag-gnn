# S2 — representação mínima de grafos de superfície

## Escopo

O módulo `uav_euler2d.graph` constrói um grafo de contorno a partir de um
único arquivo Parquet de superfície. Cada face exportada é um nó, com
`case_id`, `geometry_id`, `entity_id`, coordenadas, normal, comprimento e
todos os atributos físicos originais preservados no campo `attributes`.

As arestas são somente as adjacências consecutivas da ordem
`contour_index`, incluindo a ligação de fechamento entre a última e a
primeira face. Essa conectividade é de **contorno**. Não há arestas
volumétricas: o dataset não fornece conectividade entre células, e o módulo
não a reconstrói por distância, coordenadas ou qualquer outra heurística.

Cada grafo registra `source_parquet` relativo à raiz do dataset, mantendo a
rastreabilidade até o arquivo de origem. Casos com o mesmo `geometry_id`
continuam sendo casos distintos, identificados pelo próprio `case_id`.

## Exemplo reproduzível

Com o dataset local disponível:

```powershell
$env:PYTHONPATH = "src"
python scripts/inspect_surface_graph.py C:\caminho\dataset_euler_2d c0015
```

O resumo JSON informa o número de nós, arestas de contorno, zero arestas
volumétricas, o arquivo Parquet de origem e os primeiros nós para inspeção.

## Limitações

O grafo não representa células do domínio, vizinhança volumétrica, faces
internas ou uma malha completa. A construção é adequada apenas à
representação mínima da superfície efetivamente exportada nesta Sprint.
