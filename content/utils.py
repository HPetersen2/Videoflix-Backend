import subprocess
import os

def convert_video(source, resolution):
    file_directory = os.path.dirname(source)
    file_name = os.path.splitext(os.path.basename(source))
    new_file_name = f"{file_name}_{resolution}p.mp4"
    mp4_dir = os.path.join(file_directory, "mp4")
    os.makedirs(mp4_dir, exist_ok=True)
    new_file_path = os.path.join(mp4_dir, new_file_name)
    
    cmd = f"ffmpeg -i '{source}' -s {resolution} -c:v libx264 -crf 23 -c:a aac -strict -2 '{new_file_path}'"
    run = subprocess.run(cmd, capture_output=True, shell=True)
    print(run.stderr)