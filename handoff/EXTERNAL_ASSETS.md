# Materiais externos e transferência privada

Este inventário identifica insumos conhecidos. Caminhos são históricos da máquina de origem, não caminhos obrigatórios na máquina de destino. Conferir existência, permissões e SHA256 antes de transferir. A ausência de um arquivo neste checkpoint não invalida o registro histórico, mas impede alegar nova leitura dele.

| Material | Local histórico / obtenção | Uso e estado |
|---|---|---|
| Dataset original ZIP | D:\Meu Drive\Atividades Atuais\PPGEE Joao Pedro Sebastien\dataset_euler_2d_banco_v2.zip | Fonte privada; não incluída no Git/pacote |
| Dataset derivado extraído | C:\Users\cvict\Documents\Codex\2026-10-13\new-chat\work\audit_extract_20261013\dataset_euler_2d | Disponível para inspeção na origem em 23/10; gerar hashes privados |
| Relatório S1 | D:\Meu Drive\Atividades Atuais\PPGEE Joao Pedro Sebastien\Relatório S1 – caso canônico Euler 2D.pdf | Referência científica histórica; obter por canal autorizado |
| Relatório de acompanhamento Projeto 02 | D:\Meu Drive\Atividades Atuais\PPGEE Joao Pedro Sebastien\Relatorio_Acompanhamento_Cientifico_Joao_Pedro_UAV_2026-10-13.pdf | Quatro páginas lidas e inspecionadas no chat de origem em 13/10; caminho não disponível na verificação de 23/10 |
| Resumo da campanha | work/audit_extract_20261013/Campanha Euler 2D banco_v2 – resumo.pdf, sob o workspace antigo | Referência privada; não incluída |
| Resultados S3 locais | C:\Users\cvict\Documents\Codex\2026-10-13\new-chat\work\s3-results.json e s3-results-final.json | Evidência histórica local; métricas agregadas em notes/; não publicar dump por caso |
| Checkpoint anterior | outputs/UAV-EXP-2026-05-checkpoint-2026-10-13.md no workspace antigo | Síntese histórica; substituída operacionalmente pelo novo PROJECT_STATE, sem apagar o registro |
| Arquivos Fluent, malhas e configurações | Custódia do pesquisador; inventário a consolidar | Necessários para proveniência/refinamento; não presumir entrega completa |
| Mandato atualizado | Será fornecido pelo Projeto 02 ao chat 02.03 | Autoridade para as próximas etapas; ainda não integra este pacote |

## Estrutura mínima do dataset derivado

~~~text
dataset_euler_2d/
  cases.csv
  dataset_manifest.json
  split_manifest.json
  meshes/mesh_metadata.json
  surface/case_<case_id>.parquet
~~~

O leitor espera superfície nesse padrão de caminho. Transferir o conjunto de arquivos preservando nomes, encoding e hashes. Não renomear IDs ou completar campos por suposição. Guardar o dataset em diretório privado separado do checkout.

## Conteúdo científico do acompanhamento de 13/10

O relatório situa o trabalho na primeira fase NACA/Euler 2D. Prioriza proveniência/qualidade de dados, comparação convencional Ridge/GNN com condições operacionais equivalentes, formalização AG/ablações, generalização/consistência e escrita gradual da dissertação. Não recomenda repetição indiscriminada da campanha. Ressalva a ausência de prova de superioridade GNN/AG e a necessidade de benchmark independente de Maxwell. O eBook deve permanecer distinto da dissertação. Essas recomendações foram incorporadas ao planejamento; não substituem autorização de sprint.

## Dependências e portabilidade

Testes sintéticos: Python padrão; CI em 3.11. Leitura de Parquet: PyArrow. Treinamento GNN: PyTorch opcional, não executado. Publicação: Quarto, TinyTeX, Git e workflows GitHub Actions. Não há lockfile completo do ambiente científico histórico. O recibo registra versões observadas na transferência, que não devem ser retroatribuídas à execução de 13/10.

Não transferir tokens, hosts.yml, .env, perfis de navegador ou caches de autenticação. Na outra máquina, autenticar o próprio GitHub por meio aprovado. Clonar o repositório público e executar testes mínimos não exige compartilhar credenciais da máquina antiga.
