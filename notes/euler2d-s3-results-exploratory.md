# S3 — resultados preliminares exploratórios

Execução local em 13/10/2026, com seed `202604`, usando o dataset Euler 2D
local. Os arquivos científicos originais não foram adicionados ao Git.

## Integridade e geometria

- validação do dataset: passou, 0 erros;
- 60 casos totais, 54 casos com superfície;
- casos convergidos por partição: treino 31, validação 7, teste 8;
- `c0015` permaneceu no teste;
- oito grafos de teste passaram o diagnóstico de continuidade;
- em `c0015`, 500 arestas de contorno e razão máxima
  centro-adjacente/comprimento de segmento aproximadamente `1.000014`;
- a área orientada dos centros foi registrada somente como diagnóstico; não é
  uma orientação física.

## Baselines

Entradas exclusivamente pré-solver:
`m`, `p`, `t`, `mach_inf`, `alpha_deg`, `chord_ref_m`.
Alvos: `CL` e `CD`. Cada caso é uma observação; faces não são amostras
independentes.

| Modelo | Partição | N | MAE CL | RMSE CL | MAE CD | RMSE CD |
|---|---:|---:|---:|---:|---:|---:|
| média do treino | treino | 31 | 0.15035 | 0.17961 | 0.02696 | 0.03197 |
| média do treino | validação | 7 | 0.14790 | 0.17123 | 0.01549 | 0.02185 |
| média do treino | teste | 8 | 0.16352 | 0.18885 | 0.02466 | 0.02729 |
| ridge geométrico | treino | 31 | 0.02992 | 0.03703 | 0.00206 | 0.00269 |
| ridge geométrico | validação | 7 | 0.03138 | 0.03311 | 0.00112 | 0.00157 |
| ridge geométrico | teste | 8 | 0.02588 | 0.03020 | 0.00264 | 0.00299 |

Os números são exploratórios. A amostra de teste tem apenas oito casos e não
permite concluir superioridade geral nem justificar seleção de hiperparâmetros.

## GNN

O código contém uma pequena rede opcional de mensagem média sobre as arestas de
contorno, com atributos geométricos dos nós e pooling global. PyTorch não está
instalado no ambiente mínimo utilizado para esta execução; a GNN foi registrada
como indisponível e não foi substituída por outro modelo.

## Limitações

O dataset não fornece endpoints das faces nem conectividade volumétrica. A
continuidade verificada é, portanto, uma evidência geométrica baseada em
centros e comprimentos, não uma prova topológica. A etapa seguinte deve avaliar
se a instalação controlada de PyTorch e o número reduzido de casos permitem uma
comparação interpretável, sem usar o teste para decisões de modelo.
