import argparse
import numpy as np 
import cv2
import logging as log
import os
import toml
import struct

CONFIG = {}
ARGS = {}
IMAGE = None


def folderread(path):
    """_summary_

    Args:
        path (_type_): _description_
    """
    import os

    for filename in os.listdir(path):
        # print(f"Found file: {filename}")
        if filename.lower().endswith('.bmp'):
            full_path = os.path.join(path, filename)
            log.info(f"Reading image: {full_path}")
            imageread(full_path)
        else:
            log.info(f"Skipping non-BMP file: {filename}")

def imageread(path: str) -> tuple[np.ndarray, int, int, int]:
    """imageread

    Args:
        path (str): path to the image file

    Raises:
        FileNotFoundError: if the image cannot be read

    Returns:
        tuple[np.ndarray, int, int, int]: _description_
    """
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        log.error(f"Image at path {path} could not be read.")
        raise FileNotFoundError
        return None
    height, width, channels = img.shape
    for y in range(height):
        for x in range(width):
            b, g, r = img[y, x]
            # log.info(f"Pixel at ({x}, {y}): Blue={b}, Green={g}, Red={r}")
    global IMAGE
    IMAGE = img

    process_header()
    process_color_register()
    # process_actor_header()

    return img

def process_header():
# typedef struct {
#         uint32_t fileVersion : 8;
#         uint32_t controlFlags : 8;
#         uint32_t reserved : 16;
#         uint32_t fileLen;
# } FrameFileMetaData;
    log.info("========== Processing header ==========")

    file_version = np.uint8(CONFIG.get('version', 1))
    control_flags = np.uint8(0)
    reserved = np.uint16(0xFFFF)
    headings = np.uint32(file_version) << 24 | np.uint32(control_flags) << 16 | np.uint32(reserved)
    file_len = np.uint32(0x3)

    write_data(headings, file_len)

    # return headings, file_len
    
def process_color_register():
    """Process color register, optionally using a colormap file.

    Args:
        img (np.ndarray): Image array
        colormap_path (str or None):] a
    """
# typedef union {
#     uint32_t code; // The entire 32-bit block
#     struct {
#         uint32_t id    : 8;
#         uint32_t red   : 8;
#         uint32_t green : 8;
#         uint32_t blue  : 8;
#     } channels; // The individual 8-bit components
# } Color;


# typedef union {
#     struct {
#         Color colorMask;
#         Color colors[15];
#     }frame;

#     uint8_t byteMap[sizeof(Color) * 16];
# } ColorRegiste
    log.info("========== Processing color register ==========")
    colors = np.array([], dtype=np.uint32)
    color_mask = np.uint32(0)                   # FIXME: define color mask properly (not 0!!!)
    height, width, channels = IMAGE.shape
    unique_rgbs = set()

    colormap_path = CONFIG.get('colormap_path', None)
    if colormap_path is not None and os.path.exists(colormap_path):
        log.info(f"Loading color palette from {colormap_path}")
        with open(colormap_path, "r") as f:
            i = np.uint8(0)
            for i, line in enumerate(f):
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        rgb_val = int(line, 16)
                        color_id = np.uint32(i)
                        color_code = (color_id << 24) | np.uint32(rgb_val)
                        colors = np.append(colors, color_code)
                        log.info(f"Loaded color code: {color_code:08X}")
                    except ValueError:
                        log.warning(f"Invalid color code in colormap: {line}")
    else:
        log.warning("No colormap file provided or file does not exist. Generating color palette from image.")

        
        for y in range(height):
            if len(colors) >= 15:
                break
            for x in range(width):
                if len(colors) >= 15:
                    break
                b, g, r = IMAGE[y, x]
                rgb_tuple = (r, g, b)
                if rgb_tuple not in unique_rgbs:
                    unique_rgbs.add(rgb_tuple)
                    color_id = np.uint8(len(colors) + 1)
                    color_code = (np.uint32(color_id) << 24) | (np.uint32(r) << 16) | (np.uint32(g) << 8) | np.uint32(b)
                    colors = np.append(colors, color_code)
                    log.info(f"Added color code: {color_code:08X} (R={r}, G={g}, B={b})")

    write_data(color_mask, colors)
    # return color_mask, colors
    
