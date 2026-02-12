# ======================== ATTENTION!!! ========================
# This is a very WIP file which WILL be edited as time goes on
# Comments may or may not be out of date.

## 

import argparse
import numpy as np 
import cv2
import logging as log
import os
import toml
import struct

import colorclamp

CONFIG = {}
ARGS = {}
IMAGE = None


def dirread(path):
    """_summary_

    Args:
        path (_type_): _description_
    """

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isdir(full_path):
            log.info(f"Entering directory: {full_path}")
            dirread(full_path)
        elif filename.lower().endswith('.bmp'):
            log.info(f"Reading image: {full_path}")
            imageread(full_path)
        else:
            log.info(f"Skipping non-BMP file: {filename}")

def dirinfo(path):
    
    files = []
    dirs = []
    tilesize = CONFIG.get('tilesize', 16)
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isdir(full_path):
            dirs.append(full_path)
            dirinfo(full_path)
        elif filename.lower().endswith('.bmp'):
            files.append(full_path)
    log.info(f"Directory {path} contains {len(files)} BMP files and {len(dirs)} subdirectories.")
    return files, dirs, tilesize



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

    # process_header()
    # process_color_register()
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

    file_version = CONFIG.get('version', 1)
    control_flags = 0
    reserved = 0xFFFF
    file_len = 0x3
    headings = struct.pack('<BBHI', file_version, control_flags, reserved, file_len)
    write_data(headings)

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
    color_mask = 0  # FIXME: define color mask properly (not 0!!!)
    height, width, channels = IMAGE.shape
    unique_rgbs = set()
    colors = []
    colormap_path = CONFIG.get('colormap_path', None)
    if colormap_path is not None and os.path.exists(colormap_path):
        log.info(f"Loading color palette from {colormap_path}")
        with open(colormap_path, "r") as f:
            i = 0
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    for hex_code in line.split(','):
                        hex_code = hex_code.strip()
                        if hex_code:
                            try:
                                rgb_val = int(hex_code, 16)
                                color_id = i
                                color_code = (color_id << 24) | rgb_val
                                colors.append(color_code)
                                log.info(f"Loaded color code: {color_code:08X}")
                                i += 1
                            except ValueError:
                                log.warning(f"Invalid color code in colormap: {hex_code}")
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
                    color_id = len(colors) + 1
                    color_code = (color_id << 24) | (r << 16) | (g << 8) | b
                    colors.append(color_code)
                    log.info(f"Added color code: {color_code:08X} (R={r}, G={g}, B={b})")
    packed_colors = struct.pack('<I', color_mask)
    for color in colors:
        packed_colors += struct.pack('<I', color)
    while len(colors) < 15:
        packed_colors += struct.pack('<I', 0)
        colors.append(0)
    write_data(packed_colors)
    # return color_mask, colors

    
def process_actor_header():
#     typedef struct {
#         uint32_t nbOfActors:8;
#         uint32_t playerActorId:8;
#         uint32_t lifeBar:8;
#         uint32_t reserved:8;
# } FrameActorsHeader;

# typedef union {
#     FrameActorsHeader frame;
#     uint8_t byteMap[sizeof(FrameActorsHeader)];
# } ActorsHeader;
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

def process_word_header():
# /**
#  * World header to get an id and control flags. 
#  */
# typedef struct {
#         uint8_t id;
#         uint8_t controlFlag;
#         uint8_t backgroundColor;
#         uint8_t nbOfTiles;
#         uint32_t len;
# } FrameWorldMetadata;

# typedef union {
#     FrameWorldMetadata frame;
#     uint8_t byteMap[sizeof(FrameWorldMetadata)];
# } WorldMetaData;
    log.info("========== Processing world header ==========")

    files, dirs, tilesize = dirinfo(ARGS.directory) if ARGS.directory else ([], [])

    world_id = np.uint8(0)
    control_flag = np.uint8(0)
    background_color = np.uint8(0)
    nb_of_tiles = np.uint8(len(files) % 256)                    # FIXME: Cant handle more than 255 tiles. Fix necessary?
    length = np.uint32((tilesize ** 2 * len(files) % 2**32))    # FIXME: Cant handle more than ~4GB of data. Fix necessary?
    world_header = struct.pack('BBBBI', world_id, control_flag, background_color, nb_of_tiles, length)
    write_data(world_header)


def process_word_tile_metadata():
#     /**
#  * This metadata needs to directly follow the WorldMetaData times the nbOfTiles.
#  */
# typedef struct {
#         uint8_t id;
#         uint8_t collision:1;
#         uint8_t event:1;
#         uint8_t type:2;
#         uint8_t reserved:4;
#         uint16_t len;
# } FrameWorldTileMetaData;

# typedef union {
#     FrameWorldTileMetaData frame;
#     uint8_t byteMap[sizeof(FrameWorldTileMetaData)];
# } WorldTileMetaData;
    log.info("========== Processing world tile metadata ==========")
    tile_id = np.uint8(0)
    collision = np.uint8(0)
    event = np.uint8(0)
    tile_type = np.uint8(0)
    reserved = np.uint8(0xF)
    length = np.uint16(0)
    tile_metadata = struct.pack('BBH', tile_id, (collision << 7) | (event << 6) | (tile_type << 4) | reserved, length)
    write_data(tile_metadata)

def process_data():
    if ARGS.directory:
        dirread(ARGS.directory)
    elif ARGS.file:
        imageread(ARGS.file)
    
    process_header()
    process_color_register()
    process_actor_header()
    process_word_header()
    process_word_tile_metadata()

    print("Processing complete!")


def pad_to_4_bytes(data):
    pad_len = (4 - (len(data) % 4)) % 4
    return data + b'\x00' * pad_len


def write_data(*args):
    with open("game.bin", "ab") as f:
        for data in args:
            if isinstance(data, bytes):
                log.info(f"Writing data as 'Bytes': {data[:8]}{'...' if len(data) > 8 else ''}")
                f.write(data)
            elif isinstance(data, (int, np.integer)):
                value = int(data)
                log.info(f"Writing data as 'Int': {hex(value)}")
                f.write(struct.pack('<I', value))
            elif isinstance(data, list):
                log.info(f"Writing data as 'List': {data}")
                for item in data:
                    f.write(struct.pack('<I', item))
            else:
                log.warning(f"Unknown data type {type(data)}! Attempting to write as bytes.")
                log.info(f"Writing data as raw bytes: {data}")
                f.write(bytes(data))


def main():
    # ==================== ARGUMENT PARSING ====================
    global ARGS
    parser = argparse.ArgumentParser(description="compressor/compiler for BMP images")
    parser.add_argument('-c', '--config', type=str, default="gbmp_config.toml", help='Path to TOML config file.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing BMP images.')
    parser.add_argument('-f', '--file', type=str, help='Path to a single BMP image file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    parser.add_argument('-nc', '--no-color-clamp', action='store_true', help='Disable color clamping')
    parser.add_argument('-cc', '--color-clamp', action='store_true', help='Only perform color clamping without generating binarty')
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
    
    process_data()

if __name__ == "__main__":
    main()
