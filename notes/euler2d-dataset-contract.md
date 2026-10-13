# Contrato preliminar do dataset Euler 2D — S0

**Identificador:** `euler2d-contract-v0.1` · **Situação:** proposta para validação com o responsável pelas simulações · **Projeto:** UAV | Maxwell–Euler e Aprendizado em Grafos · **Etapa:** estudo aerodinâmico bidimensional.

> Este documento define um **contrato-alvo**, não um relato de arquivos já entregues ou testados. O nome do solver, as variáveis exportáveis, a localização nativa das incógnitas, as convenções de forças e a configuração numérica dependem de confirmação com João Pedro. Não atribuir valores ainda desconhecidos ao solver.

## 1. Finalidade, escopo e fontes técnicas

A organização distingue (i) a configuração geométrica, (ii) a discretização e (iii) a execução físico-numérica. O objetivo é produzir simulações rastreáveis, dados de superfície utilizáveis por GNNs e uma base para caracterização posterior de fidelidades. Uma mesma geometria pode ter diversas malhas, condições operacionais ou níveis de fidelidade, mas deve manter uma identidade estável.

Este contrato incorpora criticamente as recomendações do relatório interno *Refatoração do Dataset de Simulações Euler 2D para Treinamento de GNN* (orientação dirigida a João Pedro) e os cuidados matemáticos do documento interno *Mecânica de Fluidos em Álgebra Geométrica* (07/10/2026). São documentos de referência do projeto; suas propostas ainda precisam ser confrontadas com a implementação efetiva.

O primeiro arquivo histórico `resultados.csv` foi descrito como contendo 51 configurações, com colunas `id,m,p,t,cl,cd`; 49 respostas válidas e erros textuais nos casos 7 e 22. Essa descrição provém do diagnóstico anterior e **não substitui nova auditoria do CSV original**. Como não há coordenadas, conectividade, distribuição de pressão ou campos completos nesse arquivo, ele não satisfaz o contrato para uma GNN de malha. Nenhuma nova simulação é considerada concluída por este documento.

## 2. Identificadores e relações entre entidades

| Campo | Escopo / significado | Regra |
| --- | --- | --- |
| `geometry_id` | Geometria física parametrizada | Persistente entre malhas e condições; idealmente associado ao hash dos parâmetros e da versão do gerador. |
| `mesh_id` | Discretização de uma `geometry_id` | Identifica conectividade, versão da malha, resolução e parâmetros de geração. |
| `case_id` | Execução individual do solver | Chave única para geometria, malha, condição, configuração numérica e, se aplicável, repetição. |
| `fidelity_id` | Nível físico-numérico caracterizado | Não atribuir somente com base no número de células; pode permanecer provisório no piloto. |
| `run_id` | Tentativa de execução/reprocessamento | Quando houver repetição, preservar logs e associar o caso à tentativa utilizada. |

Relação esperada: `geometry_id` → várias `mesh_id`; pares de geometria/malha → vários `case_id`. Todos os casos da mesma geometria devem pertencer à **mesma partição** quando o objetivo for generalização para geometrias inéditas. Não dividir por linha, nó, face, malha ou condição.

## 3. Domínio geométrico e planejamento experimental

O vetor geométrico inicialmente declarado é \(\mathbf d=[m,p,t]^T\), com \(m\) representando curvatura máxima, \(p\) a posição de máxima curvatura e \(t\) a espessura relativa. Os limites propostos são \(m\in[0,0.04]\), \(p\in[0.20,0.60]\), \(t\in[0.08,0.16]\). A hipótese de parametrização NACA de quatro dígitos precisa ser confirmada junto à fórmula e à versão do gerador geométrico. Documentar convenção do bordo de fuga, corda de referência, orientação dos pontos e eventuais restrições adicionais.

O novo Design of Experiments (DoE) será **planejado**, não uma reclassificação retrospectiva das 51 geometrias históricas. LHS maximin ou Sobol são candidatos, com `seed=42` para operações estocásticas controláveis; a escolha, o tamanho amostral e a alocação por fidelidade dependem da verificação numérica e do orçamento de simulação. O conjunto final de teste deve ser congelado por geometria antes de qualquer enriquecimento adaptativo. Proporções de referência iniciais: 70%/15%/15%, configuráveis.

## 4. Organização recomendada

```text
dataset_euler_2d/
  cases.csv
  meshes/mesh_metadata.json
  surface/case_<case_id>.parquet
  volume/case_<case_id>.vtu           # opcional no piloto
  dataset_manifest.json
  split_manifest.json               # gerado pela preparação
```

O arquivo `cases.csv` reúne uma linha por **execução**; `surface/` preserva valores associados a entidades de contorno; `volume/` armazena campos em células/nós de volume quando exportados. A conectividade completa e a localização física das variáveis devem ser acessíveis de forma inequívoca por arquivos próprios ou referências às malhas. Não converter dados cell-centered em dados nodais sem registrar a transformação; preservar preferencialmente os valores nativos.