def process_actor_header():
    """
    """
    # Example config structure:
    # CONFIG['actors'] = [
    #   {'id': 0, 'nbOfSprite': 2, 'len': 128},
    #   {'id': 1, 'nbOfSprite': 3, 'len': 256},
    # ]
    log.info("========== Processing actor header ==========")

    actors = CONFIG.get('actors', [])
    nb_of_actors = len(actors)
    player_actor_id = CONFIG.get('player_actor_id', 0)
    life_bar = CONFIG.get('life_bar', 1)
    reserved = 0xFF

    actors_header = struct.pack('BBBB', nb_of_actors, player_actor_id, life_bar, reserved)
    write_data(actors_header)

    for actor in actors:
        actor_id = actor.get('id', 0)
        nb_of_sprite = actor.get('nbOfSprite', 1)
        length = actor.get('len', 0)
        meta = struct.pack('BBH', actor_id, nb_of_sprite, length)
        write_data(meta)

        sprite_data = b'\x01\x02\x03\x04' * (length // 4) # FIXME: Actual sprites
        sprite_data = pad_to_4_bytes(sprite_data)
        write_data(sprite_data)

    # return

def pad_to_4_bytes(data):
    pad_len = (4 - (len(data) % 4)) % 4
    return data + b'\x00' * pad_len

def load_color_palette():
    with open("colormap.text", "r") as f:
        pass



def write_data(*args):
    with open("game.bin", "ab") as f:
        for data in args:
            if isinstance(data, np.ndarray):
                log.info(f"Writing data array: {hex(data[0])} ... {hex(data[-1])} (totals {data.size} elements)")
                f.write(data.tobytes())
            elif isinstance(data, (int, np.integer)):
                value = int(data)
                log.info(f"Writing data as 'Int': {hex(value)}")
                f.write(value.to_bytes((value.bit_length() + 7) // 8 or 1, byteorder='big'))
            elif isinstance(data, bytes):
                log.info(f"Writing data as 'Bytes': {data[:8]}{'...' if len(data) > 8 else ''}")
                f.write(data)
            else:
                log.warning(f"Unknown data type {type(data)}! Attempting to write as bytes.")
                log.info(f"Writing data as raw bytes: {data}")
                # fallback: try to write as bytes
                f.write(bytes(data))


def main():
    # ==================== ARGUMENT PARSING ====================
    global ARGS
    parser = argparse.ArgumentParser(description="compressor/compiler for BMP images")
    parser.add_argument('-c', '--config', type=str, default="gbmp_config.toml", help='Path to TOML config file.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing BMP images.')
    parser.add_argument('-f', '--file', type=str, help='Path to a single BMP image file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()
    ARGS = args

    # ==================== CONFIG LOAD ====================
    global CONFIG
    try:
        CONFIG = toml.load(args.config)
    except Exception as e:
        log.error(f"Failed to load config file: {e}")
        CONFIG = {}

    output_file = CONFIG.get('output_file', 'game.bin')
    verbose = args.verbose or CONFIG.get('verbose', False)
    colormap_path = CONFIG.get('colormap_path', 'colormap.txt')
    version = CONFIG.get('version', 1)
    number_of_actors = CONFIG.get('number_of_actors', 1)
    actor_config = CONFIG.get('actor', {})

    # Clean previous output
    if verbose:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    if os.path.exists(output_file):
        os.remove(output_file)

    log.info(f"Configuration loaded: version={version}, number_of_actors={number_of_actors}, colormap_path={colormap_path}")
    


    if ARGS.directory:
        folderread(ARGS.directory)
    elif ARGS.file:
        imageread(ARGS.file)
    else:
        log.error("Provide either a directory or a file path as arguments.")

    

    print("Processing complete!")


if __name__ == "__main__":
    main()
