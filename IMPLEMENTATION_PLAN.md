# Plano técnico de implementação

Data da análise: 07/10/2026. Repositório analisado no commit `a94ce443299b4928d0f1e08cecdacf7a36ff5fb1`.

**Estado:** planejamento aprovado para implementação em 07/10/2026. A análise original abaixo permanece como registro do ponto de partida; as decisões consolidadas e o acompanhamento desta etapa prevalecem sobre referências antigas a trabalho futuro. As respostas originais da seção 11 foram preservadas.

### Decisões aprovadas e acompanhamento

- Q1=B: núcleo factual rigoroso e sugestões técnicas separadas, sujeitas a validação.
- Q2=A: cada uma das cinco métricas agregadas deve ser >=0.8, além da média geral; auditar também todos os exemplos, sem ocultar notas baixas.
- Q3=A: geração `gpt-4.1-mini-2025-04-14`, juiz `gpt-4.1-2025-04-14`. Adotar conservadoramente o teto proposto de US$ 5; não trocar modelos ou aumentar o teto silenciosamente.
- Q4=A e Q5=A: Few-shot + Role Prompting, três exemplos no system, uma história principal e tratamento explícito de lacunas.
- Q6=A: comparação v1/v2 qualitativa, sem baseline pago da v1.
- Q7=A: preservar `.env.example` e `requirements.txt`; configurar OpenAI no `.env` local ignorado pelo Git.
- Q8=A e Q9=A: projeto padrão, dataset/experimentos públicos e capturas em `docs/evidencias/` quando existirem resultados reais e configuração válida.
- Preservar os quatro arquivos proibidos byte a byte. Validar etapas locais com testes offline e mocks; executar operações externas somente após verificar configuração.
- Inspeção inicial desta etapa: nenhum `.env` ou variável de credencial configurada. A chave enviada no chat não será repetida em código, documentação ou logs; configuração local segura foi solicitada. Sem LangSmith configurado, avançar com implementação offline, sem tentar pull/push/avaliação.
- Exceção operacional à sequência original: se o pull real estiver indisponível, preservar a v1 fornecida, validar o pull com mocks e criar a v2 a partir da análise já realizada. Não afirmar que houve download remoto.

| Etapa executada | Resultado em 07/10/2026 |
| --- | --- |
| Ambiente | `venv/` criado; requirements original instalado; `pip check` sem dependências quebradas. |
| Configuração | `.env` local ignorado pelo Git com OpenAI, snapshots, handle e projeto definidos. Chaves vazias; a chave do chat não foi copiada para comandos ou arquivos. |
| Pull local | Implementado e validado com 9 testes iniciais; round-trip e preservação do arquivo anterior em falhas. Pull remoto pendente de configuração. |
| V2 e testes obrigatórios | Três exemplos sintéticos, Role Prompting, regras de fidelidade e lacunas; etapa com 16 testes aprovados. |
| Push local e contratos | Publicação pública, metadados e validação implementados; 50 testes aprovados após essa etapa. |
| Integração offline e revisão final | 52 testes aprovados, incluindo clientes OpenAI sem rede e target original com LLM falso. `pytest -q`: 52 passed. |
| Segurança e preservação | Scanner local sem achados de chaves nos 16 arquivos candidatos a versionamento; quatro hashes protegidos iguais. Nenhum commit criado. |
| README | Atualizado com decisões, comandos, limitações, comparação qualitativa, testes e métricas explicitamente não medidas. |
| Operações externas | Não executadas: faltam credenciais no ambiente local. Sem métricas finais, publicação, experimentos, compartilhamento ou capturas. |

Não houve iteração de qualidade baseada em nota: nenhum juiz foi chamado. A primeira validação estrutural encontrou duas assertions excessivamente restritivas (maiúsculas nos cenários e verbo português “preencher” confundido com placeholder); elas foram ajustadas para o contrato real, sem alterar o prompt para satisfazer palavras-chave. Os testes foram repetidos e passaram.

## 1. Entendimento do desafio

Entregar um fluxo Python 3.10+, LangChain e LangSmith que transforme relatos de bugs em User Stories com OpenAI. O prompt semente é `leonanluppi/bug_to_user_story_v1`; a publicação final deve ser pública em `lucaskawasaki/bug_to_user_story_v2`.

O trabalho posterior deve implementar `src/pull_prompts.py`, `src/push_prompts.py`, `prompts/bug_to_user_story_v2.yml`, os seis testes de `tests/test_prompts.py` e a documentação em `README.md`. O pull deve salvar o conteúdo original em `prompts/bug_to_user_story_v1.yml`, sem corrigir suas deficiências intencionais. Few-shot Learning é obrigatório, acompanhado de pelo menos outra técnica da lista do desafio.

Sucesso exige funcionamento de ponta a ponta, testes efetivos, cinco métricas individualmente >= 0.8 e média das cinco >= 0.8, com resultados reais documentados. O README também exige fork público no GitHub, expectativa de 3–5 iterações, evidências do dataset com 15 exemplos, experimentos e tracing de pelo menos três exemplos.

**Arquivos protegidos:** `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl`. Não serão modificados. Qualquer necessidade de mudança será discutida antes; limitações encontradas estão registradas neste plano.

Atingir 0.8 é um critério de conclusão a comprovar, não uma garantia antecipada: notas dependem das respostas geradas, dos juízes, das referências e da execução íntegra. Testes estruturais não demonstram qualidade semântica.

## 2. Estado atual do projeto

### Inventário e dependências

Na análise inicial, foram lidos todos os 14 arquivos versionados, incluindo integralmente os 15 registros JSONL. Não foram encontrados `AGENTS.md` na árvore inspecionada ou nos diretórios ancestrais. O Git estava sem alterações naquele momento. Ainda não havia v2, `.env`, ambiente virtual ou plano anterior na raiz. O executável `python` informava Python 3.14.7; a instalação de dependências foi validada posteriormente, conforme o acompanhamento no início deste documento. A tabela abaixo descreve o ponto de partida.

