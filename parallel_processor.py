"""Module pour traiter les images en parallèle."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Callable
from dataclasses import dataclass


@dataclass
class ImageTagResult:
    """Résultat du tagging d'une image."""
    image_path: Path
    tags: List[str]
    success: bool
    error: str = ""


def process_images_parallel(
    image_paths: List[Path],
    processing_function: Callable[[Path], List[str]],
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] = None
) -> List[ImageTagResult]:
    """
    Traite plusieurs images en parallèle.

    Args:
        image_paths: Liste des chemins d'images à traiter
        processing_function: Fonction qui prend un Path et retourne une liste de tags
        max_workers: Nombre maximum de workers en parallèle
        progress_callback: Fonction optionnelle appelée avec (complété, total) pour la progression

    Returns:
        Liste des résultats de tagging
    """
    results = []
    total = len(image_paths)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumettre toutes les tâches
        future_to_image = {
            executor.submit(processing_function, img_path): img_path
            for img_path in image_paths
        }

        # Collecter les résultats au fur et à mesure
        for future in as_completed(future_to_image):
            image_path = future_to_image[future]
            completed += 1

            try:
                tags = future.result()
                results.append(ImageTagResult(
                    image_path=image_path,
                    tags=tags,
                    success=True
                ))
            except Exception as e:
                results.append(ImageTagResult(
                    image_path=image_path,
                    tags=[],
                    success=False,
                    error=str(e)
                ))

            # Appeler le callback de progression si fourni
            if progress_callback:
                progress_callback(completed, total)

    return results
