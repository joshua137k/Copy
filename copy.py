import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import shutil
import threading
import json

CONFIG_FILE = "config.json"

def ler_configuracao():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"origem": "", "destino": ""}

def salvar_configuracao(origem, destino):
    with open(CONFIG_FILE, "w") as file:
        json.dump({"origem": origem, "destino": destino}, file)

def escolher_diretorio(titulo, entry):
    diretorio = filedialog.askdirectory(title=titulo)
    if diretorio:
        entry.delete(0, tk.END)
        entry.insert(0, diretorio)

def copiar_arquivos_novos_com_progresso(origem, destino, progresso):
    total_arquivos = 0
    total_copiados = 0

    # Primeiro, contamos o total de arquivos a serem copiados
    for pasta_atual, _, arquivos in os.walk(origem):
        pasta_destino_atual = os.path.join(destino, os.path.relpath(pasta_atual, origem))
        arquivos_destino = set(os.listdir(pasta_destino_atual) if os.path.exists(pasta_destino_atual) else [])
        total_arquivos += len([arq for arq in arquivos if arq not in arquivos_destino])

    if total_arquivos == 0:
        progresso.insert(tk.END, "Não há arquivos novos para copiar.\n")
        return

    for pasta_atual, _, arquivos in os.walk(origem):
        pasta_destino_atual = os.path.join(destino, os.path.relpath(pasta_atual, origem))
        if not os.path.exists(pasta_destino_atual):
            os.makedirs(pasta_destino_atual)

        arquivos_destino = set(os.listdir(pasta_destino_atual))

        for arquivo in arquivos:
            if arquivo not in arquivos_destino:
                caminho_completo_origem = os.path.join(pasta_atual, arquivo)
                caminho_completo_destino = os.path.join(pasta_destino_atual, arquivo)

                try:
                    if os.path.isfile(caminho_completo_origem):
                        shutil.copy(caminho_completo_origem, caminho_completo_destino)
                        total_copiados += 1
                        porcentagem = (total_copiados / total_arquivos) * 100
                        progresso.insert(tk.END, f"Copiando: {arquivo} para {pasta_destino_atual} ({porcentagem:.2f}% concluído)\n")
                except Exception as e:
                    progresso.insert(tk.END, f"Erro ao copiar {arquivo}: {e}\n")

    if total_copiados == 0:
        progresso.insert(tk.END, "Não há arquivos novos para copiar.\n")
    else:
        progresso.insert(tk.END, "Cópia concluída. Todos os arquivos foram copiados.\n")


def iniciar_copia(origem_entry, destino_entry, progresso):
    origem = origem_entry.get()
    destino = destino_entry.get()
    salvar_configuracao(origem, destino)
    if not origem or not destino:
        messagebox.showerror("Erro", "Por favor, selecione ambas as pastas.")
        return

    threading.Thread(target=copiar_arquivos_novos_com_progresso, args=(origem, destino, progresso)).start()

# Funções de interface gráfica
def criar_label_frame(parent, titulo, row, column, padx, pady):
    frame = ttk.LabelFrame(parent, text=titulo)
    frame.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
    return frame

def criar_entry_com_botao(frame, label_text, button_text, button_command):
    label = ttk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=(0, 5))
    
    entry = ttk.Entry(frame, width=50)
    entry.pack(side=tk.LEFT, padx=(0, 5))

    button = ttk.Button(frame, text=button_text, command=lambda: button_command(entry))
    button.pack(side=tk.LEFT)
    
    return entry

def criar_interface():
    # Configurações iniciais da janela
    root = tk.Tk()
    root.title("Copiador de Arquivos")
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10))

    # Carregando configurações salvas
    config = ler_configuracao()

    # Frame de Origem e Destino
    origem_frame = criar_label_frame(root, "Origem", 0, 0, 10, 5)
    destino_frame = criar_label_frame(root, "Destino", 1, 0, 10, 5)

    origem_entry = criar_entry_com_botao(origem_frame, "Pasta de Origem:", "Escolher", lambda e: escolher_diretorio("Escolha a pasta de origem", e))
    destino_entry = criar_entry_com_botao(destino_frame, "Pasta de Destino:", "Escolher", lambda e: escolher_diretorio("Escolha a pasta de destino", e))

    origem_entry.insert(0, config["origem"])
    destino_entry.insert(0, config["destino"])

    # Área de progresso
    progresso = scrolledtext.ScrolledText(root, height=10)
    progresso.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")  # Usando sticky="nsew" para expansão vertical e horizontal

    # Botão de início
    iniciar_btn = ttk.Button(root, text="Iniciar Cópia", command=lambda: iniciar_copia(origem_entry, destino_entry, progresso))
    iniciar_btn.grid(row=3, column=0, padx=10, pady=(0, 10))

    # Configurando a expansão das linhas e colunas da grade
    root.grid_rowconfigure(2, weight=1)  # Expande a linha 2 (onde a área de progresso está)
    root.grid_columnconfigure(0, weight=1)  # Expande a coluna 0 (onde todos os widgets estão)

    # Iniciando a janela principal
    root.mainloop()

criar_interface()
