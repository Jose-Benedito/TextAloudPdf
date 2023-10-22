import PyPDF2
import pyttsx3
from gtts import gTTS
import os
import pygame
from pydub import AudioSegment
import threading
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, Button, messagebox, Scale

class PDFReader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Reader")
        self.geometry("850x750")

        self.textview = scrolledtext.ScrolledText(self, wrap=tk.WORD,padx=100, font=("Times New Roman", 12))
        
        self.button_load = Button(self, text="Carregar PDF", bg="black", fg="white",  font=("Helvetica", 12), command=self.on_button_load_clicked)
       
        self.button_play = Button(self, text="Play",bg="green", fg="white",  font=("Helvetica", 12), command=self.on_button_play_clicked)

        self.button_pause = Button(self, text="Pause",bg="yellow", fg="black",  font=("Helvetica", 12), state=tk.DISABLED, command=self.on_button_pause_clicked)

        self.button_stop = Button(self, text="Stop",bg="red", fg="white",  font=("Helvetica", 12), state=tk.DISABLED, command=self.on_button_stop_clicked)

     
        
       # self.speed_scale = Scale(self, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="Velocidade de Fala")
        
        self.button_load.pack()
        self.textview.pack(expand=True, fill="both")
        self.button_play.pack()
        self.button_pause.pack()
        self.button_stop.pack()
        
       # self.speed_scale.pack()

        self.current_page = 0
        self.text = ""
        self.audio_engine = pyttsx3.init()
        self.playing = False  # Variável de sinalização para controlar a reprodução
       # self.speed = "1.3"  # Velocidade padrão

    def on_button_load_clicked(self):
        filetypes = (("PDF files", "*.pdf"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Por favor, escolha um arquivo em PDF.", filetypes=filetypes)
        if filename:
            self.load_pdf(filename)

    def load_pdf(self, filename):
        pdf_file = open(filename, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        num_pages = pdf_reader.getNumPages()

        self.current_page = 0
        self.text = ""

        for page_number in range(num_pages):
            page = pdf_reader.getPage(page_number)
            self.text += page.extractText()

        self.textview.delete(1.0, tk.END)
        self.textview.insert(tk.END, self.text)

    def on_button_play_clicked(self):
        self.button_play["state"] = tk.DISABLED
        self.button_pause["state"] = tk.NORMAL
        self.button_stop["state"] = tk.NORMAL
        
      #  self.speed = self.speed_scale.get()  # Obter a velocidade a partir do controle deslizante

        text = self.textview.get(1.0, tk.END)
        periods = re.split(r'(?<=[.!?])', text)  # Separar períodos com base em pontuações finais

        # Exibir mensagem de alerta
        dialog = messagebox.showinfo("Aguarde", "A conversão do áudio está sendo realizada. O áudio estará pronto em breve.")

        threading.Thread(target=self.convert_periods_to_audio, args=(periods, dialog)).start()

    def on_button_pause_clicked(self):
        #pygame.mixer.music.pause()
       # os.system("pause "+"audio/audio.mp3")
        os.system("pactl set-sink-mute @DEFAULT_SINK@ toggle")

    def on_button_stop_clicked(self):
        pygame.mixer.music.stop()
        self.playing = False  # Sinaliza a reprodução para parar
        self.button_play["state"] = tk.NORMAL
        self.button_pause["state"] = tk.DISABLED
        self.button_stop["state"] = tk.DISABLED
   
    def convert_periods_to_audio(self, periods, dialog):
        pygame.mixer.init()
        self.playing = True  # Inicia a reprodução

        for period in periods:
            if not self.playing:
                break  # Verifica se a reprodução deve ser interrompida

            # Destacar o período com um marcador de cor (amarelo)
            start_pos = self.textview.search(period, 1.0, tk.END)
            end_pos = self.textview.index(f"{start_pos}+{len(period)}c")
            self.textview.tag_add("highlight", start_pos, end_pos)
            self.textview.tag_configure("highlight", background="yellow")

            tts = gTTS(text=period, lang='pt-br', slow=False)  # Usar a velocidade configurada
            tts.save('audio/audio.mp3')
            #pygame.mixer.music.load('audio/audio.mp3')
            #pygame.mixer.music.play()
           # audio = AudioSegment.from_file("audio/audio.mp3", format="mp3")
            #audio = AudioSegment.from_mp3("audio/audio.mp3")
            # export to mp3
            #final.export("final.mp3", format="mp3")
            os.system("play " + "audio/audio.mp3 " + "tempo 1.3")

        
           # audio.speedup(playback_speed=2.0) # speed up by 2x

            while pygame.mixer.music.get_busy():
                if not self.playing:
                    #pygame.mixer.music.stop()

                    # Parar a reprodução de áudio no Linux usando pactl
                    os.system("pactl suspend-sink @DEFAULT_SINK@ 1")

                    break

            # Remover o destaque após a reprodução
            self.textview.tag_remove("highlight", start_pos, end_pos)

        dialog.destroy()
        self.playing = False  # Garante que a variável de sinalização seja redefinida

    def on_destroy(self):
        self.playing = False  # Sinaliza a reprodução para parar
        self.destroy()

if __name__ == '__main__':
    app = PDFReader()
    app.protocol("WM_DELETE_WINDOW", app.on_destroy)
    app.mainloop()
