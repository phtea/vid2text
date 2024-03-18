import io
import os
import pickle
import argparse
# import sys
# import numpy as np
from play_text import play_text
from time import perf_counter
from datetime import datetime
import cv2
from PIL import Image, ImageFilter
import moviepy.editor as mp




WIDTH = 120
INDEX = 0
LYRICS = []
ONLY_EDGES = False

def frame_capture(path_to_video):
    print("Capturing frames...")
    # global IMAGES
    images_list = []
    cap = cv2.VideoCapture(path_to_video)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_number = 0
    success = 1
    while success:
        success, image = cap.read()
        if success is False:
            break
        _, buffer = cv2.imencode(".png", image)
        byte_im = buffer.tobytes()
        images_list.append(byte_im)
        frame_number += 1
        print(f"__{frame_number}/{frame_count}\r", end="")
    return images_list


def quine_to_list():
    global LYRICS
    with io.open(__file__, mode="r", encoding="utf-8") as f:
        lyrics = f.read().replace("\u3000", " ")
        lyrics = lyrics.replace("\n", " ")
        for i in range(1, 4):
            lyrics = lyrics.replace(" " * i, " ")
        lyrics = lyrics.replace(" " * 3, " ")
        lyrics = lyrics.replace("SEPARATOR", "sep")
        lyrics = lyrics.replace(" " * 2, " ")[::-1]
        LYRICS = list(lyrics)


def text_to_list():
    global LYRICS
    lyrics = "lagtrain"
    LYRICS = list(lyrics)


def pop_and_insert(lyrics_list: list):
    first = lyrics_list.pop()
    lyrics_list.insert(0, first)
    return lyrics_list


ASCII_CHARS_FUNCS = [lambda lyrics_list: [" "], pop_and_insert]
ASCII_CHARS = list("  .,,;")


def resize(image, new_width=WIDTH, new_height=None):
    (old_width, old_height) = image.size
    if new_height is None:
        aspect_ratio = float(old_height) / float(old_width)
        new_height = int((aspect_ratio * new_width))
    new_dim = (new_width, new_height)
    new_image = image.resize(new_dim)
    return new_image


