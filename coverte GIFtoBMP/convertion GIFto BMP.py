from logging import exception

from PIL import Image, UnidentifiedImageError
import os
import argparse
import math

def gif_to_bmp_auto(gif_path, r, g, b , a, tuile):
    color = (r, g, b, a)
    #  CHARGEMENT DE L'IMAGE GIF (STATIQUE)
    # Conversion en RGBA pour gérer correctement la transparence
    img = Image.open(gif_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # DÉTECTION DE LA COULEUR DE FOND
    # On suppose que le pixel en haut à gauche correspond au fond
    bg_color = pixels[0, 0]

    # Tableau pour marquer les pixels déjà visités (flood fill)
    visited = [[False] * height for _ in range(width)]

    # Liste des bounding boxes des sprites détectés
    sprites = []

    # FONCTIONS UTILITAIRES
    def is_bg(x, y):
        """Retourne True si le pixel (x, y) est du fond"""
        return pixels[x, y] == bg_color

    def flood_fill(x, y):
        """
        Parcours tous les pixels connectés (non-fond)
        à partir du point (x, y) et calcule la bounding box
        du sprite correspondant.
        """
        stack = [(x, y)]
        min_x = max_x = x
        min_y = max_y = y

        while stack:
            cx, cy = stack.pop()

            # Vérification des limites de l'image
            if cx < 0 or cy < 0 or cx >= width or cy >= height:
                continue

            # Ignorer les pixels déjà traités ou du fond
            if visited[cx][cy] or is_bg(cx, cy):
                continue

            # Marquer le pixel comme visité
            visited[cx][cy] = True

            # Mise à jour de la bounding box
            min_x = min(min_x, cx)
            max_x = max(max_x, cx)
            min_y = min(min_y, cy)
            max_y = max(max_y, cy)

            # Ajout des pixels voisins (4-connectivité)
            stack.extend([
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1)
            ])

        # +1 sur max_x / max_y car crop est exclusif
        return min_x, min_y, max_x + 1, max_y + 1

    # DÉTECTION AUTOMATIQUE DES SPRITES
    for x in range(width):
        for y in range(height):
            # Si le pixel n'est pas encore visité et n'est pas du fond,
            # alors on a trouvé un nouveau sprite
            if not visited[x][y] and not is_bg(x, y):
                sprites.append(flood_fill(x, y))

    # CRÉATION DU DOSSIER DE SORTIE
    # Nom de base du fichier GIF (sans extension)
    base_name = os.path.splitext(os.path.basename(gif_path))[0]
    # Dossier contenant le GIF
    gif_dir = os.path.dirname(gif_path)
    # Dossier de sortie à côté du GIF
    output_dir = os.path.join(gif_dir, base_name + "_bmp")
    os.makedirs(output_dir, exist_ok=True)

    # EXTRACTION, AJUSTEMENT MODULO 4 ET SAUVEGARDE BMP
    TILE_SIZE = tuile

    for i, box in enumerate(sprites):
        sprite = img.crop(box)
        sw, sh = sprite.size

        # --- changer le fond ---
        new_sprite = Image.new("RGBA", (sw, sh), color)
        new_sprite.paste(sprite, (0, 0), mask=sprite)
        sprite = new_sprite

        # --- dossier du sprite ---
        sprite_dir = os.path.join(output_dir, f"sprite_{i:03}")
        os.makedirs(sprite_dir, exist_ok=True)

        tiles_x = math.ceil(sw / TILE_SIZE)
        tiles_y = math.ceil(sh / TILE_SIZE)

        tile_index = 0

        for ty in range(tiles_y):
            for tx in range(tiles_x):
                x = tx * TILE_SIZE
                y = ty * TILE_SIZE

                # tuile 16x16 avec fond
                tile = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), color)

                # zone réelle à copier depuis le sprite
                crop_box = (
                    x,
                    y,
                    min(x + TILE_SIZE, sw),
                    min(y + TILE_SIZE, sh)
                )

                part = sprite.crop(crop_box)
                tile.paste(part, (0, 0))

                # BMP = largeur multiple de 4 (16 OK, mais on garde la sécurité)
                tile.save(
                    os.path.join(sprite_dir, f"tile_{tile_index:03}.bmp"),
                    format="BMP"
                )
                tile_index += 1

    print(f"✔️ {len(sprites)} sprites BMP générés (largeur multiple de 4)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--gif", '-gi', help="Path d'image GIF")
    parser.add_argument("--red", '-r', type = int, default=255, help="le rouge de la couleur")
    parser.add_argument("--green", '-g', type = int, default=255, help="le vert de la couleur")
    parser.add_argument("--blue", '-b', type = int, default=255, help="le bleu de la couleur")
    parser.add_argument("--alpha", '-a', type = int, default=255, help="le alpha de la couleur")
    parser.add_argument("--tuile", '-t', type=int, default=16, help="longeur et largeur d'une tuile")
    args = parser.parse_args()
    gif_to_bmp_auto(args.gif,args.red,args.green,args.blue,args.alpha, args.tuile)

    # voici un exemple dans mon cas. path de l'empacement de compialtion , path du gif , couleur rouge , couleur verte , couleur blue , alpha et mesure d'une tuile.
    #python "C:\Users\willi\Desktop\GI-S4-Vert\coverte GIFtoBMP\convertion GIFto BMP.py" --gif "C:\Users\willi\Desktop\1NES - Kung Fu - Miscellaneous - Characters.gif" --red 255 --green 0 --blue 255 --alpha 255 --tuile 16
