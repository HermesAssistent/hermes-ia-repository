import os
import google.generativeai as genai
from config import API_KEY

# Configuração do modelo especializado em peças
model_pecas = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="""
    Você é um assistente virtual especialista em diagnóstico de peças automotivas.
    Sua única função é analisar um problema de veículo e, com base no modelo do carro, identificar a peça exata que precisa de reparo ou substituição.
    Seja conciso, direto e forneça apenas o nome e, se possível, a especificação da peça.
    Não gere relatórios, orçamentos, ou orientações. Foque 100% na identificação da peça.
    """,
    safety_settings={
        "HARASSMENT": "BLOCK_NONE",
        "HATE": "BLOCK_NONE",
        "SEXUAL": "BLOCK_NONE",
        "DANGEROUS": "BLOCK_NONE",
    }
)

def analisar_e_diagnosticar(dados_sinistro):
    # Extração dos dados relevantes do sinistro
    categoria_problema = dados_sinistro.get("categoria_problema", "").lower()
    modelo_veiculo = dados_sinistro.get("modelo_veiculo", "")
    danos = dados_sinistro.get("danos_veiculo", "")
    
    
    if categoria_problema == "pane mecânica":
        prompt_para_ia = f"""
        **Análise de Peça**
        ---
        **Veículo:** {modelo_veiculo}
        **Problema relatado:** {danos}
        
        Qual é a peça mais provável que causa este problema?
        """
        try:
            response = model_pecas.generate_content(prompt_para_ia)
            return response.text.strip()
        except Exception as e:
            return f"Erro ao obter diagnóstico de peça: {e}"
    
    return "O problema relatado (ex: colisão ou outro) não requer um diagnóstico de peça por IA."