### 4.1. `cases.csv` — registro por execução

| Família | Campos canônicos propostos | Observações |
| --- | --- | --- |
| Identificação | `case_id`, `geometry_id`, `mesh_id`, `fidelity_id`, `run_id` | IDs inequívocos, ligações verificáveis. |
| Geometria | `m`, `p`, `t`, `chord_ref_m`, `geometry_generator_version` | Guardar também hash dos parâmetros/gerador no manifesto. |
| Condição de voo | `mach_inf`, `alpha_deg`, `rho_inf_kg_m3`, `p_inf_Pa`, `T_inf_K`, `gamma`, `q_inf_Pa` | Mach 0,8 é condição histórica informada; novo valor e ângulo de ataque ainda precisam ser confirmados. |
| Resultado global | `CL`, `CD`, `Cm` (se disponível) | Coeficientes adimensionais e referência de força/momento explícita. `L/D` é derivado de `CL/CD`, não alvo independente. |
| Execução | `status`, `failure_code`, `solver`, `solver_version`, `solver_config_id` | Falhas têm `CL/CD = NaN`, nunca a string `ERRO` em colunas numéricas. |
| Convergência | `iterations`, `final_residual`, `convergence_metrics_ref` | Salvar critérios e histórico de forças/resíduos em artefato associado. |
| Recursos | `wall_time_s`, `cpu_hours`, `peak_memory_bytes` | Registrar hardware, número de processos/threads e artefatos brutos no manifesto. |

O contrato distingue **campos-alvo** daqueles disponíveis no piloto. Quando uma grandeza ainda não puder ser exportada, registrar sua ausência e o motivo, sem gerar valores artificiais. Definir um vocabulário controlado para `status` (por exemplo, `success`, `failed`, `non_converged`, `invalid_mesh`) e `failure_code`; documentar a semântica definitiva com o solver.

### 4.2. `surface/case_<case_id>.parquet` — observáveis de parede

**Chaves:** `case_id` e `entity_id` (identifica nó ou face); `native_location` (`node`/`boundary_face`/`cell`), `surface_component_id` e `side` (`upper`/`lower` quando aplicável).

**Geometria:** `x_over_c`, `y_over_c`, `s_over_c`, `normal_x`, `normal_y`, `segment_length_m` (para faces), orientação, ordem ou conectividade explícita; `node_start_id` e `node_end_id` quando a representação for por face/segmento. Coordenadas dimensionais e localização do centro da face ou dos nós devem ser identificadas quando necessárias.

**Campo:** `pressure_Pa`, `Cp` e referência de normalização; metadados do método de reconstrução/interpolação, se utilizados.

Para \(\rho_\infty\) (densidade), \(V_\infty\) (módulo da velocidade) e \(p_\infty\) (pressão de campo livre), verificar

\[
q_\infty=\tfrac12\rho_\infty V_\infty^2,\qquad
C_p=(p-p_\infty)/q_\infty.
\]

O valor nativo do solver deve ser guardado no local em que é calculado ou reconstruído. Em formulações por volumes finitos cell-centered, preservar a pressão de célula quando disponível e exportar a pressão reconstruída na **face de parede** para a integração. Em formulações nodais, preservar os valores nos nós. Não confundir o identificador de nó com a ordenação de um contorno fechado; a conectividade, especialmente em bordo de fuga e múltiplas componentes, precisa ser explícita ou verificavelmente reconstruível.

### 4.3. `volume/case_<case_id>.vtu` — campos opcionais no piloto

Em um subconjunto representativo, preservar geometria, conectividade e localização de \(\rho,u,v,p,E\) ou das variáveis conservativas \(U=[\rho,\rho u,\rho v,\rho E]^T\), com unidades e significado de energia explícitos. Campos volumétricos e operadores discretos são necessários para estudar vorticidade física, termo baroclínico ou resíduos de Euler. **Somente \(C_p\) superficial não caracteriza o campo completo de Euler**. O formato VTK/VTU é preferencial para malhas não estruturadas; Parquet pode ser usado quando a topologia e os metadados estiverem preservados sem ambiguidade.

### 4.4. `meshes/mesh_metadata.json` — discretização

Registrar `mesh_id`, `geometry_id`, número de nós, número de células, tipos de elementos, orientação/conectividade de contorno, extensão do domínio, gerador e parâmetros, versão, métricas de qualidade, localização nativa das incógnitas, arquivos associados e seus hashes. Documentar se existe uma malha de volume reutilizável entre casos e como cada caso a referencia.

## 5. Relações de consistência física

Para um contorno fechado \(\Gamma\) de aerofólio 2D, com normal unitária externa ao **corpo** \(\mathbf n\), corda de referência \(c>0\) e pressão dinâmica \(q_\infty\), a força de pressão por unidade de envergadura é

\[
\mathbf F'=-\oint_\Gamma p(s)\mathbf n(s)\,ds.
\]

A força adimensional é

