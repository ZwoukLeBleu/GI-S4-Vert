import argparse
import logging as log
import os
import time
import toml

import sections

class _FileWriter:
    def __init__(self, path: str):
        self._fh = open(path, 'wb')

    def write(self, data: bytes) -> None:
        self._fh.write(data)

    def seek(self, *args):
        self._fh.seek(*args)

    def tell(self) -> int:
        return self._fh.tell()

    def close(self):
        self._fh.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ---------------------------------------------------------------------------
# Compilation pipeline
# ---------------------------------------------------------------------------

def compile_binary(config: dict, root_path: str, verbose: bool) -> None:
    output_file   = config.get('output_file',   'game.bin')
    colormap_path = os.path.join(root_path, config.get('colormap_path', 'colormap.txt'))
    tile_size     = config.get('tilesize', 16)
    life_bar      = config.get('life_bar',  1)
    actor_config  = config.get('actor',    {})
    world_config  = config.get('world',    {})

    output_path = os.path.join(root_path, output_file)

    palette = sections.load_palette(colormap_path)
    if not palette:
        log.error("Empty palette - aborting.")
        return

    log.info(f"Output: {output_path}")
    log.info(f"Tile size: {tile_size}x{tile_size}")

    with _FileWriter(output_path) as writer:
        # FileMetaData
        log.info("=== FileMetaData ===")
        sections.write_file_metadata(writer, config)

        # ColorRegister
        log.info("=== ColorRegister ===")
        sections.write_color_register(writer, palette)

        # ActorsHeader
        log.info("=== ActorsHeader ===")
        sections.write_actors_header(writer, actor_config, life_bar)

        # For each A, write ActorMetaData + sprites
        log.info("=== Actor sections ===")
        sections.write_all_actors(writer, actor_config, root_path, palette, tile_size)

        # WorldTilesHeader, for each W, write world tile sections
        log.info("=== World tile sections ===")
        sections.write_all_world_tiles(writer, world_config, root_path, palette)

        # WorldMetaData + world map
        log.info("=== WorldMetaData ===")
        sections.write_world_metadata(writer, world_config, root_path, palette)

        # Patch FileMetaData.fileLen
        sections.patch_file_len(writer)

    file_size = os.path.getsize(output_path)
    print(f"Output: {output_path}  ({file_size} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="GBMP"
    )
    parser.add_argument(
        '-c', '--config',
        default="gbmp_config.toml",
        help='Path to the TOML config file (default: gbmp_config.toml).'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging.'
    )
    args = parser.parse_args()

    config: dict = {}
    try:
        config = toml.load(args.config)
    except Exception as exc:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)
        log.error(f"Failed to load config '{args.config}': {exc}")
        return

    verbose = args.verbose or config.get('verbose', False)
    if verbose:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    else:
        log.basicConfig(format='%(levelname)s: %(message)s', level=log.WARNING)

    root_path = os.path.dirname(os.path.abspath(args.config))

    start = time.time()
    compile_binary(config, root_path, verbose)
    print(f"Done in {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
