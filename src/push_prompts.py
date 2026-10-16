"""Valida e publica a v2 pública no LangSmith, sem incluir modelo ou credenciais."""

import os
import re
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from utils import check_env_vars, load_yaml, print_section_header, validate_prompt_structure

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_NAME = "bug_to_user_story_v2"
HUB_USERNAME = "lucaskawasaki"
TECHNIQUES = {"few-shot", "role-prompting", "chain-of-thought", "tree-of-thought",
              "skeleton-of-thought", "react"}
load_dotenv(ROOT / ".env")


def build_prompt(prompt_data: dict) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])


def _texts(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _texts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _texts(item)


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """Verifica tipos antes de usar o validador fornecido pelo desafio."""
    errors = []
    if not isinstance(prompt_data, dict):
        return False, ["O conteúdo do prompt deve ser um mapeamento YAML."]
    for field in ("description", "system_prompt", "user_prompt", "version", "created_at"):
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Campo {field} deve ser uma string não vazia.")
    for field in ("tags", "techniques_applied"):
        value = prompt_data.get(field)
        if (not isinstance(value, list) or not value
                or not all(isinstance(item, str) and item.strip() for item in value)):
            errors.append(f"Campo {field} deve ser uma lista não vazia de strings.")
    if errors:
        return False, errors
    _, basic_errors = validate_prompt_structure(prompt_data)
    errors.extend(basic_errors)
    techniques = prompt_data["techniques_applied"]
    if len(set(techniques)) != len(techniques):
        errors.append("As técnicas devem ser distintas.")
    if "few-shot" not in techniques or not set(techniques) <= TECHNIQUES:
        errors.append("Inclua few-shot e técnicas reconhecidas pelo desafio.")
    if prompt_data["version"] != "v2":
        errors.append("A versão esperada é v2.")
    if any(re.search(r"\b(?:TODO|FIXME)\b|\[PREENCHER\]", text, re.IGNORECASE)
           for text in _texts(prompt_data)):
        errors.append("O prompt contém marcadores de implementação pendente.")
    examples = re.split(r"(?m)^### Exemplo \d+\s*$", prompt_data["system_prompt"])[1:]
    if len(examples) < 2:
        errors.append("Inclua pelo menos dois blocos numerados de exemplos.")
    for example in examples:
        parts = example.split("Saída:", 1)
        if (len(parts) != 2 or not parts[0].strip().startswith("Entrada:")
                or not parts[0].split("Entrada:", 1)[1].strip() or not parts[1].strip()):
            errors.append("Cada exemplo precisa de Entrada e Saída preenchidas.")
            break
    try:
        prompt = build_prompt(prompt_data)
        if prompt.input_variables != ["bug_report"]:
            errors.append("A única variável dinâmica deve ser bug_report.")
        if prompt.messages[0].prompt.input_variables:
            errors.append("O system deve conter instruções estáveis, sem variáveis.")
        if prompt_data["user_prompt"].count("{bug_report}") != 1:
            errors.append("O user deve conter bug_report exatamente uma vez.")
        if not errors:
            prompt.format_messages(bug_report='Teste de ação com {chaves} e Unicode.')
    except (ValueError, KeyError, TypeError):
        errors.append("Template inválido; confira variáveis e escape de chaves literais.")
    return not errors, errors


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        print("Prompt inválido:\n- " + "\n- ".join(errors))
        return False
    if prompt_name != PROMPT_NAME:
        print("Nome inválido: este script publica somente bug_to_user_story_v2.")
        return False
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return False
    if os.getenv("USERNAME_LANGSMITH_HUB") != HUB_USERNAME:
        print("Configure USERNAME_LANGSMITH_HUB=lucaskawasaki.")
        return False
    try:
        techniques = prompt_data["techniques_applied"]
        tags = list(dict.fromkeys(prompt_data["tags"] + techniques))
        url = Client().push_prompt(
            f"{HUB_USERNAME}/{prompt_name}",
            object=build_prompt(prompt_data),
            is_public=True,
            description=prompt_data["description"],
            tags=tags,
            readme=(f"# {prompt_name}\n\n{prompt_data['description']}\n\n"
                    f"Versão: {prompt_data['version']}\n\n"
                    f"Técnicas: {', '.join(techniques)}\n\n"
                    "Origem: leonanluppi/bug_to_user_story_v1.\n"
                    "Entrada: bug_report. Saída: User Story em português e Markdown.\n"
                    "Sugestões técnicas são separadas dos requisitos confirmados."),
            commit_description="Publicação do YAML local validado: " + ", ".join(techniques),
        )
        print("Push concluído: lucaskawasaki/bug_to_user_story_v2")
        # Não imprimir respostas arbitrárias, query strings ou credenciais de URLs.
        parsed = urlsplit(url) if isinstance(url, str) else None
        if (parsed and parsed.scheme == "https" and parsed.hostname
                and (parsed.hostname == "smith.langchain.com"
                     or parsed.hostname.endswith(".smith.langchain.com"))
                and not parsed.username and not parsed.password and not parsed.query):
            print(url)
        return True
    except Exception:
        print("Falha no push. Confira credenciais, handle, permissões e conexão.")
        return False


def main() -> int:
    print_section_header("PUBLICAÇÃO DO PROMPT OTIMIZADO")
    # load_yaml pode incluir a linha inválida na exceção; não a enviar ao terminal.
    with redirect_stdout(StringIO()):
        document = load_yaml(str(INPUT_PATH))
    if not isinstance(document, dict) or set(document) != {PROMPT_NAME}:
        print("YAML inválido ou ausente: esperado o mapeamento bug_to_user_story_v2.")
        return 1
    return 0 if push_prompt_to_langsmith(PROMPT_NAME, document[PROMPT_NAME]) else 1


if __name__ == "__main__":
    sys.exit(main())
