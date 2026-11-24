# R2 Regras para liberar a comparação experimental

Versão `r2-euler2d-v1`, 24/11/2026. Este checklist acompanha o [protocolo](../notes/r2-comparative-protocol.md) e a [configuração](../configs/experiments/r2-kriging-gnn-v1.json). Todas as condições de execução abaixo permanecem abertas nesta entrega. Preparar as PRs e o protocolo não inicia nenhum ajuste.

## Documentos desta entrega

- Protocolo fechado: 31/7/8 convergidos, geometria disjunta, c0015 incluído, condições constantes verificadas, CL/CD primários e Cp secundário.
- Teto: 12 ajustes, até 4510 épocas incluindo piloto, uma CPU/thread, 8 horas globais, 8 GiB RSS e 2 GiB de saídas privadas.
- Teste classificado como histórico com exposição prévia. A avaliação futura é retrospectiva e descritiva, sem alegação confirmatória.
- Os JSONs em `templates/` são formulários vazios. Não contêm hashes de dados, aceite E1, medições de hardware nem autorização.

## Evidência E1 sob custódia privada

João Pedro conserva originais e compartilha somente os materiais autorizados. Preencher o [inventário](../templates/r2-e1-inventory.json) fora do Git, incluindo cada arquivo relevante, origem, tamanho e SHA-256. Guardar referências às versões e transformações, sem credenciais. O resumo público pode informar disponibilidade e limitações, sem publicar caminhos privados, IDs adicionais ou dados por caso sem autorização própria.

Conferir, antes de aceitar a população:

1. Manifesto original e hashes, contagens 31/7/8 success, c0015 no teste, separação por geometry_id e ausência de geometria física duplicada entre partições.
2. Gerador e domínio m/p/t, condições constantes nos 46 casos, malha/atributos disponíveis antes do solver, unidades e referências de CL/CD/Cp.
3. Configuração/versão do solver, critérios e registros de convergência disponíveis; separar success, falhos e não convergidos e distinguir snapshot final de médias de janela.
4. Evidências e ressalva de malha de c0015, sem excluir ou regenerar esse caso.
5. Histórico de consultas ao teste: S3, relato v2, versões posteriores, datas conhecidas/desconhecidas e influência declarada nas decisões, com artefatos quando existentes.
6. Relatório do validador comum, erros e avisos com disposição científica. Diagnósticos por centros não comprovam topologia; erro preditivo não estima erro de discretização.

Se um registro histórico não existir, marcar sua ausência e seu impacto, sem reconstruir parâmetros. O orientador registra aceite das limitações ou bloqueios. Falta de insumos impede declarar E1 concluída nesta preparação.

## Código e ambiente antes de qualquer ajuste

- R1 revisada e aceita como infraestrutura; implementar e revisar R3/R4 conforme este protocolo. Os CLIs legados da PR #33 não são executores conformes: um só prevê CL e o outro usa cinco partes de desenvolvimento.
- Criar vista de modelagem somente de treino/validação. A auditoria completa pode ler os rótulos do teste sob custódia, com registro; seu relatório não deve expor erros aos responsáveis pela seleção. O validador existente não aplica isolamento de acesso.
- Verificar fora do treino, com dados sintéticos e, quando autorizado, dados privados: roundtrip de checkpoint sem otimização, inferência sem Cp, permutação de nós/arestas, integração por caso, hashes e bloqueio de sobrescrita.
- Registrar versões efetivas e fixá-las em lockfile do novo ambiente, além de OS, CPU, RAM e threads de BLAS/PyTorch. Esse lockfile não será atribuído às campanhas históricas. Instalação depende de autorização própria, sem procedimento automático.
- Implementar limites por processo e globais, contabilizar CPU de filhos, memória e slots; conferir o ledger antes de cada ajuste. A configuração documental não impõe os limites nos scripts atuais.

## Decisão que poderá liberar treinamento

Registrar responsável, data e referência à decisão do orientador contendo:

1. Versão e SHA-256 do protocolo/configuração e aceite E1 com limitações.
2. SHAs de código R1/R3/R4 e ambiente/hardware, com verificações de integração aprovadas.
3. Tetos exatos de 8 horas, CPU única/thread única, memória/armazenamento, 12 slots e seeds 42/43/44. Recursos ou retomadas fora disso exigem emenda.
4. Permissão específica para ajustar modelos; instalações, merge e publicação permanecem ações distintas.

O piloto técnico GNN também é treinamento e só ocorre depois dessa decisão. São 10 épocas no treino, sem avaliar validação/teste, seguidas de descarte dos pesos. As três execuções principais iniciam do zero.

## Congelamento antes da avaliação final

Preencher o [registro de congelamento](../templates/r2-freeze-record.json) no destino privado. Os campos de candidato relativos a validação são inaplicáveis ao piloto e devem ser marcados como tal, com motivo. Artefatos de candidatos falhos podem ser ausentes, mas falha, consumo e motivo são obrigatórios. IDs de treino/validação, configuração, parâmetros, transformações e hashes dos modelos selecionados são obrigatórios.

Conferir protocolo e manifestos por hash, código limpo, candidaturas previstas e falhas preservadas. Fixar um Ridge, um par GPR conjunto e os checkpoints GNN 42/43/44. Um modelo ausente ou a falha da seed primária impede o relatório primário completo; não se troca a seed nem se substitui silenciosamente a família.

Solicitar a decisão específica de avaliação final **somente depois** desse pacote concreto existir. A decisão identifica seu hash e libera uma passagem em lote nos oito casos. Salvar e hashear as predições antes de inspecionar erros. Não avaliar kernels perdedores ou mudar escolhas após abrir o teste. As repetições de inferência para cronometragem são sem rótulos e sem mudança de modelo.

## Entrega de resultados futura

Preservar no destino privado predições, Cp, resíduos por caso, incerteza GPR, ledger e artefatos. Apresentar síntese científica autorizada: n=8, exposição histórica, c0015 incluído, resultados negativos e limites de supervisão/recursos. Não substituir a tabela histórica S3. Merge, redistribuição de resultados e publicação dependem de decisões separadas.
