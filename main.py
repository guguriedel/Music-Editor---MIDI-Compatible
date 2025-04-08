import tkinter as tk
import tempfile
import os
from tkinter import ttk, filedialog, messagebox, simpledialog
#pip install mido python-rtmidi

#pip install pygame
from mido import Message, MidiFile, MidiTrack, MetaMessage
import pygame

#Fazer pausa e undo button

# Variáveis globais
note_count = 0  # Contador de notas por compasso
x_position = 100 
line = 0
num_measures = 4  # Quantidade de compassos por linha de partitura - MUDAR DPSS
measure_time = 0
time_per_mesaure = 4
vert_lst_pos = []
notes_lst = []
comp_number = 0

#Funcao imp/exp play MIDI - INACABADO

# Posições das notas 
note_positions_clef_G = {
    "E": 122,   # Mi, primeira linha
    "F": 112, "F#": 112, # Fá, primeiro espaço
    "G": 102, "G#": 102, # Sol, segunda linha
    "A": 92, "A#": 92,   # Lá, segundo espaço
    "B": 82,   # Si, terceira linha
    "C": 132, "C#": 132,   # Dó, terceiro espaço
    "D": 127, "D#": 127,  # Ré, quarta linha
    "C2": 72, "C2#": 72,   # Mi, quarto espaço
}
note_positions_clef_F = {
    "G": 123, 
    "A": 113,  
    "B": 103,  
    "C": 93,   
    "D": 83,   
    "E": 73,   
    "F": 63,   
    "G2": 53   
} #Dito que teremos só uma oitava não faz sentido fazer mais de uma clave. Estamos sempre desenhando C4 até C5.

# Símbolos das notas
note_symbols = {
    "Semibreve": "𝅗", #4 TEMPOS
    "Minima": "𝅗𝅥", #2 TEMPO
    "Seminima": "𝅘𝅥", #1 TEMPO
    "Colcheia": "𝅘𝅥𝅮", # 1/2 TEMPO
    "Semicolcheia": "𝅘𝅥𝅯", # 1/4 TEMPO
    "Pausa Seminima": "𝄽"   # Pausa de 1 tempo
}

# Tabela de conversão de notas para valores MIDI
note_to_midi = {
    "C" : 60, "C#" : 61, "D": 62, "D#":63, "E":64, "F":65, "F#":66, "G":67, "G#":68, "A":69, "A#":70, "B":71, "C2":72
}

# Tabela de durações de notas em ticks (assumindo resolução padrão de 480 ticks por batida)
note_durations = {
    "Semibreve": 1920,   # 4 tempos
    "Minima": 960,       # 2 tempos
    "Seminima": 480,     # 1 tempo
    "PausaSeminima": 480, "Pausa": 480,
    "Colcheia": 240,     # 1/2 tempo
    "Semicolcheia": 120, # 1/4 tempo
}

def midi():
    # Cria um arquivo MIDI e adiciona as notas
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Adiciona informações de BPM e compasso
    bpm = 120
    tempo = int(60000000 / bpm)  # Calcula o tempo em microssegundos por batida
    track.append(MetaMessage('set_tempo', tempo=tempo))  # Define o BPM
    track.append(MetaMessage('time_signature', numerator=time_per_mesaure, denominator=num_measures, clocks_per_click=24, notated_32nd_notes_per_beat=8))  # Define o compasso 4/4

    time_elapsed = 0  # Tempo inicial
    for note in notes_lst:
        if 'Pausa' in note:
            duration = note_durations.get(note["tempo"], None)  # Obtém duração da pausa em ticks
            if duration:
                time_elapsed += duration  # Acumula o tempo da pausa
        else:
            # Se for uma nota musical e não uma pausa
            pitch = note_to_midi.get(note["Nota"], None)  # Converte nota para número MIDI
            duration = note_durations.get(note["tempo"], None)  # Obtém duração em ticks

            if pitch and duration:  # Se a nota e duração forem válidas
                track.append(Message('note_on', note=pitch, velocity=64, time=time_elapsed))
                track.append(Message('note_off', note=pitch, velocity=64, time=duration))
                time_elapsed = 0  # Reseta o tempo acumulado entre eventos

    return mid

