import os
import google.generativeai as genai
from config import API_KEY

# =============== CONFIGURAÇÃO MODELOS ===============

# Modelo especializado em peças automotivas
model_pecas = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="""
    Você é um especialista em peças automotivas.
    Sua única função é identificar qual peça está com defeito ou foi danificada,
    com base no modelo do veículo e no problema relatado.
    Responda somente com o nome da peça (e especificação se necessário).
    Não gere explicações, relatórios, justificativas ou instruções de reparo.
    """
)

# Modelo especializado em diagnósticos residenciais
model_residencial = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="""
    Você é um especialista em sinistros residenciais.
    Sua única função é identificar qual elemento da casa está com problema,
    baseado na descrição relatada (ex: cano, fiação, telhado, parede, laje, tomada, disjuntor).
    Responda apenas com o elemento ou componente afetado.
    Não gere explicações, nem instruções de reparo.
    """
)

# Modelo especializado para cargas
model_carga = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction="""
    Você é um especialista em avarias de cargas e transporte.
    Sua única função é identificar qual parte da carga, embalagem ou estrutura foi afetada,
    com base na descrição do sinistro (ex: palete, lacre, contêiner, caixa, mercadoria, refrigeração).
    Responda somente com o componente ou item afetado.
    Não gere explicações ou instruções operacionais.
    """
)


# =============== FUNÇÃO PRINCIPAL ===============

def analisar_e_diagnosticar(dados_sinistro):

    tipo = dados_sinistro.get("tipo", "").lower()

    # -----------------------------
    #   SINISTRO AUTOMOTIVO
    # -----------------------------
    if tipo == "automotivo":
        categoria = dados_sinistro.get("categoria_problema", "").lower()
        modelo_veiculo = dados_sinistro.get("modelo_veiculo", "")
        danos = dados_sinistro.get("danos_veiculo", "")

        # Diagnóstico de peça para pane mecânica
        if categoria == "pane mecânica":
            prompt = f"""
            Veículo: {modelo_veiculo}
            Problema relatado: {danos}

            Qual peça está com defeito?
            """
            try:
                result = model_pecas.generate_content(prompt)
                return result.text.strip()
            except Exception as e:
                return f"Erro ao obter diagnóstico automotivo (peças): {e}"

        # Diagnóstico para colisão (parte afetada)
        if categoria == "colisão":
            prompt = f"""
            Veículo: {modelo_veiculo}
            Danos relatados: {danos}

            Qual a parte mais afetada pela colisão?  
            Apenas o nome da parte (ex: para-choque, paralama, porta, farol).
            """
            try:
                result = model_pecas.generate_content(prompt)
                return result.text.strip()
            except Exception as e:
                return f"Erro ao obter diagnóstico automotivo (colisão): {e}"

        return "Não há diagnóstico específico para este tipo de ocorrência automotiva."


    # -----------------------------
    #   SINISTRO RESIDENCIAL
    # -----------------------------
    if tipo == "residencial":
        problema = dados_sinistro.get("problema", "")
        comodo = dados_sinistro.get("comodo_afetado", "")
        danos = dados_sinistro.get("danos_visiveis", "")

        prompt = f"""
        Tipo de problema: {problema}
        Cômodo afetado: {comodo}
        Danos visíveis: {danos}

        Qual elemento do imóvel está com problema?  
        Apenas responda com o elemento (ex: cano PVC, telhado, disjuntor, parede de alvenaria, fiação, tomada).
        """

        try:
            result = model_residencial.generate_content(prompt)
            return result.text.strip()
        except Exception as e:
            return f"Erro ao obter diagnóstico residencial: {e}"


    # -----------------------------
    #   SINISTRO DE CARGA
    # -----------------------------
    if tipo == "transporte":
        problema = dados_sinistro.get("problema", "")
        tipo_carga = dados_sinistro.get("tipo_carga", "")
        danos = dados_sinistro.get("danos_carga", "")
        temperatura = dados_sinistro.get("temperatura", "")

        prompt = f"""
        Tipo do problema: {problema}
        Tipo da carga: {tipo_carga}
        Danos relatados: {danos}
        Temperatura (se houver): {temperatura}

        Qual elemento da carga, embalagem ou estrutura foi mais afetado?  
        Responda somente com um item (ex: palete, lacre, embalagem, refrigeração, contêiner, caixa).
        """

        try:
            result = model_carga.generate_content(prompt)
            return result.text.strip()
        except Exception as e:
            return f"Erro ao obter diagnóstico da carga: {e}"


    # -----------------------------
    #   TIPO NÃO RECONHECIDO
    # -----------------------------
    return "Tipo de sinistro não reconhecido ou sem diagnóstico aplicável."
