# Release de revisão — 23/10/2026

- Base da PR: main.
- PR: https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/pull/29 — merged e fechada após autorização explícita em 23/10/2026.
- Merge em main: c2bf7d562e864e12b6c7a3a8e678b35f04c67a7d.
- Head aprovado: 3a6e0d1934b417b627970185eb87816241a81f78; checks test e render: success.
- Quarto Publish: https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/actions/runs/39962381130 — success, originado do merge em main.
- Pages deployment: https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn/actions/runs/39962639167 — success.
- gh-pages: f39f16e79a07767d0260586a5f8054c0bde22aac.
- Site: https://cvictorr2508.github.io/uav-maxwell-euler-ag-gnn/ — índice, três apêndices e PDF conferidos por HTTPS e por hash Git blob; PDF com 105 páginas.
- Head: codex/release-s3-handoff-20261023.
- Conteúdo integrado: develop 3e088101ca1b7e7e94785949006b6a90b0db7f3e e main 04f4c027aafeaaa449c40e22f476c873559d5a80.
- Merge local das duas histórias: d33057c9d90e170c9b3fe8921dc6e9ab303d8cb2, sem conflitos.
- Alterações editoriais: apêndices A (dados/verificação), B (grafos) e C (baselines/reprodução), sem novas métricas ou mudanças nos modelos.
- Continuidade: PROJECT_STATE e documentos handoff/.

O pacote pós-publicação contém RELEASE_RECEIPT.json e PUBLICATION_VERIFICATION.json. Eles distinguem o head aprovado da PR, o merge publicado, gh-pages e o commit local de checkpoint. O checkpoint local descendente de main atualiza estes documentos e o empacotador, sem push ou nova publicação. O pacote pré-merge foi preservado como histórico e não representa o estado final.

Workflow existente: .github/workflows/quarto-publish.yml, nome Quarto Publish; push em main dispara build-deploy, que renderiza e publica em gh-pages. Pages está configurado para a raiz dessa branch. O site público não deve ser declarado atualizado com base apenas no build da PR.
