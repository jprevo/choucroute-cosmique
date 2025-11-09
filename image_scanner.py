"""Module pour scanner et trouver les fichiers images dans un répertoire."""

from pathlib import Path
from typing import List

# Extensions d'images supportées
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}


def scan_images(directory: str) -> List[Path]:
    """
    Scanne un répertoire et retourne tous les fichiers images.

    Args:
        directory: Chemin du répertoire à scanner

    Returns:
        Liste des chemins Path vers les fichiers images trouvés
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Le répertoire {directory} n'existe pas")

    if not dir_path.is_dir():
        raise NotADirectoryError(f"{directory} n'est pas un répertoire")

    images = []
    for file_path in dir_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file_path)

    return sorted(images)
