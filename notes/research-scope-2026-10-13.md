# Contrato científico e operacional — realinhamento de 13/10/2026

**Projeto:** UAV | Maxwell–Euler & Geometric Deep Learning · **Programa:** PPGEE, Universidade de Brasília · **Pesquisador:** João Pedro · **Situação:** proposta de realinhamento para revisão na PR; não constitui validação de resultados preexistentes.

## Decisão de escopo

A pesquisa examina matemática das equações de Euler e Maxwell, Álgebra Geométrica, propriedades das representações em grafos e reprodutibilidade de software científico. Suas atividades computacionais assistidas utilizam **problemas acadêmicos independentes** e bases públicas ou sintéticas adequadas, sem aplicações militares e sem construir uma cadeia operacional de redução de detectabilidade ou otimização conjunta de desempenho aerodinâmico e resposta de retorno eletromagnético.

A designação UAV refere-se genericamente a aeronaves não tripuladas; **não** determina tipo de configuração, missão ou plataforma experimental. O objeto da dissertação é a metodologia matemática e computacional. O conteúdo pedagógico do eBook permanece separado dos resultados específicos da dissertação.

## Perguntas verificáveis

**Q1 — Representação matemática:** estabelecer equações, convenções, hipóteses e equivalências prováveis ou demonstradas de Maxwell/Euler em Álgebra Geométrica, preservando tensores e formas conservativas quando necessários.

**Q2 — Representação geométrica:** comparar representações convencionais de malha/grafo com atributos derivados de AG em problemas acadêmicos; separar identidade matemática, invariância e equivariância efetivamente implementada.

**Q3 — Validação computacional:** comparar baselines, qualidade das entradas, desempenho preditivo, sensibilidade a remalhamento/condições, métricas físicas, recursos de CPU/GPU e reprodutibilidade. Nenhum ganho é presumido.

## Critérios para experimentação

1. Utilizar casos canônicos verificáveis (escoamentos 2D, malhas, testes de álgebra, propagação eletromagnética) e dados licenciados para o uso pretendido.
2. Registrar geometria, condições, discretização, solver, versão, unidades, convergência, localização dos campos e limites de validade.
3. Distinguir **erro de discretização**, **erro de modelagem** e **erro do surrogate**, onde mensuráveis.
4. Proteger o conjunto de teste por geometria; seed de referência 42, parâmetros versionados e variantes de sensibilidade declaradas.
5. Preservar a localização nativa de pressão e conectividade; a integração de pressão exige condições e convenções físicas verificadas.
6. Avaliar multifidelidade apenas quando os níveis aproximarem a mesma grandeza em condições compatíveis e tiverem custos observados.

## Estado dos artefatos e rastreabilidade

As antigas versões do código, capítulos, decisões e discussões permanecem **no histórico Git**, mas não são incorporadas automaticamente ao novo contrato científico. A PR #16 segue como **draft legado**, com componentes genéricos de AG e grafo potencialmente reutilizáveis e conteúdo aplicativo pendente de revisão; não deve ser incorporada sem adaptação formal. O estudo S1 e seus dados eventualmente obtidos conservam valor histórico, mas suas conclusões só se aplicam aos experimentos efetivamente verificados.

O contrato de dados Euler 2D é um **schema proposto**, condicionado à inspeção das saídas do solver. A presente refatoração textual não altera os resultados, arquivos brutos, nem prova equivalência numérica ou ganhos de computação.

## Governança

O orientador aprova hipóteses, mudanças metodológicas e publicação. João Pedro mantém responsabilidade intelectual por simulações e pesquisas atribuídas. ChatGPT apoia discussão e revisão; Codex implementa código e testes; GitHub constitui fonte de verdade dos artefatos versionados.

**Critérios de aceite desta refatoração:** identidade e finalidade acadêmicas coerentes; eliminação de referências ativas à aplicação anterior nas fontes correntes; referências bibliográficas pertinentes; Quarto validado; histórico preservado; ausência de alteração automática em `main` e ausência de merge da PR #16. O material deverá ser revisado e aprovado antes de qualquer publicação.
