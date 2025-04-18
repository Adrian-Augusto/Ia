import os
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
import threading

# Configuração da API
load_dotenv()
api_key = os.getenv("GENAI_API_KEY")
genai.configure(api_key=api_key)
modelo = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Array de Alimentações da IA
alimentacoes_ia = [
    "Você é um assistente especializado em programação. Responda de forma clara, simples e com exemplos práticos. Sempre que possível, use exemplos de código em Python, JavaScript e outras linguagens populares.",
    "Sempre que o usuário fizer uma pergunta sobre programação, forneça uma resposta objetiva e concisa. Caso a pergunta seja mais complexa, divida a explicação em etapas.",
    "Responda de forma amigável, humana e direta. Dê exemplos práticos sempre que possível, e use uma linguagem simples e acessível para todos os níveis de conhecimento.",
    "Ao responder perguntas sobre erros de código, forneça soluções práticas e sugestões de correção, indicando a parte do código que pode ser melhorada ou corrigida.",
    "Forneça explicações sobre conceitos de programação de maneira clara. Por exemplo, ao explicar o que é uma função em Python, forneça um exemplo simples de código."
]

# Alimentação inicial da IA com as instruções do array
def alimentar_ia():
    for alimentacao in alimentacoes_ia:
        modelo.generate_content(alimentacao)

loop_ativo = False

def gerar_resposta(pergunta):
    try:
        resposta = modelo.generate_content(pergunta)
        return resposta.text.strip()
    except Exception as e:
        return f"[Erro ao gerar resposta: {e}]"

def transcrever_audio():
    global loop_ativo
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=0) as source:
        while loop_ativo:
            status_label.config(text="🎧 Ouvindo...")

            try:
                # Aumentando o tempo de espera e limite de tempo da frase
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                status_label.config(text="⏱️ Nenhum som detectado.")
                continue

            status_label.config(text="🧠 Processando...")

            try:
                texto = recognizer.recognize_google(audio, language="pt-BR")
                entrada_texto.delete(1.0, tk.END)
                entrada_texto.insert(tk.END, texto)
                processar_resposta(texto)
            except sr.UnknownValueError:
                status_label.config(text="🤔 Não entendi.")
            except sr.RequestError:
                status_label.config(text="⚠️ Erro com a API.")

def processar_resposta(texto):
    resposta = gerar_resposta(texto)
    saida_texto.config(state='normal')
    saida_texto.insert(tk.END, f"\n🗣️ Você: {texto}\n🤖 IA: {resposta}\n")
    saida_texto.config(state='disabled')
    status_label.config(text="✅ Pronto.")

def iniciar_transcricao():
    global loop_ativo
    loop_ativo = True
    botao_iniciar.config(state='disabled')
    threading.Thread(target=transcrever_audio, daemon=True).start()

def parar_transcricao():
    global loop_ativo
    loop_ativo = False
    status_label.config(text="⛔ Parado.")
    botao_iniciar.config(state='normal')

def limpar_campos():
    entrada_texto.delete(1.0, tk.END)
    saida_texto.config(state='normal')
    saida_texto.delete(1.0, tk.END)
    saida_texto.config(state='disabled')
    status_label.config(text="🧼 Limpo. Pronto.")

def sair():
    janela.quit()

# Interface
janela = tk.Tk()
janela.title("🧠 Assistente IA para Programação")
janela.geometry("900x800")  # Aumentando o tamanho para melhor visualização
janela.configure(bg="#1e1e2f")

# Títulos e texto
status_label = tk.Label(janela, text="Clique em 'Iniciar' para começar.", bg="#1e1e2f", fg="white", font=("Arial", 14, "bold"))
status_label.pack(pady=15)

entrada_texto = scrolledtext.ScrolledText(janela, height=4, font=("Arial", 14), bg="#2c3e50", fg="white", insertbackground='white')
entrada_texto.pack(pady=15, padx=30, fill=tk.X)

# Adicionando os botões em um frame
botoes_frame = tk.Frame(janela, bg="#1e1e2f")
botoes_frame.pack(pady=15)

botao_iniciar = tk.Button(botoes_frame, text="🎙️ Iniciar", command=iniciar_transcricao, font=("Arial", 12, "bold"), bg="#4a90e2", fg="white", width=14)
botao_iniciar.grid(row=0, column=0, padx=10)

botao_parar = tk.Button(botoes_frame, text="⏹️ Parar", command=parar_transcricao, font=("Arial", 12, "bold"), bg="#f39c12", fg="white", width=14)
botao_parar.grid(row=0, column=1, padx=10)

botao_limpar = tk.Button(botoes_frame, text="🧹 Limpar", command=limpar_campos, font=("Arial", 12, "bold"), bg="#7f8c8d", fg="white", width=14)
botao_limpar.grid(row=0, column=2, padx=10)

botao_sair = tk.Button(botoes_frame, text="❌ Sair", command=sair, font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", width=14)
botao_sair.grid(row=0, column=3, padx=10)

saida_texto = scrolledtext.ScrolledText(janela, height=15, font=("Arial", 13), bg="#2c3e50", fg="white", insertbackground='white')
saida_texto.pack(pady=15, padx=30, fill=tk.BOTH, expand=True)
saida_texto.config(state='disabled')

# Alimenta a IA inicialmente com múltiplos exemplos
threading.Thread(target=alimentar_ia, daemon=True).start()

janela.mainloop()