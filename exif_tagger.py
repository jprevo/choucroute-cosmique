"""Module pour ajouter des tags EXIF/IPTC aux images."""

from pathlib import Path
from typing import List

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    import piexif
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False


def add_tags_to_image(image_path: Path, tags: List[str]) -> bool:
    """
    Ajoute des tags à l'image via les métadonnées EXIF/IPTC.

    Args:
        image_path: Chemin vers l'image
        tags: Liste de tags à ajouter

    Returns:
        True si succès, False sinon
    """
    if not EXIF_AVAILABLE:
        print("Avertissement: PIL/Pillow et piexif ne sont pas installés. Les tags EXIF ne seront pas ajoutés.")
        return False

    try:
        # Ouvrir l'image
        img = Image.open(image_path)

        # Préparer les tags pour EXIF
        # Les tags sont stockés dans le champ "ImageDescription" et "XPKeywords"
        tags_string = "; ".join(tags)

        # Charger ou créer les données EXIF
        try:
            exif_dict = piexif.load(str(image_path))
        except Exception:
            # Si pas d'EXIF existant, créer un nouveau dictionnaire
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

        # Ajouter les tags dans ImageDescription (0x010e)
        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = tags_string.encode('utf-8')

        # Ajouter également dans XPKeywords (0x9c9e) pour Windows
        # XPKeywords attend du UTF-16
        exif_dict["0th"][0x9c9e] = tags_string.encode('utf-16le') + b'\x00\x00'

        # Encoder les données EXIF
        exif_bytes = piexif.dump(exif_dict)

        # Sauvegarder l'image avec les nouvelles données EXIF
        img.save(str(image_path), exif=exif_bytes)

        return True

    except Exception as e:
        print(f"Erreur lors de l'ajout des tags EXIF à {image_path}: {e}")
        return False


def read_tags_from_image(image_path: Path) -> List[str]:
    """
    Lit les tags d'une image.

    Args:
        image_path: Chemin vers l'image

    Returns:
        Liste des tags trouvés
    """
    if not EXIF_AVAILABLE:
        return []

    try:
        exif_dict = piexif.load(str(image_path))

        tags = []

        # Lire ImageDescription
        if piexif.ImageIFD.ImageDescription in exif_dict.get("0th", {}):
            desc = exif_dict["0th"][piexif.ImageIFD.ImageDescription]
            if isinstance(desc, bytes):
                desc = desc.decode('utf-8', errors='ignore')
            tags.extend([tag.strip() for tag in desc.split(';') if tag.strip()])

        return tags

    except Exception as e:
        print(f"Erreur lors de la lecture des tags EXIF de {image_path}: {e}")
        return []