| Arquivo | Responsabilidade e implementação atual | O que falta / dependências |
| --- | --- | --- |
| `README.md` | Enunciado, comandos, restrições, entrega, publicação e evidências. Resultados numéricos são ilustrativos. | Documentar processo real, técnicas, comparação v1/v2, modelos, iterações, resultados e execução OpenAI. Depende de todas as fases. |
| `requirements.txt` | Fixa `langchain-core==1.6.4`, `langsmith==0.13.0`, `langchain-openai==1.6.2`, `langchain-google-genai==4.4.0`, `python-dotenv==1.2.3`, `pyyaml==6.0.3`, `pydantic==2.13.5`, `pytest==9.1.1`. Não depende do metapacote `langchain`. | Instalação e `pip check` apenas na etapa de implementação. Manter versões; o pacote Gemini presente não obriga seu uso. |
| `.env.example` | Lista credenciais, endpoint, projeto, handle e modelos. `LLM_PROVIDER=google`; modelos e chaves vazios. | Configurar `.env` local com OpenAI e `lucaskawasaki`; não copiar o provider Google inadvertidamente. Não é necessário editar o template para o fluxo funcionar. |
| `.gitignore` | Ignora `.env`, `.env.local`, `venv/`, caches, logs, `screenshots/` e `results/`. | Planejar evidências acessíveis: arquivos dentro das duas últimas pastas não serão versionados normalmente. `.venv/` não consta; preferir `venv/`. |
| `prompts/bug_to_user_story_v1.yml` | Mapeamento externo `bug_to_user_story_v1`; campos internos `description`, `system_prompt`, `user_prompt`, `version`, `created_at`, `tags`. `{bug_report}` aparece no system e no user. | Substituir pelo pull real na fase própria, preservando o conteúdo recebido. Não há few-shot nem contrato de saída útil. |
| `prompts/bug_to_user_story_v2.yml` | Ainda não existe. | Criar com esquema compatível, exemplos reais de entrada/saída, regras de fidelidade, tratamento de lacunas e `techniques_applied`. Depende de decisões da seção 11. |
| `src/pull_prompts.py` | Imports e instruções prontos; `pull_prompts_from_langsmith()` e `main()` contêm `...`. | Implementar validação de ambiente, pull, extração das mensagens, conversão para esquema local, persistência e status. Usa `Client`, `save_yaml`, `check_env_vars`, `print_section_header`. |
| `src/push_prompts.py` | Imports e assinaturas prontos; `push_prompt_to_langsmith(...) -> bool`, `validate_prompt(...) -> tuple[bool, list]` e `main()` sem implementação. | Ler YAML, validar, construir `ChatPromptTemplate`, publicar com descrição/tags/técnicas e reportar URL/status. Usa `load_yaml`, `Client`, ambiente e campos internos da v2. |
| `src/evaluate.py` — protegido | Carrega JSONL, cria/reutiliza dataset, puxa v2 do Hub, compõe prompt e LLM, executa experimento sequencial, publica cinco feedbacks e calcula médias. `main()` retorna 0 ou 1. | Não implementar nada. Exige prompt já publicado, execução na raiz, credenciais, modelos e dataset correto. Limitações abaixo. |
| `src/metrics.py` — protegido | Três juízes gerais: F1, Clarity e Precision. Contém também quatro juízes específicos e um bloco de demonstração executável. Usa `utils.get_eval_llm()` e parser JSON próprio. | Não alterar. Os quatro juízes específicos não entram no resultado oficial. Falhas dos juízes podem virar score 0. |
| `src/utils.py` — protegido | YAML, ambiente, impressão, validação básica, extração JSON e seleção de LLM. `get_llm()` usa provider/modelo/chave; `get_eval_llm()` usa `EVAL_MODEL`. | Reutilizar as interfaces reais. Complementar validação no push/testes, sem alterar este arquivo. |
| `tests/test_prompts.py` | Loader YAML, inclusão de `src` no path, import do validador e classe com seis métodos `pass`. | Implementar assertions: hoje os métodos não verificam nada e podem passar falsamente. Nenhuma outra suíte de testes existe. |
| `src/__init__.py`, `tests/__init__.py` | Marcadores de pacotes, somente comentários. | Nenhuma alteração necessária. |
| `datasets/bug_to_user_story.jsonl` — protegido | 15 exemplos válidos na inspeção com `inputs.bug_report`, `outputs.reference`, `metadata`. Cinco simples, sete médios, três complexos. | Manter integralmente; serve de avaliação, não de banco de respostas para copiar para o prompt. |

