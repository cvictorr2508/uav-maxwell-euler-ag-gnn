# Checklist de verificação do solver Euler 2D — S1

**Projeto:** UAV | Maxwell–Euler e Aprendizado em Grafos · **Responsável pela campanha:** João Pedro · **Estado:** modelo de preenchimento, sem afirmar verificações realizadas · **Contrato:** `notes/euler2d-dataset-contract.md` (v0.1).

> Marcar cada item como **verificado**, **não verificado**, **não disponível** ou **não aplicável**, com evidência (log, arquivo, captura de configuração, comando, versão ou checksum). Não preencher lacunas por inferência. As caixas abaixo iniciam desmarcadas.

## A. Identificação do solver e formulação física

- [ ] Nome, versão, fonte/documentação e procedimento de execução do solver registrados.
- [ ] Equações efetivamente resolvidas confirmadas: Euler compressível invíscido 2D, ou outra formulação documentada.
- [ ] Gás e equação de estado identificados; \(\gamma\), constante do gás, unidades e convenções de energia informados.
- [ ] Solver nodal versus cell-centered e tipo de volumes/elementos identificados.
- [ ] Esquema de fluxo, ordem espacial, reconstrução, limiter e tratamento de choques identificados.
- [ ] Integração temporal/pseudo-temporal, CFL e estratégia de inicialização documentados.
- [ ] Condição de parede e condição de campo distante especificadas; extensão do domínio e tratamento de bordo de fuga conhecidos.
- [ ] Sistema de coordenadas, orientação de normal da superfície e sentido positivo de \(\alpha\) documentados.

**Evidências:** inserir aqui referências a arquivos, versão, parâmetros, hashes ou logs.

## B. Geometria e condições do caso canônico

- [ ] Parâmetros \(m,p,t\) identificados; faixa adotada e hipótese de gerador NACA de quatro dígitos confirmadas ou corrigidas.
- [ ] Versão do gerador, comprimento de corda, tratamento de bordo de fuga e hash/ID da geometria informados.
- [ ] Mach de campo livre registrado (valor histórico \(M_\infty=0{,}8\), sujeito a confirmação no rerun).
- [ ] Ângulo de ataque \(\alpha\) registrado, mesmo quando fixo.
- [ ] Pressão \(p_\infty\), temperatura \(T_\infty\), densidade \(\rho_\infty\), velocidade \(V_\infty\) e \(\gamma\) registrados ou calculáveis a partir de informações rastreáveis.
- [ ] Pressão dinâmica \(q_\infty=\rho_\infty V_\infty^2/2\) e corda/área de referência documentadas.
- [ ] Um caso canônico executado e passível de reprodução com as configurações fornecidas.

**ID de geometria:** __________  **ID de caso:** __________  **Comando/config:** __________

## C. Malha e estudo de convergência

- [ ] Gerador, versão, conectividade, tipos de célula, parâmetros da malha e extensão do domínio registrados.
- [ ] Quantidade de nós, elementos, faces de contorno e métricas de qualidade reportadas.
- [ ] Orientação, fechamento, identificadores e localização de centros das faces de parede verificados.
- [ ] Ao menos uma geometria canônica com malhas grossa, intermediária e de referência planejadas/executadas e registradas como tal.
- [ ] Ampliar o estudo para **4–6 geometrias representativas** da faixa de \(m,p,t\), quando viável, incluindo regimes críticos.
- [ ] Em cada malha, comparar \(C_L,C_D,C_p(s)\), posição de choque quando houver, iterações, resíduos e histórico dos coeficientes.
- [ ] Comparar `wall_time_s`, CPU-hours, memória e ambiente de processamento.
- [ ] Definir tolerâncias de aceitação e justificar nível de referência por comportamento numérico, não pelo número de células.

**Não pressupor que 200 mil células representem uma referência convergida.** Se o estudo não permitir estimativa rigorosa do erro assintótico, explicitar essa limitação em vez de declarar independência de malha.

## D. Convergência, coeficientes e falhas

- [ ] Resíduos iniciais/finais e critério de parada preservados.
- [ ] Histórico de \(C_L,C_D\) por iteração ou janela final exportado.
- [ ] Convenção de \(C_L,C_D,C_m\), eixos de sustentação/arrasto e ponto de referência do momento documentados.
- [ ] Determinar o significado de \(C_D\) no Euler invíscido (forças de pressão e eventuais contribuições numéricas; sem atrito viscoso).
- [ ] Códigos de status e `failure_code` disponíveis para execuções inválidas ou não convergidas.
- [ ] Reinvestigar falhas do CSV histórico (`id=7` e `id=22`) e registrar diagnóstico com evidência, se reproduzíveis.
- [ ] Não misturar `ERRO` ou outros textos em colunas numéricas; valores indisponíveis como `NaN` com status explícito.

