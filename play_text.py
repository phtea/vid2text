import time
# import os
import vlc
import moviepy.editor as mp
# import sys


# play text on cmd terminal
def play_text(path_to_text, path_to_video, fps=15.3, loop=False):
    with open(path_to_text, "r") as f:
        f = f.read()
        frames = f.split("SEPARATOR")
    output_folder = "output/"
    clip = mp.VideoFileClip(path_to_video)
    audiofile = output_folder + "audio.mp3"
    try:
        clip.audio.write_audiofile(audiofile)
    except:
        print("Wrong extension of file used to play audio. Try using .mp4 instead")
    print(f"Playing in {fps} FPS... Unless you wanna type your own:")
    input_fps = input()
    if input_fps == "":
        pass
    else:
        fps = float(input_fps)
    p = vlc.MediaPlayer(audiofile)
    p.audio_set_volume(50)
    p.play()
    flag = 0
    if loop:
        try:
            while True:
                play_every_frame(fps, frames, flag)
        except KeyboardInterrupt:
            print("Stopped by user.")
    else:
        try:
            play_every_frame(fps, frames, flag)
        except KeyboardInterrupt:
            print("Stopped by user.")
    p.stop()

def play_every_frame(fps, frames, flag):
    for i in frames:
        out = i + f"\nphtea/frame{flag:04d}"
        print(out)
        time.sleep(1 / fps)
        flag = flag + 1


# entry point
if __name__ == "__main__":
    # play_text("output/lagtrain_quine_fullscreen.txt", path_to_video="input/lagtrain.mp4")
    play_text()