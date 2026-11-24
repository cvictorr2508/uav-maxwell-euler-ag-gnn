# Pendências editoriais e científicas de D1

Corte: 24/11/2026. R0 trata documentação; R1 trata correções de infraestrutura. Novas campanhas permanecem condicionadas a decisões posteriores do orientador.

| Pendência | Fonte disponível | Próxima decisão ou material necessário |
|---|---|---|
| Proveniência e qualidade CFD | `handoff/EXTERNAL_ASSETS.md`; apêndice A | João Pedro disponibiliza, por canal autorizado, dataset, hashes, configurações, malhas e históricos existentes |
| Resultados v2–v4 | PDF integrado na PR #31 | Receber logs, CSVs, configuração, ambiente e artefatos; não reconstruir versões ou medições por suposição |
| Uso anterior do teste | PDF p. 5 | Consolidar cronologia e política de avaliação final com o orientador; manter os casos e `c0015` |
| População e tarefa comparativa | Código v4/GPR e protocolo S3 | Aprovar papel dos não convergidos e distinção CL/CD global versus Cp com integração |
| Experiência AG | PDF p. 25 | Receber código e definição das transformações; decidir escopo S4 sem aceitação retroativa de resultados |
| Ruído CFD de aproximadamente 1% | Afirmação do PDF | Exigir evidência de repetibilidade/convergência antes de tratá-lo como limite de desempenho |
| Autoria do eBook e contribuições | `CITATION.cff`, texto e PDF de João Pedro | Orientador e pesquisador confirmam autores, papéis e atribuição das contribuições; D1 não altera nomes por inferência |
| Licença editorial e figuras | LICENSE do repositório e fontes citadas | Confirmar licença do texto/PDF/figuras e direitos de redistribuição; MIT do código não resolve automaticamente a política acadêmica |
| Bibliografia afetada | `references.bib`; capítulos 5–6 e apêndice C | Referências adicionadas: Rasmussen/Williams (2006) e Cawley/Talbot (2010), fontes primárias verificáveis; manter estilo IEEE existente |
| ENCERRAMENTO | Inventário `handoff/DOCUMENTS_TO_TRANSFER.md` | Receber ZIP e recibos/hashes externos para atestar a transferência; Git não substitui essa verificação |

Critérios de aceite de R0: diff restrito aos dez arquivos delimitados; fontes e datas explícitas; tabela histórica S3 preservada; HTML/PDF sem execução científica; revisão visual de tabelas, equações e referências afetadas. O orientador decide merge e publicação separadamente.

Na revisão da PR #32, referências a tarefas internas e números de PR foram mantidas nas notas de auditoria e retiradas dos acréscimos à narrativa pública, conforme `notes/editorial-scientific-guidelines.md`. Datas, estado de evidência e limitações científicas permanecem no eBook.
