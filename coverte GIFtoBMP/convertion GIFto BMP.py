from logging import exception

from PIL import Image, UnidentifiedImageError
import os
import argparse

def gif_to_bmp_auto(gif_path):
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
    for i, box in enumerate(sprites):
        # Découpage du sprite
        sprite = img.crop(box)
        sw, sh = sprite.size

        # --- Forçage de la largeur multiple de 4 ---
        # Calcul du plus petit multiple de 4 supérieur ou égal
        new_width = (sw + 3) // 4 * 4

        if new_width != sw:
            # Création d'une nouvelle image avec padding transparent
            padded = Image.new("RGBA", (new_width, sh), (0, 0, 0, 0))
            padded.paste(sprite, (0, 0))
            sprite = padded
        #remplacer le fond par la couleur qu'on veut'
        # Couleur de fond à remplacer (magenta)
        old_bg = (255, 0, 255, 255)  # RGBA

        # Nouvelle couleur de fond
        new_bg = (255,255,128,255)

        # Remplacement pixel par pixel
        pixels_sprite = sprite.load()
        for x in range(sprite.width):
            for y in range(sprite.height):
                if pixels_sprite[x, y] == old_bg:
                    pixels_sprite[x, y] = new_bg
        # Sauvegarde en BMP
        sprite.save(
            os.path.join(output_dir, f"sprite_{i:03}.bmp"),
            format="BMP"
        )

    print(f"✔️ {len(sprites)} sprites BMP générés (largeur multiple de 4)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--gif", '-g', help="Path d'image GIF")
    #parser.add_argument("--bmp", '-b', help="Path d'image BMP")
    args = parser.parse_args()
    gif_to_bmp_auto(args.gif)