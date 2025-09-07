import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Carregar a chave da API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")

genai.configure(api_key=api_key)

# Criar um modelo Gemini com instrução específica e focada
model_pecas = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="""
    Você é um assistente virtual especialista em diagnóstico de peças automotivas.
    Sua única função é analisar um problema de veículo e, com base no modelo do carro, identificar a peça exata que precisa de reparo ou substituição.
    Seja conciso, direto e forneça apenas o nome e, se possível, a especificação da peça.
    Não gere relatórios, orçamentos, ou orientações. Foque 100% na identificação da peça.
    """
)

def identificar_peca_necessaria(caminho_arquivo_json):
    """
    Lê o JSON do sinistro, analisa o problema, e decide o encaminhamento.
    """
    if not os.path.exists(caminho_arquivo_json):
        print(f"Erro: O arquivo '{caminho_arquivo_json}' não foi encontrado.")
        return

    with open(caminho_arquivo_json, 'r', encoding='utf-8') as f:
        dados_sinistro = json.load(f)

    problema = dados_sinistro.get("problema", "").lower()
    modelo_veiculo = dados_sinistro.get("modelo_veiculo", "")
    danos = dados_sinistro.get("danos_veiculo", "")
    seguradora_info = dados_sinistro.get("seguradora")
    tem_seguro = isinstance(seguradora_info, str) and seguradora_info.lower() == "sim"
    
    # Verifica se o problema é do tipo que a IA pode analisar (pane/falha)
    is_problema_tecnico = "pane" in problema or "eletric" in problema or "mecani" in problema or "bateria" in problema
    
    if is_problema_tecnico:
        print("\n--- Análise de Causa Técnica ---")
        prompt_para_ia = f"""
        **Análise de Peça**
        ---
        **Veículo:** {modelo_veiculo}
        **Problema relatado:** {danos}
        
        Qual é a peça mais provável que causa este problema?
        """
        try:
            response = model_pecas.generate_content(prompt_para_ia)
            print("\n--- Diagnóstico da Peça ---")
            print(response.text)
        except Exception as e:
            print(f"Ocorreu um erro ao consultar a IA: {e}")
            
    else:
        print("\n--- Análise de Sinistro (Não-técnico) ---")
        print("O problema relatado (ex: colisão) não requer um diagnóstico de peça por IA.")

    # Lógica de encaminhamento baseada na existência de seguro
    print("\n--- Recomendação de Encaminhamento ---")
    if tem_seguro:
        print("Recomendamos que você acione sua seguradora para obter assistência e registrar o sinistro.")
    else:
        print("Como não identificamos um seguro ativo, recomendamos levar o veículo a uma oficina de sua confiança para uma avaliação detalhada.")

# Execução do script
if __name__ == "__main__":
    nome_do_arquivo = 'relatorio_sinistro.json'
    identificar_peca_necessaria(nome_do_arquivo)