def modify(image, type):
    """
    Modify the given image using ASCII characters based on the provided type.

    Parameters:
        image (PIL.Image.Image): The input image to be modified.
        type (int): The type of modification to apply.
            - 0: Perform simple ASCII conversion using predefined characters (ASCII_CHARS).
            - 1: Perform ASCII conversion using characters generated from custom functions (ASCII_CHARS_FUNCS).

    Returns:
        str: The modified image represented as a string with ASCII characters.
    """
    match type:
        case 0:
            global ASCII_CHARS
            buckets = 256 // (len(ASCII_CHARS) - 1)
            initial_pixels = list(image.getdata())
            new_pixels = [ASCII_CHARS[pixel_value // buckets] for pixel_value in initial_pixels]
            return ''.join(new_pixels)
        case 1:
            global LYRICS
            global ASCII_CHARS_FUNCS
            buckets = 256 // len(ASCII_CHARS_FUNCS)
            initial_pixels = list(image.getdata())
            new_pixels = [ASCII_CHARS_FUNCS[pixel_value // buckets](LYRICS)[-1] for pixel_value in initial_pixels]
            return ''.join(new_pixels)


def do(image, new_width=WIDTH, new_height=None, kof="list"):
    """
    Resizes the given image and performs additional modifications based on the provided parameters.

    Parameters:
        image (PIL.Image.Image): The input image to be processed.
        new_width (int): The desired width of the output image. Defaults to WIDTH.
        new_height (int): The desired height of the output image. Defaults to None.
        kof (str): The type of modification to be applied. Can be "list", "quine", or "text". Defaults to "list".
    Returns:
        str: The modified image represented as a string, with each row separated by a newline character.
    """
    image = resize(image, new_height=new_height, new_width=new_width)
    image = image.convert('L') # turn_gray
    if ONLY_EDGES:
        image = image.filter(ImageFilter.FIND_EDGES)
        original_size = image.size
        image = image.crop((1, 1, image.width - 1, image.height - 1))
        image = image.resize(original_size)

    pixels = None
    if kof == "list":
        pixels = modify(image, 0)
    elif kof in ("quine", "text"):
        pixels = modify(image, 1)
    len_pixels = len(pixels)
    new_image = [pixels[index:index + int(new_width)] for index in range(0, len_pixels, int(new_width))]
    return '\n'.join(new_image)


def runner(image, new_height=None, kof="list"):
    global WIDTH
    try:
        image = Image.open(io.BytesIO(image))
    except Exception as e:
        print(e)
        return
    image = do(image, new_height=new_height, new_width=WIDTH, kof=kof)
    return image


def vid2text(name_of_dump, images_list, to_dump=True, new_height=None, new_width=None, kof="list"):
    """
    Converts a list of images to text frames using the specified method (kof).

    Parameters:
        name_of_dump (str): The name of the file where the converted frames will be saved.
        images_list (list): A list of image data in bytes format to be converted.
        to_dump (bool): If True, the converted frames will be pickled and saved to a binary file.
                     If False, the frames will be saved to a text file as strings with 'SEPARATOR' between each frame.
        new_height (int): The new height for the frames. If specified, the frames will be resized accordingly.
        new_width (int): The new width for the frames. If specified, the frames will be resized accordingly.
        kof (str): The method for converting images to text frames. Available options: 'list', 'quine', 'text'.

    Returns:
        None: The function saves the converted frames to a file specified by name_of_dump.

    Note:
        This function uses the global variable WIDTH, which can be modified externally to change the frame width.

    Example:
        # Convert images in the images_list to text frames and save them to "output_file.txt"
        vid2text("output_file", images_list, dump=False, new_height=40, new_width=80, kof="text")
    """
    print("Dumping file...")
    global WIDTH
    if kof == "quine":
        quine_to_list()
    elif kof == "text":
        text_to_list()
    if new_width is not None:
        WIDTH = new_width
    frames = []
    index = 0
    indexes = len(images_list)
    for image in images_list:
        frames.append(runner(image, new_height=new_height, kof=kof))
        print(f"__{index}/{indexes}\r", end="")
        index += 1
    if not os.path.isdir("output"):
        os.mkdir("output")
    name_of_dump = "output/" + name_of_dump
    if to_dump is True:
        with open(name_of_dump, "wb") as fp:  # Pickling
            pickle.dump(frames, fp)
    else:
        name_of_dump = name_of_dump + ".txt"
        with open(name_of_dump, "w") as fp:  # Writing to file as string
            for frame in frames:
                fp.write(frame)
                fp.write("SEPARATOR")
    print(f"Hooray. {name_of_dump} is dumped!\n")


def get_vid_fps(vid_name):
    vid = cv2.VideoCapture(vid_name)
    return int(vid.get(cv2.CAP_PROP_FPS))


def get_name_of_dump(name):
    now = datetime.now()
    name = os.path.basename(name)
    return os.path.splitext(name)[0] + now.strftime("_%d_%m_%Y_%H_%M_%S")


def main(input, output, only_edges, kof, loop):
    global ONLY_EDGES
    start_time = perf_counter()
    name_of_dump_file = get_name_of_dump(input)
    try:
        terminal_width, terminal_height = os.get_terminal_size()
    except:
        terminal_width, terminal_height = 120, 30
    # terminal_width, terminal_height = 18, 5
    if only_edges:
        ONLY_EDGES = True
    else:
        ONLY_EDGES = False
    fps = get_vid_fps(input)
    if output is None:
        images = frame_capture(input)
        vid2text(name_of_dump_file, images, to_dump=False, new_width=terminal_width, new_height=terminal_height, kof=kof)
        del images
        path = "output/" + name_of_dump_file + ".txt"
    else:
        path = output
    end_time = perf_counter()
    print(end_time - start_time)
    play_text(path, path_to_video=input, fps=fps, loop=loop)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Help for using this code.")
    parser.add_argument("-i", "--input", default="input/bad_apple.mp4", help="Path to the input file.")
    parser.add_argument("-o", "--output", default=None, help="Path to the output file.")
    parser.add_argument("-oe", "--only_edges", default=False, action="store_true", help="Show only edges")
    parser.add_argument("-l", "--loop", default=False, action="store_true", help="Loop the video")
    parser.add_argument("-kof", "--kind_of_file", default="list", help="Kind of output file. Available: list/quine/text")

    args = parser.parse_args()
    main(args.input, args.output, args.only_edges, args.kind_of_file, args.loop)
