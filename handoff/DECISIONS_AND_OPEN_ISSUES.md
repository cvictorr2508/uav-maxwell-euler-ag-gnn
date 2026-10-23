# Decisões, ressalvas e escolhas abertas

## Decisões aceitas no histórico

| Decisão | Registro e consequência |
|---|---|
| Usar o dataset derivado | UAV-EXP-2026-02; preservar os originais e a origem |
| Manter oito não convergidos | Análise de sensibilidade; avisos snapshot/janela preservados |
| Manter c0015 no teste | Restrição experimental explícita, com ressalva de malha |
| Partições originais | 31/7/8 convergidos; não reescrever manifesto |
| Múltiplos casos por geometria | Ajuste S2; preservar integridade referencial |
| Conectividade disponível | Contorno via contour_index; zero topologia volumétrica inferida |
| Sem vazamento | Somente entradas pré-solver; observáveis Fluent são referências |
| GNN S3 | Protótipo não executado; --run-gnn é disponibilidade |
| Barreira científica | Erros de validate_dataset bloqueiam métricas no CLI S3 |
| Publicação atual | PR #29 merged em main com autorização; Quarto Publish, deployment e site verificados |
| Retorno a develop | Sincronização autorizada pelo usuário, incluindo documentação revisada; PR/merge/checks em SYNC_VERIFICATION.json |

## Questões para o mandato atualizado do Projeto 02

1. Qual é o artefato editorial principal da próxima sprint: harmonização do eBook, artigo separado ou metodologia da dissertação? Quais entregas e avaliadores?
2. Registrar a publicação #29 e a sincronização de retorno já autorizadas. Definir a autonomia para merges e futuras publicações durante a continuidade em outra máquina.
3. Quando e sob qual orçamento serão autorizados PyTorch e treino da GNN com condições globais? Quais seeds/repetições e critérios de checkpoint?
4. Há documentação suficiente para reproduzir a campanha Fluent? Qual é a política de acesso/transferência dos arquivos científicos?
5. Qual análise de qualidade de c0015 e de refinamento é possível sem alterar o teste? Novas simulações são de responsabilidade e aprovação específicas.
6. Como reconciliar seed geral 42 com a configuração histórica 202604, preservando o split? Não tratar essa diferença documental como licença para regenerar dados.
7. Quais alegações de generalização e incerteza são sustentáveis com oito testes e 31 treinos? Caso insuficientes, quais conclusões limitadas serão aceitas?
8. Maxwell, 3D e multifidelidade permanecerão fundamentação/extensão ou exigirão campanhas independentes? Não iniciar por inércia do título do projeto.
9. Autoria, contribuições e licença do texto estão aprovadas para a versão final acadêmica?

## Débitos técnicos/documentais a avaliar, sem correção automática nesta release

- O CLI coleta disponibilidade PyTorch também no caminho sem flag; os rótulos diferem e nenhum caminho treina. Decidir futura interface junto com o protocolo GNN.
- A suíte confirma bloqueio para um erro sintético específico, mas a cobertura não demonstra que toda corrupção de dados produz relatório em vez de exceção. Auditar denominadores nulos e valores inválidos conforme risco.
- A seleção de entradas tem whitelist; ampliar a validação de alvos/configurações apenas com escopo aprovado e testes apropriados.
- O limiar de continuidade geométrica é heurístico; avaliar sua interpretação antes de usá-lo como gate de treino em dados diferentes.
- Faltam condicionamento operacional, inferência e avaliação completas do protótipo GNN.
- Versões e recursos históricos incompletos não devem ser preenchidos com medições de outra execução.
- Os capítulos e algumas notas históricas têm futuro verbal/estados antigos; D1 deverá harmonizá-los e preservar registros datados.