\[
\mathbf C_F=\frac{\mathbf F'}{q_\infty c}
=-\frac{1}{c}\oint_\Gamma C_p(s)\mathbf n(s)\,ds,
\]

onde a segunda igualdade pressupõe contorno fechado e integração consistente, de modo que a pressão constante de referência não contribua para a força resultante. Os coeficientes \(C_L,C_D\) decorrem das projeções nos eixos de sustentação/arrasto fixados pelo solver; não identificar automaticamente \((C_{F,x},C_{F,y})\) com \((C_D,C_L)\) sem conhecer a definição de incidência e a orientação de eixos.

Na implementação discreta, usar pressão e normais **das faces** quando o solver fornece valores por face. Documentar quadratura, tratamento do bordo de fuga, sentido das normais e diferença para integração nodal. Definir tolerâncias de comparação após verificar exatidão numérica e a convenção de \(C_L\)/\(C_D\) do solver. Em Euler invíscido, \(C_D\) não representa arrasto de atrito viscoso.

## 6. Verificação de malha, fidelidade e regime transônico

Antes da campanha, verificar um caso canônico e comparar **4–6 geometrias representativas** em malhas grossa, intermediária e de referência, quando o solver permitir. Medir \(C_L\), \(C_D\), \(C_p(s)\), posição de choque quando houver, resíduos, histórico dos coeficientes, `wall_time_s`, CPU-hours e memória. Com Mach histórico 0,8, o caráter transônico local e as ondas de choque devem ser examinados, não presumidos em todas as geometrias.

A definição de `fidelity_id` será posterior à avaliação do erro de discretização, convergência, tratamento de choque, condições de contorno e recursos computacionais. Ter aproximadamente 200 mil células **não demonstra** fidelidade de referência. Não chamar a comparação de “independência de malha” sem evidência dos indicadores examinados.

## 7. Manifests e validações automáticas propostas

**`dataset_manifest.json`**: `schema_version`, fonte e licença, `created_at`, responsável, versão do solver, commit dos scripts/gerador, configurações e identificadores/hash dos arquivos brutos, mapeamentos de campos, unidades, transformações realizadas, dados não disponíveis, parâmetros do DoE, níveis de fidelidade e recursos.

**`split_manifest.json`**: `seed=42`, proporções parametrizáveis, IDs de geometria por conjunto, versão da amostra e política de congelamento do teste final. Remalhamentos, condições adicionais e fidelidades de uma geometria acompanham a partição dessa mesma geometria.

**Testes mínimos:** (i) unicidade e integridade referencial; (ii) tipos numéricos e valores finitos onde obrigatórios; (iii) domínio de \(m,p,t\); (iv) fechamento/orientação/conectividade válidos e normais coerentes; (v) coerência entre \(C_p\), pressão e \(q_\infty\); (vi) aproximação da integral de pressão aos coeficientes globais dentro de tolerâncias justificadas; (vii) dados brutos preservados e transformações rastreáveis; (viii) nenhuma geometria em mais de uma partição; (ix) registros de falhas explícitos, sem alvos fabricados.

Os arquivos extensos de CFD não serão versionados automaticamente no GitHub. O repositório deve conter scripts, schema, manifestos adequados à publicação e amostras sintéticas explicitamente rotuladas, observando licença e permissões dos dados.

## 8. Política de entrega em etapas

| Marco | Evidência exigida | Situação atual |
| --- | --- | --- |
| **S0 — contrato** | Especificação v0.1 e checklist disponíveis para revisão | Documental, independente do rerun. |
| **S1 — solver** | Um caso canônico com metadados, pressão superficial, malha e logs reproduzíveis; início do estudo de malhas | Aguardando confirmação e artefatos do aluno. |
| **S2 — pipeline/PR #16** | Dados-piloto lidos por adaptador, grafo validado, integração física e testes de CI | Só após os arquivos reais. |
| **S3 — campanha** | DoE formal, simulações rastreáveis, hierarquia numérica caracterizada | Futuro; quantidade não definida. |

O código atual da PR #16 aceita CSV por nó de **contorno ordenado** (`configuration_id,node_id,x,y`); o contrato ora proposto admite arquivos por caso e por superfície. A adaptação do pacote Python **não integra S0** e deverá ser feita na PR #16 depois da inspeção das saídas efetivas do solver.

## 9. Pendências para homologar a versão 1.0

Confirmar: software/versão e formulação numérica; ângulo de ataque; valores de \(p_\infty,\rho_\infty,T_\infty,\gamma\); normalização dos coeficientes; definição de \(C_D\); posição das incógnitas; conectividade e convenção das normais; formato de exportação de \(p/C_p\); variáveis volumétricas acessíveis; parâmetros de malha e convergência; causa das falhas históricas; orçamento e número de casos. Decisões permanecem abertas até receber evidência do solver.

**Documentos relacionados:** `notes/euler2d-solver-validation-checklist.md`, `notes/editorial-scientific-guidelines.md`; PR #16 `feature/ch5-2d-data-ga-pipeline`.
