import json
import redis
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ChatIA.strategies.prompt_strategy import (
    AutomotivoPromptStrategy,
    ResidencialPromptStrategy,
    TransportePromptStrategy
)
from ChatIA.config import (
    MODEL_AUTOMOTIVO,
    MODEL_RESIDENCIAL,
    MODEL_TRANSPORTE
)
from prompt_factory import PromptFactory
from hermes_service import HermesService

# ---------------------------
# REDIS CLIENT
# ---------------------------
redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# ---------------------------
# FACTORY DE PROMPTS
# ---------------------------
prompt_factory = PromptFactory([
    AutomotivoPromptStrategy(),
    ResidencialPromptStrategy(),
    TransportePromptStrategy()
])


# ---------------------------
# FUNÇÃO DE SELEÇÃO DE MODELO
# ---------------------------
def selecionar_modelo(tipo_sinistro):
    if tipo_sinistro == "AUTOMOTIVO":
        return MODEL_AUTOMOTIVO
    elif tipo_sinistro == "RESIDENCIAL":
        return MODEL_RESIDENCIAL
    elif tipo_sinistro == "CARGA":
        return MODEL_TRANSPORTE
    else:
        raise ValueError(f"Tipo de sinistro inválido: {tipo_sinistro}")


# ---------------------------
# INSTANCIA O SERVIÇO PRINCIPAL
# ---------------------------
hermes = HermesService(
    selecionar_modelo,
    redis_client,
    prompt_factory.obter_strategy
)

# ---------------------------
# FASTAPI CONFIG
# ---------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# INICIAR CHAT
# ==========================================================
@app.post("/iniciar-chat")
def iniciar_chat(
        user_id: str = Body(..., embed=True),
        tipo_sinistro: str = Body(...)
):
    strategy = prompt_factory.obter_strategy(tipo_sinistro)
    resposta_inicial = hermes.iniciar_chat(user_id, tipo_sinistro)

    return {
        "resposta": resposta_inicial,
        "user_id": user_id,
        "tipo_sinistro": tipo_sinistro,
        "conversa_finalizada": False
    }


# ==========================================================
# PROCESSAR MENSAGEM
# ==========================================================
@app.post("/processar-mensagem")
def processar_mensagem(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    relato_usuario = payload.get("texto", "")

    if not user_id or not relato_usuario:
        raise HTTPException(status_code=400, detail="Campos 'user_id' e 'texto' são obrigatórios.")

    try:
        dados_sinistro, resposta_hermes = hermes.processar_relato(user_id, relato_usuario)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Se o JSON do sinistro foi completado
    if dados_sinistro:
        status_java, diagnostico = hermes.finalizar_e_enviar_relatorio(user_id, dados_sinistro)

        return {
            "resultado": dados_sinistro,
            "status_java": status_java,
            "diagnostico_peca": diagnostico,
            "conversa_finalizada": True,
            "mensagem_final": "Obrigado! Seu relatório foi enviado para análise."
        }

    # Conversa continua
    return {
        "resposta": resposta_hermes,
        "user_id": user_id,
        "conversa_finalizada": False
    }


# ==========================================================
# DEBUG: SESSÕES ATIVAS NO REDIS
# ==========================================================
@app.get("/sessoes-ativas")
def listar_sessoes():
    keys = redis_client.keys("chat_session:*")
    return {"sessoes": keys}


# ==========================================================
# DEBUG: LIMPAR SESSÃO
# ==========================================================
@app.delete("/limpar-sessao/{user_id}")
def limpar_sessao(user_id: str):
    redis_client.delete(f"chat_session:{user_id}")
    return {"mensagem": f"Sessão removida: {user_id}"}


# ==========================================================
# UVICORN
# ==========================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
