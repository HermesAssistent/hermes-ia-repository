import json
import re

# Extrai o primeiro objeto JSON encontrado em uma string de texto
def extrair_json(texto):
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None