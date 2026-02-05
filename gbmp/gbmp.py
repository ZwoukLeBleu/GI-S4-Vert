import argparse
import numpy as np 
import cv2
import logging as log

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
    height, width, channels = img.shape
    for y in range(height):
        for x in range(width):
            b, g, r = img[y, x]
            log.info(f"Pixel at ({x}, {y}): Blue={b}, Green={g}, Red={r}")

    process_color_register(img)
    return img

def process_header():
# typedef struct {
#         uint32_t fileVersion : 8;
#         uint32_t controlFlags : 8;
#         uint32_t reserved : 16;
#         uint32_t fileLen;
# } FrameFileMetaData;
    file_version = np.uint8(0)
    control_flags = np.uint8(0)
    reserved = np.uint16(0)
    headings = np.uint32(file_version) << 24 | np.uint32(control_flags) << 16 | np.uint32(reserved)
    file_len = np.uint32(0)

    return headings, file_len
    
def process_color_register(img: np.ndarray):
    """_summary_

    Args:
        img (np.ndarray): _description_
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


#     typedef union {
#     struct {
#         Color colorMask;
#         Color colors[15];
#     }frame;

#     uint8_t byteMap[sizeof(Color) * 16];
# } ColorRegiste

    height, width, channels = img.shape
    color_mask = np.uint32(0)                   # FIXME: define color mask properly (not 0!!!)
    colors = np.array([], dtype=np.uint32)

    for y in range(height):                     # NOTE:  This loop should only be used if there is no color palette!
        for x in range(width):
            b, g, r = img[y, x]
            color_id = np.uint8(len(colors) + 1)
            color_code = (np.uint32(color_id) << 24) | (np.uint32(r) << 16) | (np.uint32(g) << 8) | np.uint32(b)
            if color_code not in colors and len(colors) < 15:
                colors = np.append(colors, color_code)
            
            log.info(f"Color ID={color_id}, Code={color_code:08X}")

    return color_mask, colors
    
def process_actors():
    """_summary_
    """
# typedef struct {
#         uint32_t nbOfActors:8;
#         uint32_t playerActorId:8;
#         uint32_t reserved:16;
# } FrameActorsHeader;

# typedef union {
#     FrameActorsHeader frame;
#     uint8_t byteMap[sizeof(FrameActorsHeader)];
# } ActorsHeader;

# /**
#  * Actor header to indicate at the console the number of sprite and its id. The console directly assign the sprite selection based on the sequence (sprite 0 = id 0 for actor id [actor_id.sprite_id])
#  */
# typedef struct {
#         uint8_t id;
#         uint8_t nbOfSprite;
#         uint16_t len; 
# } FrameActorMetaData;
#  typedef union {
#     FrameActorMetaData frame;
#     uint8_t byteMap[sizeof(FrameActorMetaData)];
# } ActorMetaData;





def main():
    parser = argparse.ArgumentParser(description="compressor/compiler for BMP images")
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory containing BMP images.')
    parser.add_argument('-f', '--file', type=str, help='Path to a single BMP image file.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()
    
    if args.verbose:
        log.basicConfig(level=log.INFO)

    if args.directory:
        folderread(args.directory)
    elif args.file:
        imageread(args.file)
    else:
        log.error("Provide either a directory or a file path as arguments.")



if __name__ == "__main__":
    main()