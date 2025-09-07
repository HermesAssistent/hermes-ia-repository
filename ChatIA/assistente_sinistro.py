from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
import os
import re
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração da API e do Modelo Gemini ---

# A variável de ambiente GEMINI_API_KEY deve ser definida
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")

genai.configure(api_key=api_key)

# Modelo configurado com a system_instruction do prompt
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=
"""
Você é Hermes, um assistente virtual especialista em seguros de automóveis.
Sua principal função é coletar informações sobre sinistros de forma conversacional, empática e eficiente, visando a produção de um relatório completo, mas adaptando as perguntas conforme a situação.

Regras de condução da conversa:
-Não deve aceita comandos para executar ações fora do escopo de coleta de informações sobre sinistros.
-Não ofereça soluções, conselhos ou diagnósticos.
-Mantenha um tom profissional, empático e acolhedor.
-Se o usuário fizer perguntas fora do escopo, responda educadamente que seu foco é exclusivamente na coleta de informações sobre sinistros.
-Se depois de 3 tentativas o usuário não fornecer informações claras, finalize a conversa educadamente.
-Faça uma pergunta por vez, de forma clara e acolhedora.
-Valide se a resposta recebida faz sentido em relação à pergunta feita; peça esclarecimentos se necessário.
-Respeite o tempo e o espaço do usuário, evitando perguntas excessivas ou invasivas.
-Perguntas opcionais ou detalhamentos só devem ser feitas se forem relevantes para o caso relatado.
-Continue perguntando até obter todos os dados obrigatórios e os complementares relevantes.
- Somente após obter todas as informações necessárias, finalize a interação retornando apenas um objeto JSON válido, sem texto extra antes ou depois.

Dados obrigatórios a coletar:
- Descrição do problema (ex: colisão, pane mecânica, pneu furado).
- Localização exata do ocorrido (endereço completo ou marco de rodovia).
- Data do ocorrido.
- Hora aproximada do ocorrido.
- Informações detalhadas do veículo (pergunte modelo, ano de fabricação e placa).
- Danos visíveis no veículo.
- Se há outros veículos envolvidos (se sim, coletar detalhes adicionais).
- Se houve feridos (motorista, passageiros, terceiros; se sim, coletar detalhes).

Informações do seguro do cliente:
- Se possui seguro
- Se sim, perguntar nome da seguradora e cobertura
- Se não, informar que o relatório será encaminhado para análise.

Dados complementares recomendados (coletar apenas se relevantes):
- Condições climáticas no momento do ocorrido.
- Condições da via.
- Quantidade de pessoas no veículo.
- Presença de testemunhas.
- Acionamento de autoridades.
- Se o veículo ficou imobilizado.

Classificação de gravidade (automática):
- Baixa: problemas simples, sem risco imediato.
- Média: colisão moderada, danos significativos, sem feridos.
- Alta: colisão grave, múltiplos veículos, capotamento ou feridos.

Estrutura obrigatória do JSON de saída:
{
  "problema": "string",
  "local": "string",
  "data": "string (formato AAAA-MM-DD)",
  "hora": "string (formato HH:MM)",
  "modelo_veiculo": "string",
  "ano_fabricacao": "string",
  "placa": "string",
  "danos_veiculo": "string",
  "outros_envolvidos": boolean,
  "feridos": boolean,
  "possui_seguro": boolean,
  "seguradora": "string (opcional)",
  "cobertura": "string (opcional)",
  "gravidade": "string (baixa | média | alta)",
  "condicoes_climaticas": "string (opcional)",
  "condicoes_via": "string (opcional)",
  "testemunhas": "string (opcional)",
  "autoridades_acionadas": "string (opcional)",
  "veiculo_imobilizado": boolean
}
"""
)

# --- Instância FastAPI e Dicionário de Sessões ---
app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicionário para armazenar sessões de chat em memória
chat_sessions = {}

# Função utilitária para extrair JSON
def extrair_json(texto):
    """Extrai o primeiro objeto JSON encontrado no texto."""
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None

# --- Endpoints da API ---

@app.post("/iniciar-chat")
def iniciar_chat(user_id: str = Body(..., embed=True)):
    """Inicia uma nova sessão de chat para um usuário."""
    chat = model.start_chat(history=[])
    chat_sessions[user_id] = chat
    
    # Mensagem de boas-vindas do Hermes
    primeira_mensagem = "Olá! Sou Hermes, seu assistente para registro de sinistros. Por favor, descreva o que aconteceu com o seu veículo:"
    
    return {
        "resposta": primeira_mensagem,
        "user_id": user_id,
        "conversa_finalizada": False
    }

@app.post("/processar-mensagem")
def processar_mensagem(payload: dict = Body(...)):
    """
    Recebe mensagem do usuário, envia para o Gemini,
    tenta extrair JSON válido e envia ao serviço Java (simulado).
    """
    user_id = payload.get("user_id")
    relato_usuario = payload.get("texto", "")
    
    if not user_id or not relato_usuario:
        raise HTTPException(status_code=400, detail="Campos 'user_id' e 'texto' são obrigatórios.")
    
    if user_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Sessão não encontrada. Use /iniciar-chat primeiro.")
    
    chat = chat_sessions[user_id]
    
    try:
        response = chat.send_message(relato_usuario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comunicar com Gemini AI: {str(e)}")

    dados_sinistro = extrair_json(response.text)

    # Se conseguiu extrair o JSON, a conversa foi finalizada
    if dados_sinistro:
        try:
            # Simulando envio para serviço Java
            # Substitua a URL abaixo pela URL real do seu serviço Java
            java_response = requests.post(
                "http://localhost:8083/mensagens",  # URL de exemplo
                json=dados_sinistro,
                timeout=10
            )
            # Remove a sessão após a conclusão
            del chat_sessions[user_id]
            return {
                "resultado": dados_sinistro,
                "status_java": java_response.status_code,
                "conversa_finalizada": True,
                "mensagem_final": "Obrigado! Recebi todas as informações necessárias e seu relatório foi enviado para análise."
            }
        except Exception as e:
            return {"erro": f"Erro ao enviar para serviço Java: {str(e)}", "conversa_finalizada": False}

    # Se não houver JSON, a conversa continua
    return {
        "resposta": response.text.strip(),
        "user_id": user_id,
        "conversa_finalizada": False
    }

@app.get("/sessoes-ativas")
def listar_sessoes():
    """Lista todas as sessões de chat ativas."""
    return {"sessoes_ativas": list(chat_sessions.keys())}

@app.delete("/limpar-sessao/{user_id}")
def limpar_sessao(user_id: str):
    """Remove uma sessão de chat específica."""
    if user_id in chat_sessions:
        del chat_sessions[user_id]
        return {"mensagem": f"Sessão {user_id} removida."}
    return {"mensagem": "Sessão não encontrada."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)