def export_midi():
    title = title_entry.get().strip()

    if not title:
        title = "minha_musica"

    file_path = filedialog.asksaveasfilename(initialfile=f"{title}.mid", defaultextension=".mid",
                                             filetypes=[("MIDI files", "*.mid")])
    if not file_path:
        messagebox.showerror("Erro", "Sem espaço para o arquivo")
        return

    midi_file = midi()

    midi_file.save(file_path)
    messagebox.showinfo("Exportação", f"Arquivo MIDI exportado com sucesso!\n{file_path}")

    return

def play_midi():

    # Cria um arquivo temporário para salvar o MIDI
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_file:
        midi_path = temp_file.name  # Salva o caminho do arquivo temporário

    midi_file = midi()

    midi_file.save(midi_path)

    #Inicializa o arquivo
    print("Tocando partitura...")
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(midi_path)  # Carrega o arquivo MIDI
        pygame.mixer.music.play()  # Reproduz o arquivo MIDI

        # Aguarda até a música terminar antes de prosseguir
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)  # Espera 100 ms para verificar o status
    finally: #Executa só após o while
        # Finaliza o mixer e remove o arquivo temporário
        pygame.mixer.quit()
        if os.path.exists(midi_path):
            os.remove(midi_path)  # Deleta o arquivo temporário

def import_midi():
    draw_partitura()
    file_path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid")])
    if not file_path:
        return

    try:
        midi_file = MidiFile(file_path)
        ticks_per_beat = midi_file.ticks_per_beat

        # Tempo padrão por beat (120 BPM)
        tempo_per_beat = 500000
        for msg in midi_file.tracks[0]:
            if msg.type == 'set_tempo':
                tempo_per_beat = msg.tempo
                break

        for track in midi_file.tracks:
            current_time = 0
            last_event_time = 0  # Para calcular pausas
            note_on_time = {}

            for msg in track:
                current_time += msg.time  # Atualiza tempo absoluto

                # Verifica pausa entre eventos
                if current_time - last_event_time > 0 and not note_on_time:
                    pause_duration_ticks = current_time - last_event_time
                    pause_type = next(
                        (key for key, value in note_durations.items() if value == pause_duration_ticks), None
                    )
                    if pause_type:
                        pausa()

                if msg.type == 'note_on' and msg.velocity > 0:
                    if msg.note not in note_on_time:
                        note_on_time[msg.note] = current_time
                    else:
                        print(f"Aviso: Nota {msg.note} já está ativa. Ignorando segundo 'note_on'.")

                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in note_on_time:
                        start_time = note_on_time[msg.note]
                        duration_ticks = current_time - start_time
                        if duration_ticks < 0:
                            print(f"Erro: Duração negativa detectada para nota {msg.note}. Ignorando evento.")
                            continue
                        del note_on_time[msg.note]

                        # Converte duração para segundos
                        duration_seconds = (duration_ticks / ticks_per_beat) * (tempo_per_beat / 1_000_000)

                        # Encontra o tipo de nota
                        note_type = next((key for key, value in note_durations.items() if value == duration_ticks), None)
                        if not note_type:
                            print(f"Aviso: Duração desconhecida ({duration_ticks} ticks).")
                            continue

                        # Encontra o nome da nota
                        note_name = next((name for name, value in note_to_midi.items() if value == msg.note), None)
                        if note_name:
                            draw_note_on_staff(note_name, note_type)
                        else:
                            print(f"Erro: Nota MIDI {msg.note} não reconhecida.")

                    # Atualiza o tempo do último evento
                    last_event_time = current_time

        messagebox.showinfo("Importação", "Arquivo MIDI importado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao importar o arquivo MIDI: {e}")


# Funcao para selecionar a duracao da nota e solicitar a nota musical
def select_note(note_type):
    print(f"Nota de compasso selecionada: {note_type}")
    note = simpledialog.askstring("Nota Musical", f"Digite a nota musical para uma {note_type} (A-G):")
    if note:
        print(f"Nota musical inserida: {note}")
        draw_note_on_staff(note.upper(), note_type)

# Função para obter a posição vertical da nota musical com base na clave de Sol
def get_note_position(note, clef):
    if clef == "Clave de Sol":
        return note_positions_clef_G.get(note, None)
    elif clef == "Clave de Fá":
        return note_positions_clef_F.get(note, None)
    return None

