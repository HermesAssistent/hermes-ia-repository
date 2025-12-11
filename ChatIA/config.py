import google.generativeai as genai
from dotenv import load_dotenv
# Importa prompts detalhados
from ChatIA.strategies.prompt_strategy import (
    AutomotivoPromptStrategy,
    ResidencialPromptStrategy,
    TransportePromptStrategy
)


load_dotenv()

# Configuração da API do Gemini
API_KEY = 'CHAVE_AQUI'
if not API_KEY:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")

genai.configure(api_key=API_KEY)

automotivo_strategy = AutomotivoPromptStrategy()
residencial_strategy = ResidencialPromptStrategy()
transporte_strategy = TransportePromptStrategy()

MODEL_AUTOMOTIVO = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=automotivo_strategy.system_instruction()
)

MODEL_RESIDENCIAL = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=residencial_strategy.system_instruction()
)

MODEL_TRANSPORTE = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=transporte_strategy.system_instruction()
)

# Configuração de serviços externos
JAVA_SERVICE_URL = "http://localhost:8090/v1/chat/receber-relato"