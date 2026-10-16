"""Baixa a semente do desafio e salva suas mensagens sem otimizá-las."""

import os
import sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langsmith import Client

from utils import check_env_vars, load_yaml, print_section_header, save_yaml

ROOT = Path(__file__).resolve().parent.parent
PROMPT_ID = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = ROOT / "prompts" / "bug_to_user_story_v1.yml"
load_dotenv(ROOT / ".env")


def serialize_prompt(prompt: ChatPromptTemplate) -> dict:
    """Aceita apenas o contrato textual que o YAML local representa sem perdas."""
    if not isinstance(prompt, ChatPromptTemplate):
        raise ValueError("A semente deve ser um ChatPromptTemplate.")
    if prompt.input_variables != ["bug_report"] or prompt.partial_variables:
        raise ValueError("A semente deve receber somente bug_report, sem parciais.")
    if len(prompt.messages) != 2 or not isinstance(
        prompt.messages[0], SystemMessagePromptTemplate
    ) or not isinstance(prompt.messages[1], HumanMessagePromptTemplate):
        raise ValueError("Esperadas exatamente duas mensagens: system e human.")
    texts = []
    for message in prompt.messages:
        template = message.prompt
        if (
            not hasattr(template, "template")
            or template.template_format != "f-string"
            or template.partial_variables
            or not isinstance(template.template, str)
            or not template.template.strip()
        ):
            raise ValueError("Mensagem incompatível com o YAML textual do desafio.")
        texts.append(template.template)
    rebuilt = ChatPromptTemplate.from_messages([
        ("system", texts[0]), ("human", texts[1])
    ])
    probe = {"bug_report": "Relato de verificação: {texto literal} e ação."}
    if rebuilt.format_messages(**probe) != prompt.format_messages(**probe):
        raise ValueError("A conversão alteraria as mensagens da semente.")
    data = {
        "description": "Prompt semente para converter relatos de bugs em User Stories",
        "system_prompt": texts[0],
        "user_prompt": texts[1],
        "version": "v1",
        "source": PROMPT_ID,
        "pulled_at": datetime.now(timezone.utc).isoformat(),
    }
    # Somente proveniência conhecida: não serializar configurações ou segredos.
    commit = (prompt.metadata or {}).get("lc_hub_commit_hash")
    if isinstance(commit, str) and commit and all(c in "0123456789abcdef" for c in commit):
        data["source_commit"] = commit
    return {"bug_to_user_story_v1": data}


def pull_prompts_from_langsmith() -> bool:
    """Retorna False em erro e preserva o YAML anterior até validar a gravação."""
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False
    temporary = None
    try:
        prompt = Client().pull_prompt(
            PROMPT_ID,
            dangerously_pull_public_prompt=True,
            include_model=False,
        )
        document = serialize_prompt(prompt)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=OUTPUT_PATH.parent, suffix=".yml", delete=False) as f:
            temporary = Path(f.name)
        # Os helpers existentes imprimem exceções; não propagar dados de erro.
        with redirect_stdout(StringIO()):
            saved = save_yaml(document, str(temporary))
            reloaded = load_yaml(str(temporary)) if saved else None
        if not saved or reloaded != document:
            raise ValueError("Falha na verificação do YAML salvo.")
        os.replace(temporary, OUTPUT_PATH)
        print("Pull concluído: prompts/bug_to_user_story_v1.yml")
        return True
    except Exception:
        print("Falha no pull. Confira credenciais, acesso, rede e contrato das mensagens.")
        return False
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    print_section_header("PULL DO PROMPT SEMENTE")
    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
