# Release de revisão — 23/10/2026

- Base da PR: main.
- Head: codex/release-s3-handoff-20261023.
- Conteúdo integrado: develop 3e088101ca1b7e7e94785949006b6a90b0db7f3e e main 04f4c027aafeaaa449c40e22f476c873559d5a80.
- Merge local das duas histórias: d33057c9d90e170c9b3fe8921dc6e9ab303d8cb2, sem conflitos.
- Alterações editoriais: apêndices A (dados/verificação), B (grafos) e C (baselines/reprodução), sem novas métricas ou mudanças nos modelos.
- Continuidade: PROJECT_STATE e documentos handoff/.

O pacote externo RELEASE_RECEIPT.json guarda a PR, SHA final, checks e estado de Pages consultados após o último push. Este documento deve receber a URL da PR assim que criada. Até aprovação explícita e execução verificada do merge, a publicação permanece preparada.

Workflow existente: .github/workflows/quarto-publish.yml, nome Quarto Publish; push em main dispara build-deploy, que renderiza e publica em gh-pages. Pages está configurado para a raiz dessa branch. O site público não deve ser declarado atualizado com base apenas no build da PR.
