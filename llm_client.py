"""Module pour interagir avec le LLM et parser les résultats."""

import re
from pathlib import Path
from typing import List, Tuple
from ollama import chat, ChatResponse


def generate_tags(
    image_path: Path,
    model: str,
    tag_count: int,
    available_tags: str
) -> List[str]:
    """
    Génère des tags pour une image en utilisant le LLM.

    Args:
        image_path: Chemin vers l'image
        model: Nom du modèle LLM à utiliser
        tag_count: Nombre de tags à générer
        available_tags: Tags disponibles pour le premier tag (séparés par virgules)

    Returns:
        Liste des tags générés et nettoyés
    """
    prompt = (
        f'Écrit {tag_count} mots-clés en français décrivant cette image, séparés par une virgule, '
        f'du plus général au plus spécifique. Le premier mot-clé DOIT être choisi parmi cette liste : '
        f'{available_tags}. N\'écrit que les mots-clés. Ne répète aucun mot-clé. '
        f'Tu peux inventer tous les mots-clés que tu veux pour les tags suivants. '
        f'Exemple : "Personnes, Chat, Salon, Tapis". Mots-clés :'
    )

    response: ChatResponse = chat(
        model=model,
        messages=[
            {
                'role': 'user',
                'content': prompt,
                'images': [str(image_path)],
            },
        ]
    )

    return parse_tags(response.message.content)


def parse_tags(raw_tags: str) -> List[str]:
    """
    Parse et nettoie les tags retournés par le LLM.

    Args:
        raw_tags: Chaîne brute de tags du LLM

    Returns:
        Liste de tags nettoyés
    """
    # Nettoyer la réponse
    cleaned = raw_tags.strip()

    # Enlever les guillemets au début et à la fin si présents
    cleaned = re.sub(r'^["\']|["\']$', '', cleaned)

    # Séparer par virgule
    tags = [tag.strip() for tag in cleaned.split(',')]

    # Nettoyer chaque tag
    cleaned_tags = []
    for tag in tags:
        # Enlever les caractères spéciaux au début/fin
        tag = re.sub(r'^[^\w\s-]+|[^\w\s-]+$', '', tag, flags=re.UNICODE)
        tag = tag.strip()

        if tag and tag not in cleaned_tags:  # Éviter les doublons
            cleaned_tags.append(tag)

    return cleaned_tags


def split_tags(tags: List[str]) -> Tuple[str, List[str]]:
    """
    Sépare le premier tag (catégorie) des tags supplémentaires.

    Args:
        tags: Liste de tous les tags

    Returns:
        Tuple (premier_tag, tags_supplémentaires)
    """
    if not tags:
        return "Sans-categorie", []

    first_tag = tags[0]
    extra_tags = tags[1:] if len(tags) > 1 else []

    return first_tag, extra_tags
