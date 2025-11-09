import argparse
from pathlib import Path
from functools import partial

from image_scanner import scan_images
from llm_client import generate_tags, split_tags
from parallel_processor import process_images_parallel
from file_operations import organize_image
from exif_tagger import add_tags_to_image


def load_tags(tags_file: str = './tags.txt') -> str:
    """Charge les tags depuis le fichier et les retourne sous forme de chaîne séparée par des virgules."""
    try:
        with open(tags_file, 'r', encoding='utf-8') as f:
            tags = [line.strip() for line in f if line.strip()]
        return ', '.join(tags)
    except FileNotFoundError:
        print(f"Avertissement: Le fichier {tags_file} n'a pas été trouvé.")
        return ''


def print_progress(completed: int, total: int):
    """Affiche la progression du traitement."""
    percentage = (completed / total) * 100
    print(f"Progression: {completed}/{total} images traitées ({percentage:.1f}%)")


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

    parser.add_argument(
        '--max-parallel',
        type=int,
        default=4,
        help='Nombre maximum de requêtes LLM en parallèle (défaut: 4)'
    )

    args = parser.parse_args()

    # Charger les tags disponibles
    available_tags = load_tags()
    if not available_tags:
        print("Erreur: Impossible de charger les tags depuis tags.txt")
        return

    # Afficher les paramètres
    print("=" * 60)
    print("CHOUCROUTE-COSMIQUE - Organisateur d'images intelligent")
    print("=" * 60)
    print(f"Répertoire source: {args.directory}")
    print(f"Répertoire de sortie: {args.outdir}")
    print(f"Modèle LLM: {args.model}")
    print(f"Mode: {'déplacement' if args.move else 'copie'}")
    print(f"Nombre de tags par image: {args.tagcount}")
    print(f"Traitement parallèle: {args.max_parallel} workers")
    print("=" * 60)

    # Étape 1: Scanner les images
    print("\n[1/3] Scan du répertoire source...")
    try:
        image_paths = scan_images(args.directory)
        print(f"✓ {len(image_paths)} image(s) trouvée(s)")
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Erreur: {e}")
        return

    if not image_paths:
        print("Aucune image à traiter. Terminé.")
        return

    # Étape 2: Générer les tags avec le LLM (en parallèle)
    print(f"\n[2/3] Génération des tags avec le LLM ({args.model})...")

    # Créer une fonction partielle avec les paramètres fixes
    tag_function = partial(
        generate_tags,
        model=args.model,
        tag_count=args.tagcount,
        available_tags=available_tags
    )

    # Traiter les images en parallèle
    results = process_images_parallel(
        image_paths,
        tag_function,
        max_workers=args.max_parallel,
        progress_callback=print_progress
    )

    # Compter les succès et échecs
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]

    print(f"\n✓ Tags générés pour {len(successful_results)} image(s)")
    if failed_results:
        print(f"✗ Échec pour {len(failed_results)} image(s)")
        for result in failed_results:
            print(f"  - {result.image_path.name}: {result.error}")

    # Étape 3: Organiser les images et ajouter les tags EXIF
    print(f"\n[3/3] Organisation des images dans {args.outdir}...")

    organized_count = 0
    tagged_count = 0

    for result in successful_results:
        if not result.tags:
            print(f"Attention: Aucun tag généré pour {result.image_path.name}, ignoré")
            continue

        # Séparer le premier tag (catégorie) des autres
        first_tag, extra_tags = split_tags(result.tags)

        try:
            # Organiser le fichier
            dest_path = organize_image(
                result.image_path,
                first_tag,
                extra_tags,
                args.outdir,
                move=args.move
            )
            organized_count += 1

            # Ajouter les tags EXIF
            if add_tags_to_image(dest_path, result.tags):
                tagged_count += 1

            print(f"✓ {result.image_path.name} → {first_tag}/{dest_path.name}")

        except Exception as e:
            print(f"✗ Erreur lors de l'organisation de {result.image_path.name}: {e}")

    # Résumé final
    print("\n" + "=" * 60)
    print("TRAITEMENT TERMINÉ")
    print("=" * 60)
    print(f"Images traitées: {len(successful_results)}/{len(image_paths)}")
    print(f"Images organisées: {organized_count}")
    print(f"Images avec tags EXIF: {tagged_count}")
    print(f"Répertoire de sortie: {args.outdir}")
    print("=" * 60)


if __name__ == '__main__':
    main()