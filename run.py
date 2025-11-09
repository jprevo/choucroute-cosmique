import argparse
from ollama import chat
from ollama import ChatResponse


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

    # TODO: Implémenter la logique de traitement des images
    print(f"Répertoire source: {args.directory}")
    print(f"Modèle LLM: {args.model}")
    print(f"Mode: {'déplacement' if args.move else 'copie'}")
    print(f"Nombre de tags: {args.tagcount}")
    print(f"Répertoire de sortie: {args.outdir}")

    # Exemple d'utilisation du LLM (à adapter avec les arguments)
    response: ChatResponse = chat(model=args.model, messages=[
        {
            'role': 'user',
            'content': f'Écrit {args.tagcount} mots-clés en français décrivant cette image, séparés par une virgule, du plus commun au plus spécifique. N\'écrit que les mots-clés. Exemple : "Personne, Chat, Salon, Tapis". Mots-clés :',
            'images': ['./images/photos/depositphotos_9209115-stock-photo-young-group-of-friends-hanging.jpg'],
        },
    ])

    print(f"\nTags générés: {response.message.content}")


if __name__ == '__main__':
    main()