from moviepy.editor import VideoFileClip
def trim_video(input_path, output_path, start_time=0, end_time=60):
    video_clip = VideoFileClip(input_path)
    trimmed_clip = video_clip.subclip(start_time, end_time)
    trimmed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    video_clip.reader.close()
