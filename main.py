import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from functools import lru_cache

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Por favor, defina GEMINI_API_KEY no arquivo .env")

genai.configure(api_key=GEMINI_API_KEY)

# Configurações otimizadas do modelo
generation_config = {
    "temperature": 0.3,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,  # Reduzido para economizar tokens
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Criação do modelo
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",  # Modelo mais leve e rápido
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Prompt de sistema otimizado
system_prompt = """Você é o HelpIA, assistente de emergências urbanas. Forneça respostas curtas e diretas:

1. Em emergências graves (incêndio, acidente, crime):
- "Ligue imediatamente para [número relevante]"
- "Faça X, Y, Z (passos curtos)"

2. Para outras emergências:
- Orientações passo a passo
- Telefones úteis
- Como descrever localização

3. Se não for emergência:
- "Só posso ajudar com emergências"

Mantenha respostas abaixo de 3 linhas."""

# Cache de respostas comuns
emergency_responses = {
    "casa pegando fogo": "Ligue imediatamente para os bombeiros (193)! Saia da casa e vá para um local seguro. Não tente apagar o fogo sozinho.",
    "acidente de carro": "Ligue para o SAMU (192) e polícia (190). Se possível, sinalize o local e não mova os feridos.",
    # Adicione mais respostas padrão conforme necessário
}

last_request_time = 0

def generate_response(user_input):
    global last_request_time
    
    # Verifica primeiro no cache de emergências
    lower_input = user_input.lower().strip()
    if lower_input in emergency_responses:
        return emergency_responses[lower_input]
    
    try:
        # Controle mais rigoroso de requisições
        elapsed = time.time() - last_request_time
        if elapsed < 2:  # Aumentado para 2 segundos
            time.sleep(2 - elapsed)
        
        last_request_time = time.time()
        
        # Gera resposta principal
        full_prompt = f"{system_prompt}\nUsuário: {user_input}\nHelpIA:"
        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"Erro na API: {str(e)}")  # Log para debug
        # Respostas de fallback
        if "fogo" in lower_input:
            return emergency_responses["casa pegando fogo"]
        return "Sistema ocupado. Por segurança: ligue para 193 (bombeiros) ou 192 (SAMU)."

def main():
    print("\nHelpIA - Chatbot de Suporte em Emergências Urbanas")
    print("Digite 'sair' para encerrar. Para emergências graves, ligue diretamente:\n")
    print("193 - Bombeiros | 192 - SAMU | 190 - Polícia\n")
    
    while True:
        try:
            user_input = input("Você: ").strip()
            
            if user_input.lower() == 'sair':
                print("HelpIA: Fique seguro! Lembre-se dos números de emergência.")
                break
                
            if not user_input:
                continue
                
            response = generate_response(user_input)
            print(f"HelpIA: {response}")
            
        except KeyboardInterrupt:
            print("\nHelpIA: Encerrando. Em caso de emergência, ligue para os números apropriados!")
            break


if __name__ == "__main__":
    main()
