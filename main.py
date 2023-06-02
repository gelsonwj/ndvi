import tkinter as tk
from tkinter import ttk
import ast
from datetime import datetime
from function_ndvi import *
from controle import *


# Função para obter a largura e altura da tela do dispositivo
def get_screen_size():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

def processar():
    farm = entry_farm.get()
    start_date = entry_start_date.get()
    end_date = entry_end_date.get()

    # Converter as datas para o formato aaaa-mm-dd
    try:
        start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        warning_message.set("Formato de data inválido!")
        return

    poligonos = conecta_bd()
    poligonos = poligonos.loc[(poligonos['fazenda'] == farm)]
    
    for index, row in poligonos.iterrows():
        roi_coords_str = row['roi_coords']
        roi_coords = ast.literal_eval(roi_coords_str)
        fazenda = row['fazenda']
        talhao = row['talhao']
        proprietario = row['proprietario']
        processor = SentinelImageProcessor(roi_coords, start_date, end_date, fazenda, talhao, proprietario)
        
        try:
            image_roi = processor.process_images()
        except IndexError:
            # Lidar com erro se o intervalo de datas for pequeno
            warning_message.set("Erro: Ajuste o intervalo de datas para obter a imagem.")
            return

        processor.export_image(image_roi, exported_label, root)
        exported_label_text = "\n".join(message_history)  # Concatena todas as mensagens do histórico
        exported_label.config(text=exported_label_text, fg="green")

    warning_message.set("")  # Limpar a mensagem de aviso

root = tk.Tk()
root.title("Obter imagens NDVI")

# Obter a largura e altura da tela do dispositivo
screen_width, screen_height = get_screen_size()

# Definir a nova largura e altura da janela principal com base na porcentagem desejada
new_width = int(screen_width * 0.4)
new_height = int(screen_height * 0.28)

# Centralizar a janela principal na tela do dispositivo
x_position = (screen_width - new_width) // 2
y_position = (screen_height - new_height) // 2

# Definir a geometria da janela principal
root.geometry(f"{new_width}x{new_height}+{x_position}+{y_position}")

# Adicionar bordas arredondadas usando ttk
style = ttk.Style()
style.configure("TEntry", padding=5, relief="flat")

label_farm = tk.Label(root, text="Digite o nome da fazenda para obter o NDVI:")
label_farm.pack()

entry_farm = ttk.Entry(root)
entry_farm.pack()

label_dates = tk.Label(root, text="Digite o intervalo de datas (mínimo de 10 dias):")
label_dates.pack()

entry_start_date = ttk.Entry(root)
entry_start_date.pack()

entry_end_date = ttk.Entry(root)
entry_end_date.pack()

button = tk.Button(root, text="Processar", command=processar)
button.pack(pady=10)

exported_label = tk.Label(root, text="", fg="green")
exported_label.pack()

warning_message = tk.StringVar()
warning_label = tk.Label(root, textvariable=warning_message, fg="red")
warning_label.pack()

root.mainloop()