# Avançar a posicao e trocar de linha
def advance_note_position(note_type):
    global x_position, note_count, line, measure_time, time_per_mesaure, comp_number, notes_lst

    #Deixei de usar dps de fzr notas estaticas
    measure_width = (canvas.winfo_width() - 40) / num_measures  # Tamanho do compasso
    note_time = {
        'Semibreve': 4,
        'Minima': 2,
        'Seminima': 1,
        'Pausa': 1,
        'Colcheia': 0.5,
        'Semicolcheia': 0.25
    }.get(note_type, 0)

    # Atualizar o tempo no compasso 
    measure_time += note_time

    # Verificar se excedeu o limite de tempo do compasso
    if measure_time > time_per_mesaure:
        messagebox.showerror("Erro", "Nota excede o limite de tempo do compasso.")
        measure_time -= note_time  # Reverter a alteração
        return

    # Espaçamento da nota no compasso
    note_spacing = 20 #(measure_width * note_time) / time_per_mesaure
    x_position += note_spacing
    note_count += 1  # Incrementa o contador de notas no compasso

    remaining_time = time_per_mesaure - measure_time
    print(f"Tempo restante no compasso: {remaining_time}")

    # Se o compasso estiver cheio, avança para o próximo
    if measure_time == time_per_mesaure:
        comp_number += 1
        x_position  = 10 + vert_lst_pos[comp_number]  # Ajustar para o fim do compasso
        measure_time = 0  # Reinicia o tempo do compasso
        note_count = 0  # Reinicia a contagem de notas no compasso

    # Verifica se ultrapassou o limite horizontal da partitura
    if x_position >= canvas.winfo_width() - 40:
        x_position = 100  # Reinicia na margem esquerda
        line += 1  # Vai para a próxima linha
        comp_number = 0


def pausa():
    draw_note_on_staff(None, 'Pausa')
    return

# Desenha a nota
def draw_note_on_staff(note, note_type):
    clef = clef_var.get()
    if note == None:
        y_position = None
    else:
        y_position = get_note_position(note, clef)
    if y_position is not None:
        symbol = note_symbols.get(note_type)
        canvas.create_text(x_position, y_position + line * 100, text=symbol, font=("Noto Music", 18))

    # Desenhar linha curta para as notas C ou C# (exceto C2 e C2#)
        if note in ["C", "C#"]:
            canvas.create_line(
                x_position - 10, y_position+ 8 + line * 100,  # Início da linha curta
                x_position + 10, y_position + 8 + line * 100,  # Fim da linha curta
                width=1
            )
        
        if "#" in note:
            canvas.create_text(x_position+7, y_position+ 6 + line * 100, text='#', font=("Noto Music", 10))
        print(f"Desenhando {note} como {note_type} na posição ({x_position},{y_position})")
        advance_note_position(note_type)

        note = {"Nota": note, "tempo": note_type}
        notes_lst.append(note)
    elif 'Pausa' in note_type:
        canvas.create_text(x_position, 90 + line * 100, text='𝄽', font=("Noto Music", 24))
        note = {"Pausa": True, "tempo": 'Seminima'}
        print(f"Desenhando {note} como {note_type} na posição ({x_position},{y_position})")
        advance_note_position(note_type)
        notes_lst.append(note)
    else:
        print(f"Nota {note} não encontrada para a clave {clef}")

#Select a clave
def select_clef(event):
    draw_partitura()

#Select o tempo
def select_meter(event):
    global num_measures, time_per_mesaure
    meter = meter_var.get()

    time_per_mesaure = int(meter[0])
    num_measures = int(meter[-1]) #8
    print("Tempo por compasso", time_per_mesaure)
    print("Numero de compassos", num_measures)
    draw_partitura()

