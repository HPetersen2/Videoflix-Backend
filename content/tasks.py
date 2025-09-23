import subprocess

def convert_480p(source):
    target = source + '_480p.mp4'
    cmd = 'ffmpeg-i"{}"-shd720-c:vlibx264-crf23-c:aaac-strict-2"{}'.format(source, target)
    subprocess.run(cmd)