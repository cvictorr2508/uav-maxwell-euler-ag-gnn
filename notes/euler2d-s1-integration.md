# Sprint S1 — Integração e validação científica

Esta sprint fornece um loader somente leitura e validações independentes para o
dataset Euler 2D derivado. Os dados científicos não fazem parte do repositório.

## Política de status

- `success`: referência determinística inicial.
- `non_converged`: preservado para análise de sensibilidade; a média e a
  meia-amplitude da janela final continuam sendo metadados de incerteza.
- `failed`: preservado no registro, sem alvo numérico e fora das partições.

Com o manifesto original, o filtro `success` produz 31 casos de treino, 7 de
validação e 8 de teste. O manifesto não é reescrito.

## Validações

`validate_dataset` verifica identificadores, estados, referências entre casos e
superfícies, contornos, normais, valores finitos, relação

\[
C_p=(p-p_\infty)/q_\infty
\]

e a integração independente da pressão superficial. As tolerâncias padrão são
`1e-4` absoluto para `Cp`, `1e-9` para fechamento e normais, `0,1%` relativo
para `CL` e `2%` para `CD`, com tolerâncias absolutas configuráveis para valores
próximos de zero.

A ordem do contorno é usada somente como ordem documentada das faces. O loader
não inventa conectividade da malha de volumes finitos.

## Dependência local

CSV e JSON usam a biblioteca padrão. A leitura dos Parquet requer `pyarrow`;
quando ausente, o loader falha explicitamente e não substitui os dados por uma
representação aproximada.

## Execução local

Com o pacote científico fora do repositório:

```text
python scripts/validate_euler2d.py <caminho>/dataset_euler_2d --json
```

O comando retorna código de saída diferente de zero quando uma validação
estrutural ou física falha. Avisos de `non_converged` não são convertidos em
erro: eles registram a diferença entre a superfície final exportada e a média
da janela usada como alvo.
