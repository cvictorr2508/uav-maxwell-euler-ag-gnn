# Guia de retomada em outra máquina

## 1. Integridade e código

Começar por handoff/DOCUMENTS_TO_TRANSFER.md. Extrair a edição ENCERRAMENTO em uma pasta curta no Windows, por exemplo C:\uav ou D:\uav, para evitar o limite de comprimento de caminhos dos recursos HTML. Verificar SHA256SUMS.json com scripts/verify_transfer.py. O manifesto cobre os arquivos do diretório, exceto o próprio manifesto; o ZIP externo tem hash separado. Esta edição usa develop integrado após a sincronização de main. O commit publicado de main é c2bf7d5; o SHA final de develop e os checks estão em SYNC_VERIFICATION.json e RELEASE_RECEIPT.json. O checkpoint anteriormente local foi incorporado à PR de sincronização.

Com rede, clonar o repositório oficial em uma pasta nova:

```powershell
git clone https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn.git
Set-Location uav-maxwell-euler-ag-gnn
git fetch origin --prune
git switch develop
git status --short --branch
git log --all -8 --oneline
```

Comparar o SHA de develop com os recibos do pacote e consultar eventuais alterações posteriores. A base para novo desenvolvimento é develop, conforme o mandato atualizado. main contém a publicação do texto; seus documentos podem refletir o estágio anterior da preparação. Não executar reset em checkout com alterações.

Sem rede, o bundle permite criar outro checkout:

```powershell
git clone --branch develop CAMINHO\repository.bundle uav-offline
Set-Location uav-offline
git remote set-url origin https://github.com/cvictorr2508/uav-maxwell-euler-ag-gnn.git
git log -3 --oneline
```

O bundle anuncia develop e as referências observadas de main/develop; elas são um snapshot, não o estado remoto futuro. repository-source.zip contém os fontes versionados de develop no encerramento, sem metadados Git. O recibo distingue o SHA de develop do merge publicado em main. Preferir clone/bundle para continuar o histórico e reconsultar o remoto antes de desenvolver.

## 2. Python mínimo

Python 3.11 é a versão de CI. Criar ambiente virtual local; os testes sintéticos usam biblioteca padrão, sem pip install:

```powershell
py -3.11 -m venv .venv
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$env:PYTHONPATH = 'src'
& $python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Falha nos testes' }
& $python -m compileall -q src tests scripts
```

Usar o executável diretamente dispensa mudar a política de execução do PowerShell. Em Linux/macOS, usar .venv/bin/python e PYTHONPATH=src. Não copiar ambientes virtuais entre máquinas.

## 3. Dados reais: acesso privado separado

Obter o dataset derivado por canal autorizado conforme EXTERNAL_ASSETS.md. Conferir hashes antes de usar; manter os arquivos fora do checkout. Somente essa etapa requer PyArrow. Caso autorizada a instalação, registrar a versão escolhida no ambiente novo; não há lockfile científico validado para toda a plataforma. PyTorch não é necessário para reproduzir os baselines.

```powershell
$dataset = 'D:\dados-privados\dataset_euler_2d'
& $python scripts/validate_euler2d.py $dataset --json
if ($LASTEXITCODE -ne 0) { throw 'Dataset inválido; experimento bloqueado' }
& $python scripts/inspect_surface_graph.py $dataset c0015
& $python scripts/run_s3_experiment.py $dataset --seed 202604 --output 'D:\resultados-privados\s3-results.json'
```

Resultado esperado da referência: validação sem erros, oito avisos de snapshot/janela dos não convergidos, partições 31/7/8 e c0015 no teste. Comparar métricas com notes/euler2d-s3-results-exploratory.md considerando o arredondamento. Guardar o JSON em diretório privado. Não gerar modelos novos ou instalar PyTorch sem mandato.

## 4. Texto, apêndices e PDF

Instalar ou disponibilizar Quarto e TinyTeX conforme a política da máquina. Registrar versões; não assumir que existem. Para a edição documental atual, os blocos de comandos são exemplos e o render pode ocorrer sem execução científica:

```powershell
quarto --version
quarto render --no-execute
```

Examinar _book/index.html, os três apêndices e o PDF gerado. Verificar navegação, tabela de métricas, equações, referências e links. O CI Quarto continua executando quarto render normalmente. Uma falha de render é diagnóstico editorial/ambiente, não motivo para refazer simulações.

## 5. Publicação, somente após autorização

A publicação da PR #29 já foi autorizada, executada e verificada. PUBLICATION_VERIFICATION.json registra o resultado. O procedimento abaixo aplica-se a publicações futuras; não repetir a operação já concluída.

Conferir checks test e render no SHA atual da PR. Obter aprovação explícita de merge em main; então o push decorrente do merge aciona Quarto Publish. Acompanhar build-deploy e o deployment Pages, verificar o commit de origem em gh-pages e abrir index, apêndices e download PDF por HTTPS. Registrar SHA e URLs; build local não comprova publicação.

A sincronização de retorno de main para develop foi autorizada; seu resultado é registrado em SYNC_VERIFICATION.json. Conferir o merge e os checks antes de retomar, sem repetir a operação. Novas sincronizações ou publicações seguirão o mandato atualizado. Não apagar branches de trabalho ou histórico arquivado por rotina.

## 6. Ponto de decisão

Entregar diagnóstico da máquina e proposta de sprint ao Projeto 02. Ler o mandato atualizado antes de mudanças. Registrar no PROJECT_STATE.md o ponto da retomada, sem substituir a evidência histórica de 13/10 por resultados não executados.
