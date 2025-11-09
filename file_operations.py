"""Module pour gérer les opérations de fichiers (copie/déplacement)."""

import shutil
import re
from pathlib import Path
from typing import List


def sanitize_filename(name: str) -> str:
    """
    Nettoie un nom de fichier pour le rendre compatible avec les systèmes de fichiers.

    Args:
        name: Nom à nettoyer

    Returns:
        Nom nettoyé
    """
    # Remplacer les caractères interdits par des underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remplacer les espaces multiples par un seul
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Supprimer les espaces au début et à la fin
    sanitized = sanitized.strip()
    # Limiter la longueur (en gardant de la marge pour l'extension)
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def build_new_filename(
    original_path: Path,
    extra_tags: List[str],
    max_tags_in_filename: int = 5
) -> str:
    """
    Construit le nouveau nom de fichier avec les tags.

    Format: {nom_original}_{tag1}_{tag2}_{tag3}.{ext}

    Args:
        original_path: Chemin original du fichier
        extra_tags: Tags supplémentaires (sans le premier qui est la catégorie)
        max_tags_in_filename: Nombre maximum de tags à inclure dans le nom

    Returns:
        Nouveau nom de fichier
    """
    original_name = original_path.stem
    extension = original_path.suffix

    # Limiter le nombre de tags dans le nom de fichier
    tags_to_use = extra_tags[:max_tags_in_filename]

    # Nettoyer et joindre les tags
    cleaned_tags = [sanitize_filename(tag) for tag in tags_to_use]

    if cleaned_tags:
        new_name = f"{original_name}_{'_'.join(cleaned_tags)}{extension}"
    else:
        new_name = f"{original_name}{extension}"

    return sanitize_filename(new_name)


def organize_image(
    source_path: Path,
    first_tag: str,
    extra_tags: List[str],
    output_dir: str,
    move: bool = False
) -> Path:
    """
    Organise une image dans la structure de répertoires.

    Structure: {output_dir}/{first_tag}/{nom_original}_{tags_extra}.{ext}

    Args:
        source_path: Chemin source de l'image
        first_tag: Premier tag (utilisé comme nom de dossier)
        extra_tags: Tags supplémentaires (ajoutés au nom de fichier)
        output_dir: Répertoire de sortie
        move: Si True, déplace le fichier, sinon le copie

    Returns:
        Chemin du fichier de destination
    """
    # Créer le répertoire de catégorie
    category_dir = Path(output_dir) / sanitize_filename(first_tag)
    category_dir.mkdir(parents=True, exist_ok=True)

    # Construire le nouveau nom de fichier
    new_filename = build_new_filename(source_path, extra_tags)

    # Chemin de destination
    dest_path = category_dir / new_filename

    # Gérer les conflits de noms
    if dest_path.exists():
        counter = 1
        stem = dest_path.stem
        suffix = dest_path.suffix
        while dest_path.exists():
            new_name = f"{stem}_{counter}{suffix}"
            dest_path = category_dir / new_name
            counter += 1

    # Copier ou déplacer le fichier
    if move:
        shutil.move(str(source_path), str(dest_path))
    else:
        shutil.copy2(str(source_path), str(dest_path))

    return dest_path