# Desenha fundo da partitura - claves, linhas e compassos
def draw_partitura():
    global x_position, note_count, line, measure_time, vert_lst_pos, notes_lst, comp_number

    #Resseta Var Globais
    note_count = 0  # Contador de notas por compasso
    x_position = 100 
    line = 0
    measure_time = 0
    vert_lst_pos = []
    notes_lst = []
    comp_number = 0
    canvas.delete("all")  # Limpa o Canvas

    width = canvas.winfo_width()  # Largura dinâmica
    line_spacing = 20  # Espaço entre as linhas da partitura
    staff_height = 100  # Altura de cada linha de partitura
    left_margin = 80  # Margem para a clave e o número do compasso
    total_measure_width = width - left_margin - 40  # Largura restante para os compassos
    measure_width = total_measure_width / num_measures  # Largura de cada compasso

    # Desenhar 5 linhas de partitura
    for j in range(6):  # Número de linhas de partitura
        # Coordenada Y inicial para esta linha
        staff_top = 50 + j * staff_height

        for i in range(5):  # 5 linhas por linha de partitura
            y = staff_top + i * line_spacing
            canvas.create_line(0, y, width - 20, y)

        # Clave de Sol ou Fá no início da linha
        clef = clef_var.get()
        if clef == "Clave de Sol":
            canvas.create_text(left_margin - 50, staff_top + 40, text="𝄞", font=("Noto Music", 37))
        elif clef == "Clave de Fá":
            canvas.create_text(left_margin - 50, staff_top + 30, text="”", font=("Hymnus FG", 45))

        # Número do compasso (em fração)
        meter = meter_var.get()
        numerator, denominator = map(int, meter.split("/"))
        canvas.create_text(left_margin - 20, staff_top + 20, text=str(numerator), font=("Arial", 20))
        canvas.create_text(left_margin - 20, staff_top + 40, text=str(denominator), font=("Arial", 20))


        vert_lst_pos = []
        # Desenhar linhas dos compassos
        for i in range(num_measures + 1):  # Inclui a última linha vertical
            x = left_margin + i * measure_width
            canvas.create_line(x, staff_top, x, staff_top + 80)
            vert_lst_pos.append(x)





# Redimensiona
def resize_canvas(event):
    draw_partitura()

# Configuração da janela principal
root = tk.Tk()
root.title("Editor de Partitura")

# Adicionar campo para o título
title_frame = tk.Frame(root)
title_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
tk.Label(title_frame, text="Título da Música:").pack(side=tk.LEFT, padx=5)
title_entry = tk.Entry(title_frame)
title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Configuração dos frames e canvas
toolbar_top = tk.Frame(root)
toolbar_top.pack(side=tk.TOP, fill=tk.X)
toolbar_bottom = tk.Frame(root)
toolbar_bottom.pack(side=tk.BOTTOM, fill=tk.X)
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(canvas_frame, width=800, height=500, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<Configure>", resize_canvas)  # Evento para redimensionamento

tk.Button(toolbar_top, text="Pausa", command=pausa).pack(side=tk.LEFT, padx=2, pady=2)
# Bot para selecionar notas
note_types = ["Semibreve", "Minima", "Seminima", "Colcheia", "Semicolcheia"]
for note in note_types:
    btn = tk.Button(toolbar_top, text=note, command=lambda n=note: select_note(n))
    btn.pack(side=tk.LEFT, padx=2, pady=2)



# Dropdowns para seleção de clave e compasso
clef_var = tk.StringVar()
clef_var.set("Clave de Sol")

'''clef_menu = ttk.Combobox(toolbar_top, textvariable=clef_var, values=["Clave de Sol", "Clave de Fá"])
clef_menu.bind("<<ComboboxSelected>>", select_clef)
clef_menu.pack(side=tk.LEFT, padx=5)
'''
meter_var = tk.StringVar()
meter_var.set("4/4")
meter_menu = ttk.Combobox(toolbar_top, textvariable=meter_var, values=["4/4", "3/4", "2/4", "3/8"])
meter_menu.bind("<<ComboboxSelected>>", select_meter)
meter_menu.pack(side=tk.LEFT, padx=5)

# Botões de exportação, importação e reprodução na parte inferior
tk.Button(toolbar_bottom, text="Exportar MIDI", command=export_midi).pack(side=tk.LEFT, padx=2, pady=2)
tk.Button(toolbar_bottom, text="Importar MIDI", command=import_midi).pack(side=tk.LEFT, padx=2, pady=2)
tk.Button(toolbar_bottom, text="Tocar Partitura", command=play_midi).pack(side=tk.LEFT, padx=2, pady=2)


# Desenhar partitura inicial
draw_partitura()


root.mainloop()
