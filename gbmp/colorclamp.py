# ======================== ATTENTION!!! ========================
# This is a very WIP file which WILL be edited as time goes on
# Comments may or may not be out of date.

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
COLOUR_PALETTE = None
OUTPUT_DIR = './clamped'

def load_palette(colour):
    global COLOUR_PALETTE

    colormap_path = CONFIG.get('colormap_path', 'colormap.txt')
    try:
        with open(colormap_path, 'r') as f:
            COLOUR_PALETTE = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    for hex_code in line.split(','):
                        hex_code = hex_code.strip()
                        if hex_code:
                            rgb_val = int(hex_code, 16)
                            r = (rgb_val >> 16) & 0xFF
                            g = (rgb_val >> 8) & 0xFF
                            b = rgb_val & 0xFF
                            log.info(f"Loaded color code: {rgb_val:08X}")
                            COLOUR_PALETTE.append((r, g, b))
            log.info(f"Loaded color palette with {len(COLOUR_PALETTE)} entries from {colormap_path}")
    except Exception as e:
        log.error(f"Failed to load color palette: {e}")
        COLOUR_PALETTE = []

    return COLOUR_PALETTE

def color_distance_to_palette(color, palette):
    min_dist = None
    closest = None
    for p in palette:
        dist = color_distance(color, p)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            closest = p
    return closest

def color_distance(c1, c2):
    return sum((int(a) - int(b)) ** 2 for a, b in zip(c1, c2))

def clamp_color(color):
    if COLOUR_PALETTE is None:
        load_palette(None)

    if not COLOUR_PALETTE:
        log.warning("Color palette is empty. Returning original color.")
        return color

    return color_distance_to_palette(color, COLOUR_PALETTE)

def clamp_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        log.error(f"Image at path {image_path} could not be read.")
        raise FileNotFoundError

    height, width, channels = img.shape
    log.info(f"Processing image of size {width}x{height} with {channels} channels.")

    for y in range(height):
        for x in range(width):
            b, g, r = img[y, x]
            original_color = (r, g, b)
            clamped_color = clamp_color(original_color)
            img[y, x] = (clamped_color[2], clamped_color[1], clamped_color[0])

    return img

def process_directory(directory_path, root_path=None):
    if root_path is None:
        root_path = directory_path
    
    rel_path = os.path.relpath(directory_path, start=root_path)
    if rel_path == ".":
        output_dir = OUTPUT_DIR
    else:
        output_dir = os.path.join(OUTPUT_DIR, rel_path)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        log.info(f"Created output directory: {output_dir}")
    else:
        log.info(f"Cleaning output directory: {output_dir}")
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    for filename in os.listdir(directory_path):
        full_path = os.path.join(directory_path, filename)
        if os.path.isdir(full_path):
            process_directory(full_path, root_path)
        elif filename.lower().endswith('.bmp'):
            log.info(f"Processing image: {full_path}")
            processed_image = clamp_image(full_path)
            output_path = os.path.join(output_dir, filename)
            log.info(f"Attempting to write image to: {output_path}")
            result = cv2.imwrite(output_path, processed_image)
            if result:
                log.info(f"Saved clamped image to: {output_path}")
            else:
                log.error(f"Failed to write image to: {output_path}")
        else:
            log.info(f"Skipping non-BMP file: {filename}")

def process_file(file_path):
    log.info(f"Processing single image: {file_path}")
    processed_image = clamp_image(file_path)
    output_path = os.path.join(os.path.dirname(file_path), f"clamped_{os.path.basename(file_path)}")
    cv2.imwrite(output_path, processed_image)
    log.info(f"Saved clamped image to: {output_path}")


def main():
    global ARGS, OUTPUT_DIR
    parser = argparse.ArgumentParser(description="image clamper")
    parser.add_argument('-c', '--config', type=str, default="gbmp_config.toml", help='Path to TOML config file.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing BMP images.')
    parser.add_argument('-f', '--file', type=str, help='Path to a single BMP image file.')
    parser.add_argument('-o', '--output', type=str, default='./clamped', help='Output directory for clamped images.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()
    ARGS = args
    OUTPUT_DIR = args.output

    global CONFIG
    try:
        CONFIG = toml.load(args.config)
    except Exception as e:
        log.error(f"Failed to load config file: {e}")
        CONFIG = {}

    colormap_path = CONFIG.get('colormap_path', 'colormap.txt')
    verbose = args.verbose or CONFIG.get('verbose', False)


    if verbose:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)

    log.info(f"Configuration loaded: colormap_path={colormap_path}")

    if ARGS.directory:
        process_directory(ARGS.directory)
    elif ARGS.file:
        process_file(ARGS.file)
    else:
        log.error("Provide either a directory or a file path as arguments.")

    log.info(f"Color palette used: {COLOUR_PALETTE}")
    log.info("Processing completed.")


if __name__ == "__main__":
    main()