Os metadados das oito versões fixadas foram consultados no PyPI: existem e declaram compatibilidade com Python 3.10 no campo `Requires-Python`. Isso não substitui a resolução das dependências transitivas nem demonstra funcionamento no Python 3.14.7 local. Fontes: páginas JSON de versões, por exemplo [langchain-core 1.6.4](https://pypi.org/pypi/langchain-core/1.6.4/json) e [pytest 9.1.1](https://pypi.org/pypi/pytest/9.1.1/json).

### Contratos reais que a implementação deverá respeitar

- `load_yaml(path)` retorna o conteúdo desserializado ou `None`; não assegura que seja um dicionário. `save_yaml(data, path)` cria diretórios e retorna booleano. Preserva texto Unicode, mas não comentários nem necessariamente estilo de blocos YAML.
- `validate_prompt_structure()` recebe o **objeto interno** do prompt, não o mapeamento externo. Exige presença de `description`, `system_prompt`, `version`, system não vazio, ausência de `TODO` no system e tamanho mínimo 2 em `techniques_applied`. Não garante tipos, campos não vazios em geral, técnicas distintas, few-shot ou variável de entrada correta.
- Os novos scripts devem manter suas assinaturas, executar pelo guard `__main__` e devolver status não zero em erro. Importar um script não deve publicar nem baixar prompts.
- O target de avaliação recebe `{"bug_report": "..."}`, chama `prompt_template | llm` e devolve `{"answer": response.text}`. Não espera JSON estruturado do gerador. Somente os juízes devem responder JSON.
- O avaliador carrega **exclusivamente a v2 remota**. Editar YAML sem novo push não muda a avaliação. O CLI não tem argumento para selecionar v1 ou subconjunto de exemplos.
- Usar somente `{bug_report}` como variável dinâmica. Chaves literais em exemplos precisam de escape no template; o texto do bug inserido como valor não deve ser formatado uma segunda vez.

### Limitações nos arquivos protegidos e encaminhamento

| Constatação | Consequência | Tratamento sem alterar arquivos protegidos |
| --- | --- | --- |
| `create_evaluation_dataset()` reutiliza dataset pelo nome, sem comparar conteúdo, contagem ou versão. | Dataset antigo/incompleto pode invalidar a evidência. | Conferir os 15 inputs/references remotos antes de aceitar resultados. Se houver colisão, usar novo `LANGSMITH_PROJECT` ou discutir recuperação, sem excluir dados automaticamente. |
| A criação envia apenas `inputs` e `outputs`, omitindo `metadata` do JSONL. | Domínio/complexidade/severidade não chegam como metadados de exemplos. | Manter tabela de estratos neste plano/README e identificar os exemplos pelo relato. Não acrescentar metadados ao fluxo protegido. |
| Exceções na criação de dataset são impressas, mas a função devolve o nome mesmo assim. | O fluxo pode continuar com estado remoto incompleto. | Tratar erro de criação como impeditivo operacional, inspecionar antes de repetir. |
| Médias usam os feedbacks disponíveis por chave, sem exigir 15 resultados por métrica. | Uma execução incompleta pode parecer suficiente. | Exigir 15 respostas e 75 feedbacks válidos, sem falhas, além do status do CLI. |
| Aprovação usa médias por métrica; não exige todos os exemplos >= 0.8. | Um bug complexo ruim pode ficar escondido pela média. | Expor resultados por exemplo/complexidade e decidir rigor adicional em Q2. |
| Juízes não validam estritamente intervalo [0,1]/finitude; falhas podem gerar zeros. | Distinguir problema de prompt de falha técnica e verificar scores anômalos. | Inspeção dos feedbacks/comentários e repetição justificada após correção de configuração. Caso exija patch, discutir antes. |
| `temperature=0` é imposto em geração e avaliação; não há ajuste específico de reasoning nem limite explícito de saída. | Alguns modelos são incompatíveis; respostas longas aumentam custo. | Escolher modelos compatíveis e controlar extensão no prompt, sem mudar `utils.py`. |
| O experimento registra nome do prompt/modelos/provider, mas não fixa explicitamente o commit remoto. | Dificuldade de reproduzir uma iteração após novo push. | Anotar commit/URL retornada do Hub, hash local, modelos e URL do experimento; não publicar durante um experimento. |
| Referências incluem detalhes não sustentados pelas entradas. | Conflito entre Recall/F1 e não inventar requisitos. | Política explícita de inferências/sugestões em Q1; preservar dataset e métricas. |

Não foi demonstrada necessidade de alterar nenhum arquivo protegido. As limitações exigem validação operacional e decisões explícitas; não serão corrigidas de forma disfarçada em outro arquivo nem contornadas com monkeypatch do avaliador.

## 3. Fluxo completo da solução

**LangSmith Hub → pull → YAML local → otimização → push → dataset → execução do LLM → avaliação → métricas → experimento/tracing.**

1. O script de pull usa `Client()` autenticado para buscar `leonanluppi/bug_to_user_story_v1`, com `dangerously_pull_public_prompt=True`. O conteúdo remoto efetivo ainda não foi inspecionado nesta etapa; não presumir que seja idêntico ao YAML incluso.
2. Extrai papéis e textos do `ChatPromptTemplate`, validando a estrutura antes de gravar o esquema local em `prompts/bug_to_user_story_v1.yml`. Recarrega e compara textos/variáveis para comprovar que não houve perda.
3. A v2 é criada separadamente, usando v1 e análise do dataset para estabelecer requisitos de qualidade. Few-shots demonstram casos novos; as referências não entram na entrada de execução.
4. O push lê `bug_to_user_story_v2` do YAML, valida, monta mensagens system/user e publica o template, sem acoplar modelo ou credenciais, em `lucaskawasaki/bug_to_user_story_v2`.
5. `src/evaluate.py` lê o JSONL e cria/reutiliza `<LANGSMITH_PROJECT>-eval`. Entradas vão ao target; `outputs.reference` é entregue aos avaliadores, não ao gerador.
6. O avaliador faz novo pull da v2, instancia `ChatOpenAI` por `get_llm()` e chama `chain.invoke(inputs)` para cada exemplo.
7. `evaluate_all_metrics()` executa três juízes por resposta e deriva as duas métricas adicionais. A execução normal completa demanda 15 gerações e 45 chamadas de juiz, antes de eventuais retries.
8. `client.evaluate()` já cria o experimento e relaciona runs, exemplos e feedbacks. O terminal mostra médias e URL; tracing LangChain fornece a árvore das chamadas.
9. A análise de falhas leva a nova revisão do YAML, testes, novo push e novo experimento. Evidências relacionam cada versão a sua execução real.

## 4. Estratégia para OpenAI

### Seleção de provider e variáveis

`utils.get_llm()` lê `LLM_PROVIDER`, aplica `.lower()` e escolhe OpenAI ou Google. O default do código é OpenAI, porém o template `.env.example` define Google explicitamente. O plano requer **`LLM_PROVIDER=openai`**, em minúsculas, sem espaços. `evaluate.main()` também consulta esse valor para exigir a chave correta.

| Variável | Configuração prevista / consumo |
| --- | --- |
| `LLM_PROVIDER` | `openai`, obrigatório no CLI de avaliação. |
| `OPENAI_API_KEY` | Chave pessoal configurada apenas no ambiente/`.env`. `utils.get_llm()` a passa como `api_key` ao `ChatOpenAI`, tanto para geração quanto para os juízes. |
| `LLM_MODEL` | Recomendação inicial: `gpt-4.1-mini-2025-04-14`. |
| `EVAL_MODEL` | Recomendação inicial: `gpt-4.1-2025-04-14`. Configurar explicitamente; a função utilitária isolada poderia fazer fallback para `LLM_MODEL`, mas o CLI exige ambos. |
| `LANGSMITH_API_KEY` | Credencial própria do LangSmith; não é a chave OpenAI. |
| `LANGSMITH_TRACING` | `true`. |
| `LANGSMITH_ENDPOINT` | Endpoint da região do workspace; o template usa `https://api.smith.langchain.com`. |
| `LANGSMITH_PROJECT` | Manter, se não houver colisão, `mba-ia-pull-evaluation-prompt`. |
| `USERNAME_LANGSMITH_HUB` | `lucaskawasaki`. |
| `LANGSMITH_WORKSPACE_ID` | Condicional, se a chave acessar múltiplos workspaces. |
| `GOOGLE_API_KEY` | Desnecessária; não configurar para esta solução. |

`load_dotenv()` já está nos scripts/utilitários. Variáveis previamente exportadas podem prevalecer sobre `.env`; conferir apenas nomes/valores não secretos no diagnóstico. Não imprimir chaves, copiá-las para exemplos, passá-las ao prompt ou armazená-las nos metadados.

### Modelos e custo x qualidade

Recomendo começar com GPT-4.1 mini para geração e GPT-4.1 para avaliação, preferindo os snapshots acima para comparabilidade. É uma recomendação de compatibilidade com este código e esta tarefa textual, não uma afirmação de que sejam os modelos mais recentes. A documentação registra Chat Completions, seguimento de instruções e snapshots; o pré-teste futuro deve confirmar acesso da conta e aceitação efetiva de `temperature=0`. Referências: [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) e [GPT-4.1](https://developers.openai.com/api/docs/models/gpt-4.1).

O gerador menor reduz custo de iteração; o juiz maior é a recomendação para avaliar cobertura e fidelidade de respostas complexas. Isso não garante melhor nota nem elimina variabilidade/viés do juiz. Manter o juiz fixo entre iterações; se a geração apresentar omissões persistentes, considerar GPT-4.1 também como gerador, conforme Q3.

Preços padrão consultados em 07/10/2026, por 1 milhão de tokens, sem descontos de cache/Batch: GPT-4.1 mini US$ 0.40 entrada / US$ 1.60 saída; GPT-4.1 US$ 2.00 entrada / US$ 8.00 saída. São preços publicados nas páginas dos modelos acima, sujeitos a alteração e condições da conta.

Estimativa ilustrativa, não medição: uma rodada com 60 mil tokens de entrada + 15 mil de saída do gerador e 135 mil de entrada + 9 mil de saída dos juízes custaria aproximadamente **US$ 0.39**. Os juízes recebem bug, referência e resposta três vezes; referências extensas tornam essa parcela relevante. 3–5 rodadas corresponderiam a cerca de US$ 1.17–1.95 nesse cenário, sem retries, testes extras, baseline ou custos do LangSmith. O README estima US$ 1–5, mas o limite real precisa ser definido em Q3. Registrar consumo efetivo a cada rodada.

## 5. Integração com LangSmith

### Ambiente e workspace

O handle já informado é `lucaskawasaki`; não propor criar outro. Verificar posteriormente se a credencial tem acesso ao workspace proprietário desse handle e permissões de leitura/escrita de prompts, datasets, runs e feedback. Endpoint deve corresponder à região; `LANGSMITH_WORKSPACE_ID` é necessário em certos acessos a múltiplos workspaces. `LANGSMITH_PROJECT` agrupa traces comuns; os experimentos criados por `evaluate()` têm seus próprios identificadores. [Configuração oficial de tracing](https://docs.langchain.com/langsmith/trace-with-langchain).

### Pull e persistência

- Implementar `pull_prompts_from_langsmith()` com o identificador semente exato e `dangerously_pull_public_prompt=True`. Manter `include_model=False` e não habilitar resolução de segredos. O flag autoriza desserialização do prompt público; não publica nada nem executa o LLM.
- Validar que o objeto recebido é um template de chat textual compatível. Inspecionar `prompt.messages` e `.prompt.template` por papel; não usar `str(prompt)` como conteúdo do YAML.
- Para o contrato esperado de uma mensagem system e uma human, armazenar seus textos sem mudanças. Se houver mensagens extras, placeholders, modelo embutido ou estrutura incompatível, falhar com diagnóstico em vez de descartar conteúdo silenciosamente.
- Usar `save_yaml`, verificar seu retorno e recarregar. Tratar autenticação, indisponibilidade, prompt inexistente e falha de escrita com status não zero. `main()` verifica somente as variáveis necessárias ao pull, sem exigir chave OpenAI.
- Preservar metadados disponíveis e distinguir dados recebidos de dados locais de proveniência. Não inventar data original de criação; registrar data de coleta separadamente se necessário. Não aplicar à v1 a regra de duas técnicas exigida da v2.

### Push e metadados

`push_prompt_to_langsmith(prompt_name, prompt_data)` receberá o nome simples e o objeto interno. `main()` deve validar o YAML e os nomes antes de qualquer mutação remota. Para este desafio, publicar apenas `bug_to_user_story_v2` no handle definido; evitar repetir o prefixo do usuário.

Construir `ChatPromptTemplate.from_messages` com `system_prompt` e `user_prompt`, conforme a proposta de exemplos no system da seção 6. Validar que as variáveis resolvidas sejam exatamente `bug_report` e que a renderização local funcione.

Chamar `Client.push_prompt` com identificador final, `object=prompt`, `is_public=True`, `description` e `tags`. Incluir técnicas nas tags e no `readme` do prompt no Hub; `techniques_applied` pertence ao YAML e não é um argumento arbitrário do método. Versão/proveniência podem constar no `readme`, e a iteração em `commit_description`. Não passar um parâmetro genérico `metadata=` inexistente nessa assinatura.

Registrar URL/commit retornados e verificar publicação pública, conteúdo das mensagens e variáveis por leitura posterior. Push bem-sucedido não comprova nota ou fidelidade do conteúdo publicado.

As assinaturas foram conferidas também no [código oficial do SDK LangSmith v0.13.0](https://github.com/langchain-ai/langsmith-sdk/blob/v0.13.0/python/langsmith/client.py), correspondente ao requirements, porque a documentação corrente pode mostrar versões posteriores. Referências de interface: [pull_prompt](https://reference.langchain.com/python/langsmith/client/Client/pull_prompt) e [push_prompt](https://reference.langchain.com/python/langsmith/client/Client/push_prompt).

### Dataset, experimentos e tracing

Com o projeto padrão, o dataset chama-se `mba-ia-pull-evaluation-prompt-eval`. A criação/reutilização e os experimentos já estão implementados; não duplicar essa lógica no push. O prefixo do experimento será `lucaskawasaki-bug_to_user_story_v2`, com identificação própria gerada pelo SDK. O avaliador usa `max_concurrency=1`.

Confirmar 15 exemplos e referências corretas, cinco feedbacks por exemplo, médias e árvore de execução. Selecionar pelo menos um caso simples, um médio e um complexo para evidências de tracing, incluindo entrada, mensagens, saída, chamadas dos juízes e notas. Tracing mostra as operações observáveis e justificativas retornadas pelos juízes; não revela raciocínio interno oculto do modelo.

O link impresso pelo avaliador depende de acesso ao workspace. A entrega exige link público do dataset com experimentos ou screenshots, conforme README. Planejar `Client.share_dataset(dataset_name=...)` e guardar a URL retornada uma vez, se essa for a opção escolhida em Q8; verificar acesso sem autenticação. Publicar o prompt não publica automaticamente dataset e traces. A comprovação visual dos três traces pode precisar de capturas próprias, mesmo com dataset compartilhado. Não executar compartilhamento nesta etapa.

## 6. Estratégia de Prompt Engineering

### Diagnóstico da v1

O system define apenas um assistente genérico; pede uma user story sem formato, critérios verificáveis, delimitação entre fatos/sugestões ou exemplos. O bug aparece em duas mensagens, inclusive dentro do system. Isso duplica conteúdo e mistura dados da tarefa com instruções. A v2 deve manter regras estáveis no system e relato variável somente no user, claramente identificado como dado.

### Leitura do dataset

| Exemplos / complexidade | Conteúdo observado | Exigência para a v2 |
| --- | --- | --- |
| 1–5, simples | Carrinho/produto 1234; email sem @; perfil iOS em paisagem; contagem 50 versus 42; imagens Safari versus Chrome. | História objetiva, persona contextual, comportamento corrigido e critérios observáveis, sem inventar causa técnica. |
| 6–8, médios | Webhook com HTTP 500; vendas acima de 1000 registros, timeout 120s e índice ausente; autorização de `/api/users/:id`. | Preservar endpoints, condições, dados expostos, severidade e evidências; cobrir fluxo esperado e falha relevante. |
| 9–12, médios | Desconto sobre produtos; ANR Android; concorrência/estoque; modal com z-index inferior ao menu em <768px. | Manter cálculos, limites e condições originais; distinguir comportamento necessário de solução técnica sugerida. |
| 13, complexo | XSS no cupom; 504/cobrança sem pedido; limite de cupom não atômico; loading infinito. | Uma história principal com critérios agrupados para os quatro problemas, contexto e impacto reportados, prevenção de perdas e tarefas sugeridas. |
| 14, complexo | N+1/SLA 3s; MRR divergente; cache 24h; CSV causando OOM. | Cobertura de todos os componentes e números dados, sem inventar fórmula contábil aprovada nem infraestrutura. |
| 15, complexo | Conflitos offline; anexos interrompidos; operações fora de ordem; 1500 operações e memória excessiva. | Preservar dados, sequência e status reais de sincronização, impactos e limites informados; não impor stack ausente. |

Há problemas concretos nas referências: o exemplo 7 introduz meta de 30 segundos não informada; o 11 introduz reserva de 15 minutos; o 12 exige largura de modal de 90%; o 15 introduz React Native, WatermelonDB, lotes de 50 e checkpoints de 5MB. A referência 4 termina com aspas textuais incompletas, embora o JSONL seja válido. A 14 mistura expectativas de cache em tempo real/5 minutos e acrescenta limites de CPU/usuários. Não copiar esses detalhes como fatos nem “corrigir” o dataset.

O input 14 também apresenta contagens de queries descritas de formas diferentes (101 e três grupos de 100); preservar a evidência e sinalizar a divergência relevante, em vez de inventar uma conciliação. O gerador não recebe `metadata.complexity`: o nível de detalhe deve ser inferido do próprio relato.

### Técnicas recomendadas

**Few-shot Learning + Role Prompting**, conforme Q4.

Role Prompting definirá um Product Manager/Analista de Requisitos experiente em transformar defeitos em valor para o usuário, critérios testáveis e comunicação com engenharia. A persona terá responsabilidades e limites concretos: preservar evidências, cobrir o bug, não inventar decisões de produto, distinguir recomendações de requisitos. Isso é especialmente útil porque a tarefa demanda tradução de sintomas técnicos para necessidades de usuários.

Não recomendo ReAct, pois não há ferramentas no target; Tree of Thought acrescentaria exploração desnecessária a uma transformação textual; CoT explícito aumentaria verbosidade e poderia misturar raciocínio com o artefato final. Um roteiro de seções ajuda a organização, mas não será contado artificialmente como técnica adicional. Não exigir exposição de raciocínio interno.

Recomendo **três exemplos sintéticos completos e diferentes dos 15 exemplos avaliados**:

1. Bug simples em outro domínio, como filtro de agenda ignorado: saída curta com persona, valor e critérios objetivos.
2. Bug médio de salvamento com contexto parcial: demonstrar preservação de dados técnicos e lacunas, sem inventar SLA ou causa raiz.
3. Bug complexo em outro domínio, com múltiplos sintomas e impactos: demonstrar cobertura agrupada, contexto factual e tarefas técnicas explicitamente sugeridas.

Cada exemplo deve conter relato e resposta final, com dados suficientes para sustentar sua própria saída. Não copiar referências nem apenas trocar IDs de exemplos do dataset. Distribuir sucesso, falha e informação ausente nos exemplos. Usar a análise do dataset para aprender o tipo de tarefa, mantendo clara a diferença entre avaliação conhecida e evidência de generalização.

### Esquema proposto e montagem

Preservar o padrão já usado pela v1: mapeamento externo `bug_to_user_story_v2` e campos internos abaixo. Não criar um contêiner `metadata` para `techniques_applied`, pois o validador existente lê esse campo diretamente.

| Campo interno | Tipo / conteúdo previsto |
| --- | --- |
| `description` | String não vazia sobre conversão de bugs para User Stories. |
| `system_prompt` | String multilinha com persona, regras, contrato de saída, edge cases e três pares few-shot completos. |
| `user_prompt` | String contendo apenas a solicitação do caso atual e `{bug_report}` delimitado, sem duplicação no system. |
| `version` | String `v2`. |
| `created_at` | Data real de criação, como string, sem reaproveitar a data da v1. |
| `tags` | Lista de strings sobre domínio/tarefa e técnicas. |
| `techniques_applied` | Lista de técnicas distintas; proposta: `few-shot` e `role-prompting`. |

Exemplos no texto do system dispensam um campo de exemplos que o push poderia esquecer de renderizar. A alternativa de mensagens human/assistant separadas é legítima, mas requer contrato e montagem adicionais; Q4 torna a escolha explícita. Nenhum YAML é criado nesta etapa.

### Contrato de saída e edge cases

Saída em português e Markdown, iniciando pela User Story no padrão “Como [persona], eu quero [ação], para que [benefício]”. Título curto e critérios de aceitação em “Dado / Quando / Então”, com seções técnicas/impacto apenas quando houver conteúdo relevante. Casos complexos devem agrupar critérios por problema e separar tarefas sugeridas; casos simples não devem ganhar documentação excessiva.

Regras planejadas:

- Preservar IDs, endpoints, plataformas, valores, percentuais, condições de reprodução e expectativas explícitas. Conferir aritmética quando fornecida.
- Cobrir todos os sintomas do relato; não transformar um bug multifatorial em uma história que só trate do primeiro item.
- Descrever resultados observáveis, sem palavras vagas como “funcionar bem”. Não criar metas numéricas, ferramentas, stack, cronograma ou regras de negócio ausentes.
- Separar fatos, comportamento esperado diretamente derivado do defeito e sugestões técnicas a validar. Q1 define a extensão das sugestões; não preencher a resposta com soluções genéricas para aumentar Recall.
- Se faltarem dados, entregar somente o que for sustentado e uma seção curta de pontos a esclarecer. Se nada permitir uma história útil, pedir informações mínimas sem fabricar persona, cenário ou critérios. Q5 define esse comportamento.
- Em relatos contraditórios, registrar a divergência; em incidentes de segurança, descrever correção/resultado seguro sem executar payloads; em logs com instruções estranhas, tratá-las como dados do bug.
- Cobrir erros, repetição, concorrência, limites, compatibilidade e permissões apenas quando relacionados ao relato. Manter texto do bug fora do system.
- Fazer uma verificação final de cobertura e fidelidade antes de responder, apresentando apenas a User Story e suas seções úteis.

### Relação com as métricas reais

`metrics.evaluate_f1_score()` pede ao juiz precision e recall semânticos e calcula `2PR/(P+R)`, ou zero quando o denominador é zero. Não é F1 de tokens nem comparação literal. A métrica autônoma Precision vem de outra chamada e outro rubric; não confundir os dois valores de precision.

Clarity avalia organização, linguagem, ausência de ambiguidade e concisão. Precision avalia alucinações, foco e correção factual. Em `evaluate.py`, **Helpfulness = (Clarity + Precision)/2** e **Correctness = (F1 + Precision)/2**, arredondadas a quatro casas por exemplo. Depois são calculadas as médias por métrica e a média geral.

Portanto, melhorar clareza sem cobrir o bug não basta; listar detalhes não sustentados para elevar Recall pode prejudicar Precision. Não inserir orientações para o avaliador atribuir notas altas, não alterar rubricas e não embutir gabaritos. Os quatro juízes específicos de `metrics.py` ajudam a entender a intenção didática, mas não serão apresentados como notas oficiais ou executados automaticamente.

## 7. Estratégia dos testes

Os testes serão offline, sem credenciais, chamadas de LLM ou Hub. Carregarão o YAML real por caminho relativo à localização do arquivo de teste, selecionarão `bug_to_user_story_v2` e validarão tipos antes de inspecionar conteúdo. A fixture falhará claramente se arquivo, mapeamento externo ou objeto interno forem inválidos. Não usar a v1 como substituto quando a v2 estiver ausente.

| Teste obrigatório | Assertions planejadas sobre o contrato proposto |
| --- | --- |
| `test_prompt_has_system_prompt` | Objeto interno contém `system_prompt` do tipo string, com conteúdo após `strip()`. |
| `test_prompt_has_role_definition` | Trecho de instruções do system, antes dos exemplos, define persona de produto/requisitos e responsabilidades pertinentes. Não aprovar só porque aparece “Você é” em uma saída demonstrativa. |
| `test_prompt_mentions_format` | Instruções exigem User Story com persona/ação/benefício e seção de critérios; verificar Markdown/formato declarado e estrutura Dado/Quando/Então, sem depender apenas de ocorrência dentro de exemplos. |
| `test_prompt_has_few_shot_examples` | Identificar blocos numerados de exemplo e pelo menos dois pares completos de entrada/saída não vazios; proposta terá três. Confirmar que são demonstrativos, não apenas menção à expressão few-shot. |
| `test_prompt_no_todos` | Percorrer textos relevantes de todo o objeto do prompt e rejeitar marcadores de pendência como `[TODO]`, `TODO` isolado e placeholders de implementação. Não rejeitar a palavra portuguesa “todos”; manter compatibilidade com a busca literal de `TODO` no system feita pelo helper. |
| `test_minimum_techniques` | `techniques_applied` é lista de strings distintas, inclui `few-shot` e pelo menos uma técnica adicional aceita; verificar também evidência estrutural da técnica escolhida. Duas tags duplicadas não contam. |

Reutilizar `validate_prompt_structure()` no objeto interno, complementando suas lacunas. Assertions devem refletir o contrato aprovado em Q4; não impor um campo `examples` que não exista nem testar somente strings decorativas.

Testes adicionais pertinentes, no mesmo `tests/test_prompts.py`, sem criar uma arquitetura de testes extensa:

- Montar o template da mesma forma usada no push, verificar `input_variables == ['bug_report']` e renderizar um relato com chaves, Unicode e múltiplas linhas, sem chamada de modelo. Confirmar que o relato aparece só na mensagem user.
- Validar rejeição de YAML com tipos errados, técnicas duplicadas, variáveis inesperadas e conteúdo obrigatório vazio, antes de publicar.
- Usar mock de `Client` e diretório temporário para contratos de pull/push: identificador correto, flag público, extração sem perda, `is_public=True`, metadados e falha de gravação/API retornando insucesso. Nenhuma escrita de teste deve substituir a v1 do repositório.

Esses testes exercitam riscos de integração concretos. A qualidade final continuará sendo demonstrada nos experimentos, e não por contagem de palavras-chave. `pytest` no estado atual não foi executado e os seis `pass` não constituem validação.

## 8. Ordem de implementação

A tabela abaixo registra a sequência aprovada. O acompanhamento no início deste documento distingue etapas locais concluídas e etapas externas pendentes; as nove respostas já foram incorporadas.

| Fase | Arquivos envolvidos | Alterações/ações esperadas | Como validar | Riscos |
| --- | --- | --- | --- | --- |
| 1 — Configuração e entendimento | Este plano; `.env` local; leitura de `.env.example`, `requirements.txt`, protegidos | Responder seção 11, preservar baseline, criar `venv/`, instalar versões fixadas e configurar OpenAI/LangSmith. Manter templates/dependências versionados inicialmente intactos. | Python >=3.10, `pip check`, confirmação de provider/modelos/endpoint sem exibir segredos. | Incompatibilidade transitiva, variáveis exportadas antigas, região errada e acesso da conta. |
| 2 — Pull | `src/pull_prompts.py`; saída `prompts/bug_to_user_story_v1.yml` | Implementar corpos, ler semente pública, validar tipo/papéis, salvar esquema local e proveniência disponível. | Mock offline, execução real de pull, reload e comparação de mensagens/variáveis. | Conteúdo remoto diferente, perda de mensagens, metadados inventados, falha de escrita. |
| 3 — Prompt otimizado | `prompts/bug_to_user_story_v2.yml` | Criar persona, regras, formato, três exemplos inéditos e metadados compatíveis. | Leitura crítica dos exemplos, correspondência factual, renderização local. | Gabarito contaminando prompt, pouca cobertura de bugs complexos, extensão excessiva. |
| 4 — Testes | `tests/test_prompts.py`; validação local em `src/push_prompts.py` | Implementar seis testes, verificações de contrato e casos de falha significativos. | `pytest tests/test_prompts.py`, `pytest -q`; erros claros para entradas inválidas. | Aprovação falsa por testes frágeis; divergência entre YAML testado e template publicado. |
| 5 — Push | `src/push_prompts.py`; v2; README para registro posterior | Implementar publicação pública, descrição/tags/técnicas e URL/commit. | Mock, execução real, leitura posterior e acesso público ao prompt. | Handle/workspace incompatível; publicar conteúdo incompleto; metadados não enviados. |
| 6 — Avaliação | Executar `src/evaluate.py`; ler protegidos e dataset; serviços remotos | Pré-teste pago pequeno se aprovado, conferir dataset e executar rodada completa com modelos fixos. | 15 saídas, 75 feedbacks, scores válidos, médias >=0.8 e exit code. | Custo, rate limits, JSON inválido do juiz, dataset incompleto e tensão referência/fidelidade. |
| 7 — Iterações de melhoria | v2; testes se contrato mudar; README como registro | Planejar 3–5 iterações documentadas; corrigir causas observadas, testar, publicar e avaliar a cada versão. Registrar modelo/commit/custo/notas. | Comparar experimentos completos sob mesmo juiz/dataset e inspecionar pior caso por complexidade. | Overfitting ao dataset conhecido, troca de juiz para elevar nota, gasto acima do limite. |
| 8 — Documentação e evidências | `README.md`; v1/v2; links/capturas conforme Q8 | Preencher técnicas, resultados, execução Windows, diferenças v1/v2, limitações, evidências de três traces e entrega no fork público. | Reproduzir instruções, conferir links/capturas e diff dos protegidos. | Links privados, imagens ignoradas pelo Git, segredos em logs ou alegações sem execução. |

Se o limite de orçamento for alcançado com alguma métrica abaixo do alvo, registrar a pendência e discutir a próxima rodada. Não declarar conclusão, baixar o limiar ou alterar o dataset. Uma revisão sem alteração necessária pode documentar estabilização; não introduzir mudanças artificiais apenas para contabilizar iterações.

## 9. Estratégia de validação

### Comandos previstos

Executar na raiz do projeto, **somente na futura etapa de implementação**. Os comandos abaixo são planejamento, não relato de execução.

Preparação no PowerShell:

```powershell
python --version
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

Se a política local bloquear ativação, usar diretamente `venv\Scripts\python.exe` e `venv\Scripts\pytest.exe`, sem alterar políticas do sistema. Criar `.env` a partir do template somente se não existir e preencher chaves localmente, com `LLM_PROVIDER=openai` e modelos escolhidos. Não sobrescrever um `.env` existente.

Validação offline e fluxo principal:

```powershell
pytest tests/test_prompts.py
pytest -q
python src/pull_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

Na execução real, a v2 deve existir antes dos testes; o pull ocorre antes da autoria da v2 e o push somente após os testes. O bloco reúne os comandos obrigatórios, enquanto a ordem operacional detalhada é a seção 8. Não existe flag `--dry-run`, seletor de v1, limite de exemplos ou argumento de modelo nesses CLIs; não documentar opções inexistentes.

`python src/metrics.py` é uma demonstração existente com sete chamadas de juiz, não uma suíte offline; não executar como teste rotineiro. A suíte `pytest -q` hoje só encontra `tests/test_prompts.py`. Um pré-teste pago pode usar futuramente uma sessão interativa com as funções públicas já existentes para geração + três juízes em um caso, sem editar o avaliador e sem apresentá-lo como rodada oficial.

### Aceitação dos experimentos

1. Conferir nome e conteúdo dos 15 exemplos no dataset remoto. A igualdade deve considerar entradas e referências; metadados locais não são enviados pelo script.
2. Associar hash/commit do prompt, snapshots de modelo, provider, data e URL à iteração. Cada nova versão requer push seguido de novo processo de avaliação.
3. Exigir 15 respostas não vazias e cinco notas finitas no intervalo [0,1] por exemplo. Descartar como evidência de aprovação qualquer execução com erros, ausências ou dataset errado; guardar o histórico para diagnóstico.
4. Conferir cada uma das cinco médias >=0.8 e a média geral >=0.8, usando valores completos exportados/visíveis no experimento, não só o terminal arredondado a duas casas.
5. Analisar também os piores exemplos e os três estratos. Atingir média não basta para afirmar que cada caso passou; aplicar a decisão de Q2 na declaração final.
6. Investigar comentários e traces para distinguir erro técnico, problema de cobertura, falta de clareza e extrapolação. Fazer mudanças orientadas pela causa, sem selecionar apenas resultados favoráveis.
7. Verificar acesso público às evidências e legibilidade de pelo menos três traces com entrada, saída e feedback.

### Preservação do repositório

Comandos de inspeção previstos ao final:

```powershell
git status --short
git diff --check
git diff a94ce443299b4928d0f1e08cecdacf7a36ff5fb1 -- src/evaluate.py src/metrics.py src/utils.py datasets/bug_to_user_story.jsonl
git ls-files -- .env .env.local
git check-ignore .env
```

O diff dos quatro protegidos deve ficar vazio; verificar também mudanças staged e arquivos novos antes do commit. Revisar o conteúdo exato de código, YAML, README e capturas para impedir credenciais versionadas; ignorar `.env` sozinho não garante isso.

Hashes SHA-256 locais registrados para confirmação posterior:

| Arquivo protegido | SHA-256 |
| --- | --- |
| `src/evaluate.py` | `4F2A071BD7D70D70FC32D3F2C3BE7B69B9281B253DB7DDAA2C9EAED2C3A47517` |
| `src/metrics.py` | `CA785F565CEFCFE5439752904B1A3F2FB6CB332FF4E20259B8ABC8CD3D6729C4` |
| `src/utils.py` | `6597BCA796C2F9A6E887035D6630D2AA1D869F64A4F390F361602DE5E94C85EF` |
| `datasets/bug_to_user_story.jsonl` | `5B33034771AB6F0BDFDB5D24C7DEF12CE0E18E95DC51E0B185E742D7117BFA4D` |

## 10. Critérios de conclusão

Checklist atualizado após implementação local; itens externos permanecem pendentes:

- [x] Ambiente Python 3.10+ funcional e dependências fixadas verificadas.
- [ ] OpenAI configurada para geração e avaliação; Gemini não utilizado.
- [ ] Pull de `leonanluppi/bug_to_user_story_v1` funcionando com o flag exigido.
- [ ] v1 salva corretamente em YAML, com fidelidade às mensagens remotas.
- [x] v2 criada e renderizada localmente, com única variável dinâmica `bug_report`; qualidade semântica ainda não medida.
- [x] Few-shot presente com exemplos completos de entrada/saída.
- [x] Segunda técnica presente no conteúdo e em `techniques_applied`.
- [x] Fidelidade, formato, informação incompleta e edge cases contemplados nas instruções.
- [x] Os seis testes obrigatórios implementados com assertions efetivas.
- [x] Testes obrigatórios e validações de contrato passando sem rede/LLM pago.
- [ ] Push funcionando com descrição, tags e técnicas.
- [ ] Prompt publicado publicamente em `lucaskawasaki/bug_to_user_story_v2`.
- [ ] Dataset remoto conferido com os 15 exemplos originais.
- [ ] Experimento completo com 15 saídas e 75 feedbacks válidos, sem falhas ocultas.
- [ ] Helpfulness >=0.8.
- [ ] Correctness >=0.8.
- [ ] F1-Score >=0.8.
- [ ] Clarity >=0.8.
- [ ] Precision >=0.8.
- [ ] Média das cinco métricas >=0.8; escopo por exemplo/agregado declarado conforme Q2.
- [ ] Experimentos disponíveis no LangSmith e vinculados às versões avaliadas.
- [ ] Tracing detalhado de pelo menos três exemplos, idealmente um de cada complexidade.
- [ ] 3–5 iterações planejadas/documentadas conforme expectativa do README, ou diferença justificada com evidências e orçamento.
- [x] README com “Técnicas Aplicadas (Fase 2)”, “Resultados Finais” e “Como Executar”, com resultados externos identificados como pendentes.
- [ ] README explica e exemplifica as técnicas, compara v1/v2 e registra resultados reais, modelos e comandos.
- [ ] Link público do dataset/experimentos ou screenshots acessíveis; screenshots das notas atingidas e evidências dos três traces.
- [ ] Fork público no GitHub contém os entregáveis finais e evidências acessíveis.
- [x] Nenhuma credencial adicionada aos arquivos candidatos a versionamento; nenhum log/captura publicado.
- [x] Nenhum dos quatro arquivos protegidos modificado.

### Segunda revisão do plano contra o enunciado

Revisão realizada após redigir as onze seções, confrontando o pedido anexado e o README com os contratos do código. **Nenhum requisito obrigatório ficou de fora do planejamento.** Esta confirmação diz respeito à cobertura do plano, não à conclusão da implementação ou obtenção de notas.

Conferência final desta etapa: o Git mostrou somente `IMPLEMENTATION_PLAN.md` como arquivo novo, sem alterações em arquivos versionados. Os quatro hashes protegidos foram recalculados e permaneceram iguais aos registrados na seção 9.

| Requisito conferido | Cobertura |
| --- | --- |
| Análise de todo o repositório e inventário por arquivo | Seção 2; dataset detalhado na seção 6. |
| Somente plano nesta etapa, sem implementação/instalação/push/avaliação paga | Declaração inicial e comandos explicitamente futuros. |
| Pull exato, flag público, YAML local e v2 separada | Seções 3, 5, 6 e 8. |
| OpenAI exclusiva, modelos, chaves e custo x qualidade | Seção 4 e Q3. |
| Handle `lucaskawasaki`, publicação pública, metadados, dataset, experimentos e tracing | Seções 3 e 5. |
| Few-shot obrigatório, segunda técnica, fidelidade e edge cases | Seção 6 e Q1/Q4/Q5. |
| Seis testes nomeados e assertions ligadas ao YAML real | Seção 7. |
| Oito fases com arquivos, ações, validação e riscos | Seção 8. |
| Quatro comandos obrigatórios e outras validações pertinentes | Seção 9. |
| Cinco métricas e média >=0.8, três traces, README e evidências | Seções 9 e 10. |
| Preservação dos protegidos e registro de limitações | Seções 2, 9 e 10. |
| Perguntas não triviais no formato solicitado | Seção 11, com recomendações e respostas em aberto. |

## 11. Perguntas para mim

Respostas recebidas e incorporadas ao acompanhamento no início do documento. Os contextos, alternativas e recomendações originais abaixo ficam preservados como histórico; prevalecem as respostas do usuário. Não incluir chaves de API.

### Q1:

**Contexto:** As referências introduzem requisitos ausentes nos bugs, enquanto Precision penaliza invenções e F1 considera cobertura da referência. Há exemplos concretos na seção 6. O dataset e as métricas permanecerão intactos.

**Alternativas:** (A) Restringir estritamente a saída aos fatos e consequências necessárias; (B) acrescentar sugestões técnicas úteis, claramente separadas e sujeitas a validação, sem inventar SLAs, stacks ou regras de produto. Se persistir conflito com a nota, registrar e discutir com o responsável pelo desafio.

**Recomendação:** B, com núcleo factual rigoroso e sugestões curtas, sustentadas pelo problema. Não reproduzir exigências arbitrárias do gabarito como fatos e não adulterar os protegidos para obter nota.

**Minha resposta:** B

### Q2:

**Contexto:** O avaliador aprova quando a média de cada métrica no dataset e a média geral atingem 0.8; ele não exige isso nos 15 exemplos individualmente. A frase “todas as métricas” pode ser entendida de modo mais rigoroso na entrega.

**Alternativas:** (A) Adotar o critério agregado implementado, com auditoria e divulgação dos resultados individuais; (B) acrescentar à conclusão a exigência de todas as cinco notas >=0.8 em cada um dos 15 exemplos, sem mudar o avaliador.

**Recomendação:** A como critério oficial do código, acompanhado de análise obrigatória dos piores casos e correção de falhas materiais. Se desejar B, prever mais iterações/custo e explicitar a validação adicional no README.

**Minha resposta:** A

### Q3:

**Contexto:** Cada rodada completa envolve aproximadamente 60 chamadas de LLM; o juiz é usado três vezes por exemplo. Não foi verificado acesso da sua conta aos modelos e nenhuma chamada paga foi feita.

**Alternativas:** (A) GPT-4.1 mini na geração + GPT-4.1 na avaliação; (B) GPT-4.1 nos dois papéis para priorizar qualidade inicial; (C) mini nos dois papéis para reduzir custo, reconhecendo limitações do juiz. Em qualquer opção, definir limite total em dólares e possibilidade de escalonar o gerador.

**Recomendação:** A com snapshots, pré-teste pequeno e teto inicial de US$ 5 para chamadas OpenAI, sujeito à sua definição. Não executar além do teto sem nova decisão. Manter o juiz fixo durante a comparação.

**Minha resposta:** A

### Q4:

**Contexto:** Few-shot é obrigatório, mas a segunda técnica e a organização dos exemplos admitem escolhas. O esquema atual possui strings system/user; não há loader para um campo estruturado de exemplos.

**Alternativas:** (A) Role Prompting como segunda técnica e três pares few-shot no system, mantendo dois campos de mensagem; (B) Role Prompting e pares human/assistant separados, estendendo YAML e montagem do push; (C) outra segunda técnica da lista, com justificativa e revisão do contrato.

**Recomendação:** A. Mantém o esquema simples, garante exemplos enviados ao modelo e permite testar o conteúdo efetivo. Usar exemplos sintéticos inéditos em todas as opções.

**Minha resposta:** A

### Q5:

**Contexto:** O target é uma única chamada, sem conversa de esclarecimento. Relatos insuficientes ou contraditórios precisam de um comportamento definido, e bugs complexos admitem uma história principal ou várias histórias independentes.

**Alternativas:** (A) Uma história principal com critérios agrupados; quando faltarem informações, entregar o que for sustentado e listar dúvidas, pedindo esclarecimento sem história se não houver base mínima; (B) produzir múltiplas histórias para bugs complexos e priorizar perguntas antes de uma história em relatos incompletos.

**Recomendação:** A, compatível com a forma das referências e com o target de chamada única. Não preencher dados faltantes por suposição silenciosa.

**Minha resposta:** A

### Q6:

**Contexto:** O README exige comparação entre v1 e v2, mas o CLI só avalia v2. A comparação pode ser qualitativa ou também numérica; números ilustrativos do enunciado não são um baseline real.

**Alternativas:** (A) Comparação qualitativa de instruções/exemplos/saídas, com notas oficiais somente da v2; (B) também executar baseline pago da v1 usando a função existente `run_experiment` em uma sessão controlada, sem modificar `evaluate.py` ou publicar v1 sob o nome v2.

**Recomendação:** B se couber no orçamento: mesmo dataset, gerador e juiz, mais uma rodada de aproximadamente 60 chamadas, usando a semente original. Caso contrário, A explicitamente identificada como comparação qualitativa.

**Minha resposta:** A

### Q7:

**Contexto:** Só cinco arquivos de implementação foram solicitados, além do YAML v1 gerado pelo pull. `.env.example` ainda recomenda Google; `requirements.txt` inclui sua integração. Nenhuma dessas condições impede usar exclusivamente OpenAI.

**Alternativas:** (A) Manter ambos intactos, configurar `.env` local e explicar a escolha no README; (B) estender posteriormente o escopo para adaptar `.env.example` a OpenAI e discutir separadamente eventual remoção da dependência Google.

**Recomendação:** A. Preserva o scaffold e evita mudanças desnecessárias. Configurar OpenAI não exige remover o suporte multiprovider já pronto. Se houver incompatibilidade real de dependências, trazê-la para discussão antes de alterar versões.

**Minha resposta:** A

### Q8:

**Contexto:** A URL do experimento é privada ao workspace. O README aceita dataset público ou screenshots, e pede capturas das notas e traces. `.gitignore` ignora `screenshots/` e `results/`; apontar imagens nessas pastas sem versioná-las quebraria a entrega.

**Alternativas:** (A) Compartilhar dataset/experimentos e incluir imagens em uma pasta de documentação versionada, como `docs/evidencias/`; (B) manter dataset privado e entregar capturas versionadas; (C) usar imagens hospedadas acessíveis, sem acrescentar arquivos locais além do escopo.

**Recomendação:** A, verificando o conteúdo público antes e permitindo a pasta de evidências como extensão explícita do escopo futuro. Conservar `.gitignore` e não publicar segredos. Dataset sintético e resultados desta tarefa são o conteúdo previsto; nenhum compartilhamento foi executado agora.

**Minha resposta:** A

### Q9:

**Contexto:** A região e as permissões do workspace não podem ser inferidas do handle. O nome de projeto padrão será reutilizado pelo avaliador, que não verifica o conteúdo de um dataset já existente.

**Alternativas:** (A) Usar o projeto padrão em um workspace onde o dataset esteja ausente ou conferido; (B) definir projeto específico desta execução para evitar colisões. Em ambos os casos, informar região e, somente se necessário, workspace ID não secreto.

**Recomendação:** A se o ambiente estiver limpo; B se já houver experimentos/dataset de outro trabalho. Manter o projeto escolhido constante nas iterações comparáveis. Configurar a API key apenas no `.env`, nunca nesta resposta.

**Minha resposta:** A