## E. Pressão superficial, \(C_p\) e integração de forças

- [ ] Confirmar se pressão e \(C_p\) são exportáveis em nós, células ou faces de parede; registrar localização **nativa**.
- [ ] Se cell-centered, verificar exportação da pressão reconstruída nas faces de contorno e preservar indicação do método.
- [ ] Exportar identificador de entidade, `case_id`, coordenadas, `x/c,y/c,s/c`, norma/orientação, comprimento de face e conectividade.
- [ ] Preservar a ordenação do contorno, identificação de extradorso/intradorso e eventuais componentes separados.
- [ ] Preservar pressão dimensional e fatores usados em \(C_p=(p-p_\infty)/q_\infty\).
- [ ] Inspecionar valores de \(C_p\) em extradorso/intradorso, especialmente em regiões transônicas ou de choque.
- [ ] Definir quadratura e comparar integração de pressão de parede com \(C_L,C_D\) exportados, usando a convenção do solver.
- [ ] Registrar limites de tolerância e possíveis causas de discrepâncias (interpolação, normais, unidades, forças, convergência, discretização).

A força seccional (por unidade de envergadura) utiliza a normal externa ao corpo e a integral \(\mathbf F'=-\oint_\Gamma p\mathbf n\,ds\); sua forma adimensional em termos de \(C_p\) requer contorno fechado, corda de referência e convenções consistentes. A tarefa \(G\to C_p\to(C_L,C_D)\) só será habilitada quando esses dados e testes estiverem disponíveis.

## F. Campo volumétrico para estudos futuros (opcional no piloto)

- [ ] Confirmar exportação de \(\rho,u,v,p,E\) ou \([\rho,\rho u,\rho v,\rho E]\), com unidades, topologia e localização das incógnitas.
- [ ] Verificar preservação de faces/células e do operador/fluxo discreto se o objetivo incluir resíduos de Euler.
- [ ] Definir subconjunto representativo de casos para armazenamento volumétrico (VTU ou formato equivalente rastreável).
- [ ] Documentar memória, espaço de armazenamento e restrições de distribuição.

**Nota:** \(C_p\) superficial não permite reconstruir sozinho o campo de Euler nem calcular vorticidade volumétrica. Resíduos de operadores distintos não são diretamente comparáveis sem justificativa.

## G. Pacote-piloto a disponibilizar para S2/PR #16

Disponibilizar **um caso canônico válido** (podendo incluir mais de uma malha) com os seguintes artefatos e um índice que ligue seus IDs:

- [ ] Registro `cases.csv` (ao menos `case_id,geometry_id,mesh_id`, parâmetros, condição física, versão e status).
- [ ] Coordenadas e conectividade do contorno, normais e identificação da localização nativa das variáveis.
- [ ] Pressão superficial e/ou \(C_p\), com referência de normalização.
- [ ] Malha e metadados de malha, incluindo orientação e limites do domínio.
- [ ] Arquivo de configuração/comandos e logs de convergência do solver.
- [ ] Coeficientes globais \(C_L,C_D\) e respectivas convenções.
- [ ] Recursos computacionais e hashes dos arquivos.
- [ ] Opcional: campo volumétrico em uma malha para futura GNN informada por física.
- [ ] Nota sobre licença/compartilhamento e canal de transferência, evitando colocar dados extensos ou restritos no repositório.

**Entrega S1 considerada verificável quando:** (a) o caso canônico puder ser reproduzido por configuração explícita; (b) os coeficientes e a pressão estiverem documentados; (c) a conectividade e a localização das grandezas forem inspecionáveis; (d) exista evidência de convergência ou uma limitação objetiva registrada. Não é necessário concluir a campanha completa para habilitar S2.

## H. Critérios de entrada para S2 e delimitação de responsabilidades

**Ação da equipe de desenvolvimento após receber os arquivos:** inspecionar tipos, unidades, chaves, conectividade, orientação e sentido das normais; documentar divergências do contrato v0.1; planejar adaptador multi-arquivo para o leitor de contorno da PR #16; construir grafo e manifesto; testar consistência \(C_p\)–força; assegurar split por `geometry_id`, seed 42 e CI.

**Não realizar durante S0:** alterar o pacote Python em `src/`, gerar falsos resultados de solver, classificar níveis de fidelidade apenas pelo número de células, declarar a PR #16 pronta para merge ou promover trabalhos experimentais às branches estáveis.

**Quadro de decisão a preencher:** responsável ______; data ______; solver/versão ______; caso canônico ______; metadados completos? ______; \(C_p\) disponível? ______; conectividade disponível? ______; S1 aprovado? ______; pendências ______.

**Documentos relacionados:** `notes/euler2d-dataset-contract.md`, `notes/editorial-scientific-guidelines.md`, PR #16.
