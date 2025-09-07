# Hermes IA - Assistente de Sinistro

## Descrição

Este repositório contém o código-fonte do Hermes IA, um chatbot assistente projetado para auxiliar no processo de relatórios de sinistros. O chatbot é construído com Python e a API do Google Gemini para fornecer uma interface de conversação inteligente.

## Funcionalidades

-   **Chatbot com IA:** Utiliza o Google Gemini para entender e responder às perguntas dos usuários de forma natural.
-   **Análise de Relatórios:** Capaz de processar e analisar informações de relatórios de sinistros em formato JSON.
-   **Interface de Linha de Comando:** Interação com o assistente diretamente do terminal.

## Tecnologias Utilizadas

-   **Linguagem:** Python 3
-   **IA e NLP:** Google Gemini API
-   **Bibliotecas Python:**
    -   `google-generativeai`

## Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/HermesAsistent/hermes-ia-repository.git
    cd hermes-ia-repository
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install google-generativeai python-dotenv
    ```

4.  **Configure sua chave de API:**
    Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da API do Google Gemini:
    ```
    GOOGLE_API_KEY="SUA_CHAVE_API_AQUI"
    ```
    O arquivo `assistente_sinistro.py` já está configurado para carregar essa variável de ambiente.

5.  **Execute o assistente:**
    ```bash
    python ChatIA/assistente_sinistro.py
    ```


