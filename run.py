import argparse
from pathlib import Path
from ollama import chat
from ollama import ChatResponse


def load_tags(tags_file: str = './tags.txt') -> str:
    """Charge les tags depuis le fichier et les retourne sous forme de chaîne séparée par des virgules."""
    try:
        with open(tags_file, 'r', encoding='utf-8') as f:
            tags = [line.strip() for line in f if line.strip()]
        return ', '.join(tags)
    except FileNotFoundError:
        print(f"Avertissement: Le fichier {tags_file} n'a pas été trouvé.")
        return ''


def main():
    parser = argparse.ArgumentParser(
        description='Organisateur d\'images intelligent utilisant un LLM pour générer des tags et classer automatiquement vos photos.'
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Répertoire contenant les images à traiter'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gemma3:4b',
        help='Nom du modèle LLM à utiliser (défaut: gemma3:4b)'
    )

    parser.add_argument(
        '--move',
        action='store_true',
        default=False,
        help='Déplacer les images au lieu de les copier (défaut: False)'
    )

    parser.add_argument(
        '--tagcount',
        type=int,
        default=8,
        help='Nombre de tags à générer pour chaque image (défaut: 8)'
    )

    parser.add_argument(
        '--outdir',
        type=str,
        default='choucroute-cosmique',
        help='Répertoire de destination pour les images copiées (défaut: choucroute-cosmique)'
    )

    args = parser.parse_args()
    available_tags = load_tags()

    print(f"Répertoire source: {args.directory}")
    print(f"Modèle LLM: {args.model}")
    print(f"Mode: {'déplacement' if args.move else 'copie'}")
    print(f"Nombre de tags: {args.tagcount}")
    print(f"Répertoire de sortie: {args.outdir}")

    prompt = f'Écrit {args.tagcount} mots-clés en français décrivant cette image, séparés par une virgule, du plus commun au plus spécifique. Le premier mot-clé DOIT être choisi parmi cette liste : {available_tags}. N\'écrit que les mots-clés. Ne répète aucun mot-clé. Tu peux inventer tous les mots-clés que tu veux pour les tags suivants. Exemple : "Personnes, Chat, Salon, Tapis". Mots-clés :'

    response: ChatResponse = chat(model=args.model, messages=[
        {
            'role': 'user',
            'content': prompt,
            'images': ['./images/photos/depositphotos_9209115-stock-photo-young-group-of-friends-hanging.jpg'],
        },
    ])

    print(f"\nTags générés: {response.message.content}")


if __name__ == '__main__':
    main()