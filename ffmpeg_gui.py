import tkinter as tk
from tkinter import messagebox, StringVar, Checkbutton
import subprocess
import re
import os
import unicodedata

# Función para limpiar caracteres especiales del título
def clean_filename(filename):
    # Normalizar el texto para separar caracteres con tilde
    nfkd_form = unicodedata.normalize('NFKD', filename)
    
    # Eliminar caracteres diacríticos (tildes)
    without_diacritics = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Reemplazar caracteres no permitidos, incluyendo puntos
    cleaned_filename = re.sub(r'[\\/*?:"<>|()]', "_", without_diacritics)
    cleaned_filename = re.sub(r'\.', "", cleaned_filename)
    
    return cleaned_filename

# Función para ejecutar FFmpeg y extraer metadatos
def analyze_video():
    video_url = entry.get()
    if not video_url:
        messagebox.showerror("Error", "Por favor, ingresa una URL de video.")
        return
    
    try:
        # Archivo temporal para guardar la metadata
        temp_metadata_file = 'temp_metadata.txt'
        
        # Comando FFmpeg para extraer metadatos y guardarlos en un archivo
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_url,       # Enlace del video
            '-f', 'ffmetadata',    # Formato de salida para los metadatos
            temp_metadata_file     # Archivo de salida
        ]
        
        # Ejecuta el comando FFmpeg
        subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Leer la metadata desde el archivo con codificación utf-8
        with open(temp_metadata_file, 'r', encoding='utf-8') as file:
            metadata_output = file.read()
        
        # Elimina el archivo temporal
        os.remove(temp_metadata_file)
        
        # Loguear la metadata completa en la consola con manejo de codificación
        print("Metadata completa obtenida del video:")
        print(metadata_output)
        
        # Buscar el título en la salida de metadatos
        title_line = None
        for line in metadata_output.splitlines():
            if line.startswith('title='):
                title_line = line
                break
        
        if title_line:
            video_title = title_line.split('=', 1)[1].strip()
            
            # Loguear el título extraído
            print("Título extraído:")
            print(video_title)
            
            # Mostrar el título sin convertir en pantalla
            title_label.config(text=f"Título: {video_title}")
            
            # Aplicar clean_filename solo cuando se use como nombre de archivo
            cleaned_title = clean_filename(video_title)
            title_var.set(cleaned_title)
        else:
            video_title = "Desconocido"
            title_label.config(text="No se encontró título")
        
        # Habilitar campos para descargar subtítulos
        download_button.config(state=tk.NORMAL)
        output_name_entry.config(state=tk.NORMAL)
        use_title_checkbox.config(state=tk.NORMAL)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar FFmpeg: {e}")

# Función para ejecutar FFmpeg y extraer subtítulos
def download_subtitles():
    video_url = entry.get()
    output_name = output_name_var.get()
    
    if not video_url:
        messagebox.showerror("Error", "Por favor, ingresa una URL de video.")
        return
    
    if use_title_var.get():
        output_name = clean_filename(title_var.get())
    
    if not output_name:
        messagebox.showerror("Error", "Por favor, ingresa un nombre de archivo de salida.")
        return
    
    try:
        # Comando FFmpeg para extraer subtítulos
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_url,            # Enlace del video
            '-map', '0:s:0',            # Extraer el primer subtítulo
            '-c:s', 'srt',              # Formato de subtítulos .srt
            f'{output_name}.srt'         # Archivo de salida
        ]
        
        # Ejecuta el comando FFmpeg
        subprocess.run(ffmpeg_command, check=True)
        
        # Mostrar el mensaje de éxito y reiniciar la vista
        messagebox.showinfo("Éxito", f"Subtítulos descargados correctamente como {output_name}.srt.")
        reset_view()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar FFmpeg: {e}")

# Función para habilitar o deshabilitar el campo de entrada del nombre de archivo
def toggle_output_name_entry():
    if use_title_var.get():
        output_name_entry.config(state=tk.DISABLED)
    else:
        output_name_entry.config(state=tk.NORMAL)

# Función para resetear la vista
def reset_view():
    # Restablecer todos los valores a su estado inicial
    entry.delete(0, tk.END)  # Limpiar el campo de entrada de video URL
    title_label.config(text="")  # Limpiar la etiqueta del título
    output_name_var.set("")  # Limpiar el campo de nombre de archivo
    use_title_var.set(False)  # Desmarcar el checkbox
    toggle_output_name_entry()  # Asegurarse de que el campo de nombre esté habilitado
    download_button.config(state=tk.DISABLED)  # Deshabilitar el botón de descarga
    output_name_entry.config(state=tk.DISABLED)  # Deshabilitar el campo de nombre de archivo
    use_title_checkbox.config(state=tk.DISABLED)  # Deshabilitar el checkbox

# Crear la ventana principal
root = tk.Tk()
root.title("JW Subtitle Extractor")
root.geometry("400x300")

# Crear una etiqueta y una entrada de texto para el enlace del video
label = tk.Label(root, text="Ingresa el enlace del video:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

# Botón para analizar el video y mostrar la metadata
analyze_button = tk.Button(root, text="Analizar", command=analyze_video)
analyze_button.pack(pady=10)

# Etiqueta para mostrar el título extraído de los metadatos
title_label = tk.Label(root, text="", wraplength=350, justify="left")
title_label.pack(pady=10)

# Variable para almacenar el nombre de salida del archivo
output_name_var = StringVar()
output_name_entry = tk.Entry(root, textvariable=output_name_var, width=50, state=tk.DISABLED)
output_name_entry.pack(pady=5)

# Opción para usar el título como nombre de archivo
use_title_var = tk.BooleanVar()
use_title_checkbox = Checkbutton(root, text="Usar título como nombre de archivo", variable=use_title_var, command=toggle_output_name_entry, state=tk.DISABLED)
use_title_checkbox.pack(pady=5)

# Botón para descargar subtítulos
download_button = tk.Button(root, text="Descargar Subtítulos", command=download_subtitles, state=tk.DISABLED)
download_button.pack(pady=10)

# Variable para almacenar el título
title_var = StringVar()

# Iniciar la aplicación
root.mainloop()
