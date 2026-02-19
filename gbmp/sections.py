# ======================== ATTENTION!!! ========================
# This is a very WIP file which WILL be edited as time goes on
# Comments may or may not be out of date.

import os
import struct
import logging as log
import cv2
import numpy as np

TILE_SIZE = 16

def _pad4(data: bytes) -> bytes:
    remainder = len(data) % 4
    if remainder:
        data += b'\x00' * (4 - remainder)
    return data


def _read_bmp(path: str) -> np.ndarray | None:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        log.error(f"Cannot read BMP: {path}")
    return img


def _build_lookup(palette: list[int]) -> dict[int, int]:
    if len(palette) == 16:
        mask_rgb = palette[0]
        colors   = palette[1:16]
    else:
        mask_rgb = 0x000000
        colors   = palette[:15]

    lookup: dict[int, int] = {mask_rgb: 0} 
    for idx, rgb in enumerate(colors):
        lookup[rgb] = idx + 1
    return lookup


def _pixels_to_bytes(img: np.ndarray, palette: list[int]) -> bytes:
    lookup = _build_lookup(palette)
    h, w, _ = img.shape
    out = bytearray()
    for y in range(h):
        for x in range(w):
            b, g, r = img[y, x]
            rgb = int((int(r) << 16) | (int(g) << 8) | int(b))
            idx = lookup.get(rgb)
            if idx is None:
                log.warning(f"Color #{rgb:06X} at ({x},{y}) not in palette; mapping to 0")
                out.append(0)
            else:
                out.append(idx)
    return bytes(out)


def _sorted_bmps(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith('.bmp')
    )


def _sorted_subdirs(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        return []
    return sorted(
        os.path.join(directory, d)
        for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d))
    )


def load_palette(colormap_path: str) -> list[int]:
    """
    Color 0 is the mask
    rest are palette entries (16 and up are ignored)
    """
    palette: list[int] = []
    try:
        with open(colormap_path, 'r') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                for token in line.split(','):
                    token = token.strip()
                    if token:
                        palette.append(int(token, 16))
    except Exception as exc:
        log.error(f"Failed to load colormap '{colormap_path}': {exc}")

    if len(palette) > 16:
        log.warning(f"Colormap has {len(palette)} entries; only the first 16 will be used.")
        palette = palette[:16]

    log.info(f"Palette loaded: {len(palette)} entries from '{colormap_path}' "
             f"(slot 0 = colorMask, slots 1-{min(len(palette)-1, 15)} = colours)")
    return palette


FILE_METADATA_OFFSET = 0
FILE_LEN_FIELD_OFFSET = 4 


def write_file_metadata(writer, config: dict) -> None:
    """
    file_len is 0 bc it depends on the total size of the file...
    Need to call a aatcher to fix the value once the rest is written?
    """
    version       = config.get('version', 1) & 0xFF
    control_flags = config.get('controlFlags', 0) & 0xFF
    reserved      = 0x0000
    file_len      = 0  # placeholder – patched later
    data = struct.pack('<BBHI', version, control_flags, reserved, file_len)
    log.info(f"FileMetaData: version={version:#04x} controlFlags={control_flags:#04x} fileLen=<TBD>")
    writer.write(data)


def patch_file_len(writer) -> None:
    total = writer.tell()
    writer.seek(FILE_METADATA_OFFSET + FILE_LEN_FIELD_OFFSET)
    writer.write(struct.pack('<I', total))
    writer.seek(0, 2)  # back to end
    log.info(f"Patched fileLen = {total} bytes ({total:#010x})")


def _pack_color(color_id: int, rgb: int) -> bytes:
    r = (rgb >> 16) & 0xFF
    g = (rgb >>  8) & 0xFF
    b =  rgb        & 0xFF
    word = (int(b) << 24) | (int(g) << 16) | (int(r) << 8) | (int(color_id) & 0xFF)
    return struct.pack('<I', word)


