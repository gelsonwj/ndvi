import tkinter as tk
from tkinter import ttk
import ast
from datetime import datetime
from function_ndvi import *
from controle import *


def get_screen_size():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height


def processar():
    farm = combobox_farm.get()
    start_date = entry_start_date.get()
    end_date = entry_end_date.get()

    try:
        start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        warning_message.set("Formato de data inválido!")
        return

    if start_date > end_date:
        warning_message.set("A data final não pode ser menor que a data inicial")
        return

    poligonos = conecta_bd()

    if farm == "Todas":
        farms = ["Esperança", "Harmonia", "Primavera"]
    else:
        farms = [farm]

    for farm in farms:
        farm_poligonos = poligonos.loc[poligonos['fazenda'] == farm]

        for _, row in farm_poligonos.iterrows():
            roi_coords = ast.literal_eval(row['roi_coords'])
            fazenda = row['fazenda']
            talhao = row['talhao']
            proprietario = row['proprietario']
            processor = SentinelImageProcessor(roi_coords, start_date, end_date, fazenda, talhao, proprietario)

            try:
                image_roi = processor.process_images()
            except IndexError:
                warning_message.set("Erro: Ajuste o intervalo de datas para obter a imagem.")
                return

            processor.export_image(image_roi, exported_label, root)
            exported_label_text = "\n".join(message_history)
            exported_label.config(text=exported_label_text, fg="green")

    warning_message.set("")


root = tk.Tk()
root.title("Obter imagens NDVI")

screen_width, screen_height = get_screen_size()

new_width = int(screen_width * 0.4)
new_height = int(screen_height * 0.28)

x_position = (screen_width - new_width) // 2
y_position = (screen_height - new_height) // 2

root.geometry(f"{new_width}x{new_height}+{x_position}+{y_position}")

style = ttk.Style()
style.configure("TEntry", padding=5, relief="flat")

label_farm = tk.Label(root, text="Selecione a fazenda para obter o NDVI", font=("TkDefaultFont", 11, "bold"))
label_farm.pack()

farms = ["Esperança", "Harmonia", "Primavera", "Todas"]
combobox_farm = ttk.Combobox(root, values=farms)
combobox_farm.pack(pady=(0, 15))  # Adiciona espaçamento leve após a caixa

label_dates = tk.Label(root, text="Digite o intervalo de datas (pelo menos 10 dias)", font=("TkDefaultFont", 11, "bold"))
label_dates.pack()

entry_start_label = tk.Label(root, text="Data Inicial:", font=("TkDefaultFont", 10))
entry_start_label.pack()

entry_start_date = ttk.Entry(root, width=22)  # Definir a largura do campo de entrada de datas
entry_start_date.pack()

entry_end_label = tk.Label(root, text="Data Final:", font=("TkDefaultFont", 10))
entry_end_label.pack()

entry_end_date = ttk.Entry(root, width=22)  # Definir a largura do campo de entrada de datas
entry_end_date.pack(pady=(0, 15))  # Adiciona espaçamento leve após a caixa

button = tk.Button(root, text="Processar", command=processar)
button.pack(pady=10)

exported_label = tk.Label(root, text="", fg="green")
exported_label.pack()

warning_message = tk.StringVar()
warning_label = tk.Label(root, textvariable=warning_message, fg="red")
warning_label.pack()

root.mainloop()
