# 🤖 Hermes – Assistente Veicular

Hermes é um sistema modular composto por três serviços principais:

- 📡 **ApiRest**: API feita em **Java/Spring** para gerenciar os dados.  
- 💻 **GUI**: Interface gráfica desenvolvida em **React**.  
- 🧠 **ChatIA**: Chat conversacional com **Gemini (Google Generative AI)** feito em **Python/FastAPI**.  

---

## ✅ Requisitos

- 🐍 **Python 3.10+**  
- 📦 Bibliotecas Python necessárias:
  - `fastapi`
  - `requests`
  - `google-generativeai`

---

## 🚀 Como executar

### ▶️ Rodando o servidor Python (ChatIA)
Entre na pasta ChatIA, instale as dependências citadas acima e rode:
```bash
uvicorn assistente_sinistro:app --reload --host 0.0.0.0 --port 8000
```

🧪 Testando requisições

Você pode testar as requisições da API utilizando ferramentas como:  

- [Bruno](https://www.usebruno.com/downloads) 🧑‍💻  
- [Postman](https://www.postman.com/) 📬  
- [Insomnia](https://insomnia.rest/) 🌙  
- Ou até mesmo via **curl** no terminal 🖥️  

📷 Exemplos de requisição no Bruno:  

![Exemplo 1](assets/image.png)  
![Exemplo 2](assets/image-1.png)  

---

### 🔹 Exemplo de requisição via curl
```bash
curl -X POST "http://localhost:8000/processar" \
     -H "Content-Type: application/json" \
     -d '{"texto": "Meu carro colidiu na Av. Paulista ontem"}'
```

## 📌 Observações importantes

- 🔄 **Independência dos serviços:** O backend em **Spring Boot** e o serviço em **FastAPI** funcionam de forma independente.  
- 🌐 **Comunicação:** A comunicação entre os serviços é feita via **HTTP/REST** utilizando **JSON**.  
- 💾 **Banco de dados:** O **PostgreSQL** é utilizado como banco de dados pela API Java/Spring.  
- 🎨 **Front-end:** O **React** é responsável pela interface que interage com os dois serviços.  
- ✨ **Variável de ambiente:** Certifique-se de configurar a variável de ambiente `GEMINI_API_KEY` antes de rodar o serviço Python.