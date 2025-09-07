import requests
from google.api_core.exceptions import GoogleAPIError
from config import MODEL, JAVA_SERVICE_URL
from utils import extrair_json
import diagnostico_service

# Dicionário para armazenar sessões de chat em memória
chat_sessions = {}

def iniciar_nova_sessao():
    # Inicia uma nova sessão de chat com o modelo Gemini
    return MODEL.start_chat(history=[])

def processar_relato(user_id, relato_usuario):
    # Processa o relato do usuário e retorna os dados do sinistro se completos
    if user_id not in chat_sessions:
        raise ValueError("Sessão não encontrada.")
    
    chat = chat_sessions[user_id]
    
    try:
        response = chat.send_message(relato_usuario)
        dados_sinistro = extrair_json(response.text)
        return dados_sinistro, response.text.strip()
    except GoogleAPIError as e:
        raise RuntimeError(f"Erro ao comunicar com Gemini AI: {e}")

def enviar_para_servico_externo(dados_sinistro):
    # Envia os dados do sinistro para o serviço Java externo
    try:
        java_response = requests.post(
            JAVA_SERVICE_URL,
            json=dados_sinistro,
            timeout=10
        )
        return java_response.status_code
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar para serviço Java: {e}")
    
def finalizar_e_enviar_relatorio(dados_sinistro):
    # Finaliza a sessão de chat e envia o relatório para o serviço externo e diagnóstico de peça
    
    try:
        java_response = requests.post(
            JAVA_SERVICE_URL,
            json=dados_sinistro,
            timeout=10
        )
        status_java = java_response.status_code
    except Exception as e:
        status_java = "Erro de conexão com o serviço Java"
        print(f"Erro ao enviar para o serviço Java: {e}")
        
    # Obter diagnóstico de peça se aplicável
    diagnostico = diagnostico_service.analisar_e_diagnosticar(dados_sinistro)
    
    return status_java, diagnostico