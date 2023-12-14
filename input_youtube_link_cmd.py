import torch
import whisper
from pytube import YouTube
import argparse
import os
from typing import Iterator
from io import StringIO
from utils import write_vtt, write_srt
import subprocess
from languages import LANGUAGES
import random
from moviepy.editor import VideoFileClip
import generate_clip
torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
loaded_model = whisper.load_model("small", device=DEVICE)

def populate_metadata(link):
    yt = YouTube(link)
    author = yt.author
    title = yt.title
    description = yt.description
    thumbnail = yt.thumbnail_url
    length = yt.length
    views = yt.views
    return author, title, description, thumbnail, length, views

def download_video(url, ruta_guardado):

    output_path = str(random.randint(100000, 999999))+".mp4"

    # Crear un objeto YouTube con la URL del video
    video = YouTube(url)

    # Seleccionar la mejor resolución disponible
    stream = video.streams.get_highest_resolution()

    # Descargar el video en la ubicación especificada
    stream.download(output_path=ruta_guardado, filename=output_path)

    print(f"Video descargado y guardado en: {ruta_guardado}{output_path}")
    output_path = ruta_guardado+output_path
    return output_path

def inference(link, loaded_model, task, save_dir):
    yt = YouTube(link)
    path = yt.streams.filter(only_audio=True)[0].download(filename=os.path.join(save_dir, "audio.mp3"))
    
    if task == "Transcribir":
        options = dict(task="transcribe", best_of=1)
        results = loaded_model.transcribe(path, **options)
        vtt = get_subs(results["segments"], "vtt", 80)
        srt = get_subs(results["segments"], "srt", 80)
        lang = results["language"]
        return results["text"], vtt, srt, lang
    elif task == "Traducir":
        options = dict(task="translate", best_of=5)
        results = loaded_model.transcribe(path, **options)
        vtt = get_subs(results["segments"], "vtt", 80)
        srt = get_subs(results["segments"], "srt", 80)
        lang = results["language"]
        return results["text"], vtt, srt, lang
    else:
        raise ValueError("Tarea no compatible")

def get_subs(segments: Iterator[dict], format: str, max_line_width: int) -> str:
    segment_stream = StringIO()

    if format == 'vtt':
        write_vtt(segments, file=segment_stream, maxLineWidth=max_line_width)
    elif format == 'srt':
        write_srt(segments, file=segment_stream, maxLineWidth=max_line_width)
    else:
        raise Exception("Formato desconocido " + format)

    segment_stream.seek(0)
    return segment_stream.read()

def get_language_code(language):
    if language in LANGUAGES.keys():
        detected_language = LANGUAGES[language]
        return detected_language
    else:
        raise ValueError("Language not supported")

def generate_subtitled_video(video, audio, transcript, output_dir):
    output_path = os.path.join(output_dir, video.replace(".mp4","_sub.mp4"))
    
    # Ejecutar ffmpeg desde la línea de comandos
    #cmd ='ffmpeg -i '+video+' -i '+audio+' -vf "subtitles='+transcript.replace("\\", "\\\\")+':original_size=hd720" -c:a aac -strict experimental -b:a 192k '+output_path
    cmd ='ffmpeg -i '+video+' -i '+audio+' -vf "subtitles='+transcript.replace("\\", "\\\\")+':force_style=" -c:a aac -strict experimental -b:a 192k '+output_path
    cmd = cmd.replace("subtitles=", "subtitles='").replace(":force_style=", "':force_style='FontName=Arial Bold,FontSize=30':original_size=hd720").replace("C:\\\\", "C\\:\\\\")
    #cmd = cmd.replace("subtitles=", "subtitles='").replace(":force_style=", "':force_style='FontName=Arial Bold,FontSize=30,OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=1':original_size=hd720").replace("C:\\\\", "C\\:\\\\")    
    print(cmd)
    subprocess.run(cmd, check=True)


def generar_clips_aleatorios(input_path, output_path_prefix, clip_duration=59):
    # Cargar el video
    clip = VideoFileClip(input_path)

    # Obtener la duración total del video
    total_duration = clip.duration

    # Verificar si el video es lo suficientemente largo para dos clips de la duración deseada
    if total_duration < 2 * clip_duration:
        raise ValueError("El video no es lo suficientemente largo para dos clips de {} segundos cada uno.".format(clip_duration))

    # Obtener dos puntos aleatorios en el tiempo para dividir el video
    split_point_1 = random.uniform(0, total_duration - clip_duration)
    split_point_2 = split_point_1 + clip_duration

    # Extraer los dos clips
    clip_1 = clip.subclip(split_point_1, split_point_1 + clip_duration)
    clip_2 = clip.subclip(split_point_2, split_point_2 + clip_duration)

    # Guardar los clips resultantes
    clip_1.write_videofile(output_path_prefix + "_clip1.mp4", codec="libx264", audio_codec="aac")
    clip_2.write_videofile(output_path_prefix + "_clip2.mp4", codec="libx264", audio_codec="aac")


# def trim_video(input_path, output_path, start_time=0, end_time=60):
#     video_clip = VideoFileClip(input_path)
#     trimmed_clip = video_clip.subclip(start_time, end_time)
#     trimmed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
#     video_clip.reader.close()
   

def main():
    parser = argparse.ArgumentParser(description='Generador automático de videos subtitulados')
    parser.add_argument('link', type=str, help='Enlace del video de YouTube')
    parser.add_argument('task', type=str, choices=['Transcribir', 'Traducir'], help='Tipo de tarea: Transcribir o Traducir')
    parser.add_argument('output_dir', type=str, help='Directorio para guardar el video generado')
    args = parser.parse_args()

    link = args.link
    task = args.task
    output_dir = args.output_dir

    # Asegúrate de que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    author, title, description, thumbnail, length, views = populate_metadata(link)
    results = inference(link, loaded_model, task, output_dir)
    video = download_video(link, output_dir)
    lang = results[3]
    detected_language = get_language_code(lang)

    transcript_path = os.path.join(output_dir, "transcript.srt")
    with open(transcript_path, "w", encoding="utf-8") as transcript_file:
        transcript_file.write(results[1])  # Assuming that the subtitles are in VTT format

    generate_subtitled_video(video, os.path.join(output_dir, "audio.mp3"), transcript_path, output_dir)
    os.remove(os.path.join(output_dir, "audio.mp3"))
    os.remove(transcript_path)
    os.remove(video)
    # Especifica la ruta del video de entrada y salida
    input_video_path = os.path.join(output_dir, video.replace(".mp4","_sub.mp4"))
    #output_video_path = "clip.mp4"

    # Llama a la función para obtener el primer minuto del video
    generate_clip.trim_video(input_video_path, input_video_path.replace("sub","clip"))
    #os.remove(input_video_path)

if __name__ == "__main__":
    main()