def write_color_register(writer, palette: list[int]) -> None:
    """
    """
    log.info("ColorRegister:")
    if len(palette) == 16:
        mask_rgb  = palette[0]
        colors    = palette[1:16]
    else:
        mask_rgb  = 0x000000
        colors    = palette[:15]

    # colour mask
    writer.write(_pack_color(0, mask_rgb))
    log.info(f"  [0] mask #{mask_rgb:06X}")

    # slots 1-15 =. palette colours
    for i, rgb in enumerate(colors):
        slot = i + 1
        writer.write(_pack_color(slot, rgb))
        log.info(f"  [{slot}] #{rgb:06X}")

    # if <16, fill w zeros
    for slot in range(len(colors) + 1, 16):
        writer.write(_pack_color(0, 0))

    log.info(f"ColorRegister written (64 bytes, {len(colors)} colours + mask)")



def write_actors_header(writer, actor_config: dict, life_bar: int) -> None:
    actors        = actor_config.get('actors', [])
    nb_of_actors  = len(actors) & 0xFF
    player_id     = actor_config.get('player_actor_id', actors[0].get('id', 0) if actors else 0) & 0xFF
    reserved      = 0xFF
    data = struct.pack('<BBBB', nb_of_actors, player_id, life_bar & 0xFF, reserved)
    log.info(f"ActorsHeader: nbOfActors={nb_of_actors} playerActorId={player_id} lifeBar={life_bar}")
    writer.write(data)



def _sprite_pixel_data(sprite_dir: str, palette: list[int], tile_size: int) -> tuple[bytes, int, int]:
    """
    """
    bmps = _sorted_bmps(sprite_dir)
    if not bmps:
        log.warning(f"Sprite directory has no BMP files: {sprite_dir}")
        return b'', 0, 0

    raw = bytearray()
    valid = 0
    for bmp_path in bmps:
        img = _read_bmp(bmp_path)
        if img is None:
            continue
        raw += _pixels_to_bytes(img, palette)
        valid += 1

    # Deducte gird dimensions from tile count
    n = valid
    side = int(n ** 0.5)
    if side * side == n:
        w, h = side, side
    else:
        w, h = n, 1

    return bytes(raw), w, h


def write_actor_section(writer, actor: dict, sprite_dirs: list[str], palette: list[int], tile_size: int) -> None:
    """
    """
    actor_id    = actor.get('id', 0) & 0xFF
    nb_sprites  = len(sprite_dirs) & 0xFF

    sprite_blocks: list[bytes] = []
    for sdir in sprite_dirs:
        px, tw, th = _sprite_pixel_data(sdir, palette, tile_size)
        nb_tiles   = tw * th
        tile_meta  = struct.pack('<BBBB', tw & 0xFF, th & 0xFF, nb_tiles & 0xFF, 0xFF)
        payload    = _pad4(tile_meta + px)
        sprite_blocks.append(payload)
        log.info(f"  Sprite '{os.path.basename(sdir)}': {tw}x{th} tiles, "
                 f"{len(px)} px bytes --> {len(payload)} bytes (padded)")

    total_len = sum(len(b) for b in sprite_blocks)

    meta = struct.pack('<BBH', actor_id, nb_sprites, total_len & 0xFFFF)
    log.info(f"ActorMetaData: id={actor_id} nbOfSprite={nb_sprites} len={total_len}")
    writer.write(meta)

    for block in sprite_blocks:
        writer.write(block)


def write_all_actors(writer, actor_config: dict, root_path: str, palette: list[int], tile_size: int) -> None:
    actors_path = os.path.join(root_path, actor_config.get('path', 'clamped/actors/'))
    all_sprite_dirs = _sorted_subdirs(actors_path)
    log.info(f"Actor sprites root: {actors_path}  ({len(all_sprite_dirs)} sprite dirs found)")

    offset = 0
    for actor in actor_config.get('actors', []):
        count = actor.get('sprite_count', actor.get('nbOfSprite', 1))
        assigned = all_sprite_dirs[offset: offset + count]
        if len(assigned) < count:
            log.warning(f"Actor '{actor.get('name', actor['id'])}': requested {count} sprites "
                        f"but only {len(assigned)} dirs available.")
        log.info(f"Actor '{actor.get('name', actor.get('id'))}' (id={actor['id']}): "
                 f"{len(assigned)} sprites --> {[os.path.basename(d) for d in assigned]}")
        write_actor_section(writer, actor, assigned, palette, tile_size)
        offset += count


