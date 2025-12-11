import json
import requests
from google.api_core.exceptions import GoogleAPIError
from utils import extrair_json
import diagnostico_service


# ==========================================================
# SERIALIZAÇÃO DO HISTÓRICO DO GEMINI
# ==========================================================

def serializar_history(history_obj):
    """
    Converte o histórico do Gemini (Content objects) em um formato JSON serializável.
    """
    history_serializado = []

    for msg in history_obj:
        texto = ""
        for part in msg.parts:
            texto += part.text or ""

        history_serializado.append({
            "role": msg.role,
            "text": texto
        })

    return history_serializado


def desserializar_history(history_json):
    """
    Converte o histórico salvo (JSON) no formato aceito pelo Gemini:
    [
        {"role": "user", "parts": ["texto"]},
        {"role": "model", "parts": ["resposta"]},
    ]
    """
    history = []
    for item in history_json:
        history.append({
            "role": item["role"],
            "parts": [item["text"]]
        })
    return history


# ==========================================================
# SERVIÇO PRINCIPAL – REDIS + GEMINI
# ==========================================================

class HermesService:

    def __init__(self, modelo_selector, redis_client, strategy_selector):
        """
        modelo_selector(tipo) -> retorna modelo Gemini apropriado
        strategy_selector(tipo) -> retorna Strategy apropriada
        redis_client -> instância do Redis
        """
        self.modelo_selector = modelo_selector
        self.strategy_selector = strategy_selector
        self.redis = redis_client


    def _key(self, user_id):
        return f"chat_session:{user_id}"


    def _salvar_sessao(self, user_id, gemini_chat, tipo_sinistro, system_instruction):
        history_serializado = serializar_history(gemini_chat.history)

        data = {
            "tipo_sinistro": tipo_sinistro,
            "history": history_serializado,
            "system_instruction": system_instruction
        }

        self.redis.set(self._key(user_id), json.dumps(data))


    def _carregar_sessao(self, user_id):
        raw = self.redis.get(self._key(user_id))
        return None if not raw else json.loads(raw)


    def _deletar_sessao(self, user_id):
        self.redis.delete(self._key(user_id))


    # ==========================================================
    # INICIAR CHAT
    # ==========================================================
    def iniciar_chat(self, user_id, tipo_sinistro):
        user_id = str(user_id)

        # Selecionar Strategy e Modelo
        strategy = self.strategy_selector(tipo_sinistro)
        model = self.modelo_selector(tipo_sinistro)

        # System Instruction vem da Strategy
        system_instruction = strategy.system_instruction()

        # Cria chat (sem system_instruction no start_chat)
        chat = model.start_chat(history=[])

        # Salvar sessão
        self._salvar_sessao(
            user_id,
            chat,
            tipo_sinistro,
            system_instruction
        )

        # Retorna a mensagem inicial configurada na Strategy
        return strategy.prompt_inicial()


    # ==========================================================
    # PROCESSAR MENSAGEM DO USUÁRIO
    # ==========================================================
    def processar_relato(self, user_id, relato_usuario):
        user_id = str(user_id)

        # Carrega sessão
        sessao = self._carregar_sessao(user_id)
        if not sessao:
            raise ValueError("Sessão não encontrada.")

        tipo_sinistro = sessao["tipo_sinistro"]
        system_instruction = sessao["system_instruction"]
        history_json = sessao["history"]

        # Desserializa histórico
        history = desserializar_history(history_json)

        # Reconstrói o modelo
        model = self.modelo_selector(tipo_sinistro)

        # Reconstrói chat
        chat = model.start_chat(history=history)

        # Envia mensagem
        try:
            resposta = chat.send_message(relato_usuario)
        except GoogleAPIError as e:
            raise RuntimeError(f"Erro ao comunicar com Gemini AI: {e}")

        # Atualiza sessão no Redis
        self._salvar_sessao(
            user_id=user_id,
            gemini_chat=chat,
            tipo_sinistro=tipo_sinistro,
            system_instruction=system_instruction
        )

        # Tenta extrair JSON (pode estar incompleto)
        dados_sinistro = extrair_json(resposta.text)

        return dados_sinistro, resposta.text.strip()


    # ==========================================================
    # FINALIZAR RELATÓRIO E ENVIAR PARA JAVA
    # ==========================================================
    def finalizar_e_enviar_relatorio(self, user_id, dados_sinistro):
        user_id = str(user_id)

        # Envia para o servidor Java
        try:
            java_response = requests.post(
                "http://localhost:8080/sinistros/receber",
                json=dados_sinistro,
                timeout=10
            )
            status_java = java_response.status_code
        except Exception as e:
            print("Erro ao enviar para Java:", e)
            status_java = "erro"

        # Diagnóstico de peças (somente se aplicável)
        diagnostico = diagnostico_service.analisar_e_diagnosticar(dados_sinistro)

        # Apaga a sessão no Redis
        self._deletar_sessao(user_id)

        return status_java, diagnostico
