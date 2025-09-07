from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hermes_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/iniciar-chat")
def iniciar_chat(user_id: str = Body(..., embed=True)):
    # Inicia uma nova sessão de chat para o usuário
    hermes_service.chat_sessions[user_id] = hermes_service.iniciar_nova_sessao()
    
    primeira_mensagem = "Olá! Sou Hermes, seu assistente para registro de sinistros. Por favor, descreva o que aconteceu com o seu veículo:"
    
    return {
        "resposta": primeira_mensagem,
        "user_id": user_id,
        "conversa_finalizada": False
    }

@app.post("/processar-mensagem")
# Endpoint para processar mensagens do usuário
def processar_mensagem(payload: dict = Body(...)):
    
    user_id = payload.get("user_id")
    relato_usuario = payload.get("texto", "")

    if not user_id or not relato_usuario:
        raise HTTPException(status_code=400, detail="Campos 'user_id' e 'texto' são obrigatórios.")
    
    try:
        dados_sinistro, resposta_hermes = hermes_service.processar_relato(user_id, relato_usuario)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if dados_sinistro:
        status_java, diagnostico = hermes_service.finalizar_e_enviar_relatorio(dados_sinistro)
        
        del hermes_service.chat_sessions[user_id]
        
        return {
            "resultado": dados_sinistro,
            "status_java": status_java,
            "diagnostico_peca": diagnostico,
            "conversa_finalizada": True,
            "mensagem_final": "Obrigado! Seu relatório foi enviado para análise."
        }
    
    return {
        "resposta": resposta_hermes,
        "user_id": user_id,
        "conversa_finalizada": False
    }

@app.get("/sessoes-ativas")
# Endpoint para listar sessões ativas (para fins de depuração)
def listar_sessoes():
    return {"sessoes_ativas": list(hermes_service.chat_sessions.keys())}

@app.delete("/limpar-sessao/{user_id}")
# Endpoint para limpar uma sessão específica (para fins de depuração)
def limpar_sessao(user_id: str):
    if user_id in hermes_service.chat_sessions:
        del hermes_service.chat_sessions[user_id]
        return {"mensagem": f"Sessão {user_id} removida."}
    return {"mensagem": "Sessão não encontrada."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)