#   #w
def write_world_tiles_header(writer, nb_tiles: int, total_data_len: int) -> None:
    data = struct.pack('<HH', nb_tiles & 0xFFFF, total_data_len & 0xFFFF)
    log.info(f"WorldTilesHeader: nbOfTiles={nb_tiles} len={total_data_len}")
    writer.write(data)



def _world_tile_pixel_data(tile_dir: str, palette: list[int]) -> bytes:
    bmps = _sorted_bmps(tile_dir)
    if not bmps:
        log.warning(f"World tile directory has no BMP files: {tile_dir}")
        return b''
    img = _read_bmp(bmps[0])
    if img is None:
        return b''
    return _pixels_to_bytes(img, palette)


def write_world_tile(writer, tile_cfg: dict, tile_dir: str, palette: list[int]) -> int:
    """
    Write WorldTileMetaData + pixel data for one tile type3
    """
    tile_id   = tile_cfg.get('id', 0) & 0xFF
    collision = tile_cfg.get('collision', 0) & 0x1
    event     = tile_cfg.get('event',     0) & 0x1
    ttype     = tile_cfg.get('tile_type', 0) & 0x3
    reserved  = 0xF & 0xF
    flags     = (collision << 7) | (event << 6) | (ttype << 4) | reserved

    px      = _world_tile_pixel_data(tile_dir, palette)
    payload = _pad4(px)
    meta    = struct.pack('<BBH', tile_id, flags, len(payload) & 0xFFFF)
    log.info(f"WorldTileMetaData: id={tile_id} collision={collision} event={event} "
             f"type={ttype} len={len(payload)}")
    writer.write(meta)
    writer.write(payload)
    return 4 + len(payload)


def write_all_world_tiles(writer, world_config: dict, root_path: str, palette: list[int]) -> None:
    world_path  = os.path.join(root_path, world_config.get('path', 'clamped/worlds/'))
    tile_cfgs   = world_config.get('tilesid', [])
    tile_dirs   = _sorted_subdirs(world_path)

    log.info(f"World tiles root: {world_path}  ({len(tile_dirs)} tile dirs found)")

    if len(tile_dirs) < len(tile_cfgs):
        log.warning(f"Config defines {len(tile_cfgs)} tile types but only "
                    f"{len(tile_dirs)} directories were found.")

    pairs = list(zip(tile_cfgs, tile_dirs))
    nb_tiles = len(pairs)

    # placeholder write of the header; needs t be patched later
    header_pos = writer.tell()
    write_world_tiles_header(writer, nb_tiles, 0)  # len patched below

    total_tile_bytes = 0
    for tile_cfg, tile_dir in pairs:
        log.info(f"Tile dir '{os.path.basename(tile_dir)}' --> id={tile_cfg.get('id')}")
        total_tile_bytes += write_world_tile(writer, tile_cfg, tile_dir, palette)

    # patch WorldTilesHeader.len
    end_pos = writer.tell()
    writer.seek(header_pos)
    write_world_tiles_header(writer, nb_tiles, total_tile_bytes)
    writer.seek(end_pos)
    log.info(f"WorldTilesHeader patched: nbOfTiles={nb_tiles} len={total_tile_bytes}")



def write_world_metadata(writer, world_config: dict, root_path: str, palette: list[int]) -> None:
    world_id   = world_config.get('id',               0) & 0xFF
    ctrl_flag  = world_config.get('controlFlag',       0) & 0xFF
    bg_color   = world_config.get('backgroundColor',   0) & 0xFF
    reserved   = 0xFF

    # ---- load world map ----
    map_file = world_config.get('map_file', None)
    if map_file:
        map_path = os.path.join(root_path, map_file)
        try:
            with open(map_path, 'rb') as fh:
                raw_map = fh.read()
            log.info(f"World map loaded from '{map_path}': {len(raw_map)} bytes")
        except Exception as exc:
            log.warning(f"Could not load world map '{map_path}': {exc} – using empty map.")
            raw_map = b''
    else:
        log.warning("No 'map_file' in [world] config – writing empty world map.")
        raw_map = b''

    map_data = _pad4(raw_map)
    meta = struct.pack('<BBBBI', world_id, ctrl_flag, bg_color, reserved, len(map_data))
    log.info(f"WorldMetaData: id={world_id} controlFlag={ctrl_flag} "
             f"backgroundColor={bg_color} len={len(map_data)}")
    writer.write(meta)
    writer.write(map_data)
