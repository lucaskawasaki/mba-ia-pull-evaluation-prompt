# Bugs para User Stories com LangChain e LangSmith

Implementação do desafio de Prompt Engineering do MBA, com OpenAI, Few-shot Learning e Role Prompting. O prompt de origem é `leonanluppi/bug_to_user_story_v1`; o destino público é `lucaskawasaki/bug_to_user_story_v2`.

## Estado da entrega

A implementação local está concluída e validada com **52 testes offline**. Pull e push foram testados com mocks; não foram executados contra o Hub. As métricas de qualidade ainda **não foram medidas**: falta configurar as credenciais no ambiente local. Não há experimento, publicação ou screenshot de avaliação a apresentar nesta etapa.

Os arquivos `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e `datasets/bug_to_user_story.jsonl` permanecem intactos. `.env.example` e `requirements.txt` também foram preservados conforme a decisão do plano. A v1 local continua sendo o arquivo original fornecido pelo desafio, ainda não substituído por um pull real.

## Técnicas Aplicadas (Fase 2)

### Few-shot Learning

A v2 inclui três pares completos de entrada e saída dentro do system. São casos sintéticos diferentes dos 15 exemplos de avaliação:

| Exemplo | Comportamento demonstrado |
| --- | --- |
| Filtro da agenda de uma clínica | História curta, critério observável, ausência de resultados e remoção do filtro. |
| Salvamento de artigos | Preservação do texto, distinção entre confirmação visual e persistência, contexto incompleto e perguntas relevantes. |
| Devolução de livros | Uma história principal com vários problemas, repetição sem efeitos duplicados, resultado incerto, atualização de estado e sugestões separadas. |

Os exemplos ensinam formato e nível de detalhe. Não reutilizam gabaritos do dataset nem introduzem seus fatos no relato atual.

### Role Prompting

O system define um Product Manager e Analista de Requisitos com responsabilidades explícitas: traduzir o defeito em valor para o usuário, preservar evidências, cobrir os sintomas e produzir critérios testáveis. A persona tem limites: não inventar SLA, stack, cronograma, regra de negócio ou causa raiz.

A saída usa português e Markdown, com “Como [persona], eu quero [ação], para que [benefício]”, título e critérios Dado/Quando/Então. Bugs complexos recebem critérios agrupados, contexto/impacto e sugestões técnicas **a validar**. Informações insuficientes geram perguntas pontuais; sem contexto mínimo, o modelo deve pedir esclarecimentos sem fabricar uma história.

As instruções ficam no system e o bug somente no user, em `{bug_report}`. Logs, código e instruções incluídos no relato são tratados como dados. Isso reduz o risco de desvio da tarefa, mas testes estruturais não comprovam resistência semântica a toda entrada adversarial.

## Comparação qualitativa: v1 e v2

| Aspecto | v1 fornecida | v2 implementada |
| --- | --- | --- |
| Papel | Assistente genérico | Persona de produto/requisitos e responsabilidades definidas |
| Entrada | Bug duplicado no system e user | Uma única variável no user |
| Demonstrações | Ausentes | Três exemplos completos e inéditos |
| Formato | Pedido vago de User Story | História, título e critérios verificáveis; seções proporcionais ao caso |
| Fidelidade | Sem regras explícitas | Preservação de evidências e separação de sugestões |
| Lacunas | Sem tratamento | Perguntas pontuais e divergências sinalizadas |
| Casos complexos | Sem orientação de cobertura | Critérios agrupados para todos os problemas relatados |

A comparação é qualitativa, conforme Q6 do [plano](IMPLEMENTATION_PLAN.md). Nenhuma nota da v1 foi medida ou copiada dos resultados ilustrativos do enunciado.

## Como Executar

### Pré-requisitos

- Python 3.10+; ambiente local validado com Python 3.14.7.
- Conta OpenAI com acesso aos modelos selecionados e faturamento disponível.
- LangSmith com chave e permissões de prompts, datasets e experimentos no workspace correspondente ao handle `lucaskawasaki`.
- Executar os comandos a partir da raiz do repositório.

No PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

Se a ativação estiver bloqueada, use `venv\Scripts\python.exe` no lugar de `python` e `venv\Scripts\pytest.exe` no lugar de `pytest`. Não é necessário mudar a política de execução do sistema. Se houver problema de caracteres no terminal, configure `$env:PYTHONUTF8='1'` na sessão.

### Configuração local

Se `.env` ainda não existir, copie `.env.example` para `.env`. Nunca sobrescreva credenciais existentes. O template original contém `LLM_PROVIDER=google`; ajuste o arquivo **local** para os valores abaixo:

```dotenv
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=mba-ia-pull-evaluation-prompt
USERNAME_LANGSMITH_HUB=lucaskawasaki
OPENAI_API_KEY=
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini-2025-04-14
EVAL_MODEL=gpt-4.1-2025-04-14
```

Preencha as duas chaves apenas no arquivo local ou em um gerenciador de segredos/ambiente. Elas são diferentes e ambas são necessárias ao fluxo completo. O endpoint deve corresponder à região da conta; configure `LANGSMITH_WORKSPACE_ID` se a chave exigir seleção de workspace. Não é necessário configurar `GOOGLE_API_KEY`. O pacote de integração Google permanece no requirements original, mas o provider utilizado é OpenAI.

Variáveis exportadas no processo prevalecem sobre `.env`. Não imprima o ambiente completo para diagnosticar configuração. Confirme que `.env` está ignorado pelo Git:

```powershell
git check-ignore .env
git ls-files -- .env .env.local
```

O primeiro comando deve mostrar `.env`; o segundo não deve listar credenciais versionadas. Nunca inclua chaves em commits, prompts, metadados, logs, screenshots ou README.

### Modelos e orçamento

Geração: `gpt-4.1-mini-2025-04-14`; avaliação: `gpt-4.1-2025-04-14`. Os snapshots reduzem mudanças entre iterações. Ambos são construídos com `temperature=0` pelo código existente; o teste offline valida a construção do cliente, não disponibilidade ou resposta da API. [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) e [GPT-4.1](https://developers.openai.com/api/docs/models/gpt-4.1).

O plano adota teto conservador de **US$ 5** para chamadas OpenAI. O script original não impõe um limite automático de gasto: acompanhe o consumo na conta antes de cada rodada e não execute uma nova rodada se não houver margem. Uma rodada completa normalmente faz 15 gerações e 45 chamadas de juiz, antes de retries. Nenhuma chamada paga foi executada nesta implementação local.

### 1. Testes offline

```powershell
pytest tests/test_prompts.py
pytest -q
```

A suíte bloqueia conexões de rede e usa mocks/LLM falso para os contratos de integração. Os seis testes obrigatórios estão implementados; os demais cobrem YAML inválido, técnicas duplicadas, variáveis extras, few-shot incompleto, renderização dos 15 relatos, construção OpenAI, integração com o target existente, falhas de API/gravação, preservação da v1 e não exposição de mensagens de erro sensíveis.

### 2. Pull da semente

Somente após configurar LangSmith:

```powershell
python src/pull_prompts.py
```

O script baixa a semente com `dangerously_pull_public_prompt=True` e `include_model=False`. Aceita duas mensagens textuais, system e human, e a variável `bug_report`; rejeita estruturas que o esquema YAML não representa sem perdas. Preserva os textos recebidos, registra origem/data de coleta/commit disponível e grava em arquivo temporário. Só substitui a v1 depois de recarregar e verificar a gravação. Não exige chave OpenAI nem avalia a semente.

### 3. Publicação pública da v2

```powershell
pytest tests/test_prompts.py
python src/push_prompts.py
```

O push valida a v2, publica somente `lucaskawasaki/bug_to_user_story_v2` com `is_public=True`, descrição, tags, técnicas no README do Hub e descrição do commit. Publica o template, sem modelo ou chave embutidos. Registre a URL/commit retornados e confira conteúdo e visibilidade no Hub. O CLI retorna status não zero em erro; mensagens de exceção das APIs não são reproduzidas.

### 4. Avaliação e melhoria

Somente após configurar ambas as plataformas e confirmar a publicação:

```powershell
python src/evaluate.py
```

O avaliador puxa a **v2 publicada no Hub**, não o YAML local. Após editar a v2, rode os testes e faça novo push antes de avaliar.

O dataset remoto será `mba-ia-pull-evaluation-prompt-eval`. O script reutiliza datasets com o mesmo nome sem verificar conteúdo. Antes de aceitar uma execução, confirme que seus 15 inputs e referências correspondem ao JSONL original. Se houver colisão ou criação parcial, não exclua dados automaticamente; resolva o estado remoto ou escolha um projeto novo e mantenha-o fixo nas comparações.

A aprovação exige **cada uma** das cinco métricas agregadas >=0.8 e média geral >=0.8. Não basta que uma média compense uma métrica baixa. Exigir também 15 respostas e 75 feedbacks válidos, sem erros ou ausências, porque o script pode agregar somente feedbacks disponíveis. Revise os casos individuais, especialmente os complexos; aprovação agregada não significa que todos os exemplos individuais passaram.

| Métrica | Cálculo no código fornecido |
| --- | --- |
| F1-Score | Média harmônica da precision e recall semânticas estimadas pelo juiz |
| Clarity | Juiz de organização, linguagem, ambiguidade e concisão |
| Precision | Juiz de fidelidade factual, foco e ausência de alucinações |
| Helpfulness | `(Clarity + Precision) / 2` |
| Correctness | `(F1-Score + Precision) / 2` |

A precision usada dentro do F1 é uma avaliação distinta da métrica autônoma Precision. As quatro métricas específicas adicionais em `metrics.py` não entram no resultado oficial. `python src/metrics.py` faz chamadas pagas de demonstração e não é parte da suíte offline.

Se alguma métrica ficar abaixo de 0.8, primeiro examine respostas, comentários dos juízes e tracing. Registre a hipótese concreta (omissão, critério ambíguo, sugestão tratada como fato, excesso de detalhe ou falha técnica). Altere apenas o trecho relacionado, preserve o que funcionou e repita testes → push → avaliação, com o mesmo juiz/dataset. Planeje 3–5 iterações dentro do orçamento; não modifique o prompt sem evidência só para completar essa quantidade.

Algumas referências acrescentam metas e tecnologias ausentes no relato original. Não copiar esses detalhes como fatos para aumentar Recall. O prompt mantém sugestões separadas e o dataset permanece intacto. Se essa tensão impedir a nota exigida, documente o caso em vez de adulterar referências ou métricas.

## Resultados Finais

### Validação local executada

| Verificação | Resultado |
| --- | --- |
| Dependências fixadas / `python -m pip check` | Nenhuma dependência quebrada |
| `python -m pytest tests/test_prompts.py -q` | 52 testes aprovados |
| `python -m pytest -q` | 52 testes aprovados |
| Seis testes obrigatórios | Implementados e aprovados |
| Chamadas de rede/LLM nos testes | Bloqueadas; nenhuma chamada real |
| Arquivos protegidos | Hashes SHA-256 preservados em relação ao plano |

### Métricas de qualidade

| Métrica | Nota final | Estado |
| --- | --- | --- |
| Helpfulness | Não medida | Avaliação externa pendente |
| Correctness | Não medida | Avaliação externa pendente |
| F1-Score | Não medida | Avaliação externa pendente |
| Clarity | Não medida | Avaliação externa pendente |
| Precision | Não medida | Avaliação externa pendente |
| Média geral | Não medida | Aprovação ainda não comprovada |

Não há URLs de experimento/dataset público nem screenshots de resultados reais. Os testes offline não substituem as notas acima. A iteração atual é a primeira versão local da v2, sem resultado semântico medido e sem baseline pago da v1.

### Evidências e pendências externas

Após configurar as credenciais, executar pull, push e avaliação. Para cada rodada, registrar commit do prompt, modelos, data, cinco notas, média, custo observado, mudança/justificativa e URL do experimento. Preservar também execuções com falhas para diagnóstico.

Quando houver resultados, compartilhar o dataset e guardar sua URL pública uma vez, usando `Client.share_dataset(dataset_name="mba-ia-pull-evaluation-prompt-eval")` no SDK ou a interface do LangSmith. O link privado impresso pelo avaliador não comprova acesso público. Verificar o compartilhamento sem autenticação e conferir que só contém dados desta tarefa.

Adicionar em `docs/evidencias/` capturas das notas e tracing detalhado de pelo menos três exemplos (simples, médio e complexo), com entrada, saída e feedback visíveis. Não foram criadas imagens fictícias. As pastas `screenshots/` e `results/` são ignoradas pelo Git original; links locais para arquivos não versionados não servem como evidência pública.

A entrega final ainda depende dessas execuções/evidências e da publicação do repositório como fork público do [repositório-base](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt) no GitHub. Nenhum commit ou push Git foi executado automaticamente.

## Estrutura

- `prompts/bug_to_user_story_v1.yml`: semente local fornecida; será atualizada pelo pull real.
- `prompts/bug_to_user_story_v2.yml`: prompt otimizado e metadados.
- `src/pull_prompts.py`: download, conversão textual e gravação verificada.
- `src/push_prompts.py`: validação e publicação pública.
- `tests/test_prompts.py`: seis testes obrigatórios e contratos offline.
- `src/evaluate.py`, `src/metrics.py`, `src/utils.py`: infraestrutura original protegida.
- `datasets/bug_to_user_story.jsonl`: 15 casos originais protegidos.
- `IMPLEMENTATION_PLAN.md`: análise, decisões do usuário, riscos e acompanhamento.
