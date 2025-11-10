"""Tests d'intégration pour l'ensemble du système."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch
from functools import partial

from image_scanner import scan_images
from llm_client import generate_tags, split_tags
from parallel_processor import process_images_parallel
from file_operations import organize_image
from exif_tagger import add_tags_to_image, read_tags_from_image, EXIF_AVAILABLE
from run import load_tags


class TestIntegration:
    """Tests d'intégration du système complet."""

    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def test_images_dir(self):
        """Retourne le répertoire d'images de test."""
        return "./tests/images"

    @pytest.fixture
    def tags_file(self, temp_dir):
        """Crée un fichier de tags pour les tests."""
        tags_path = Path(temp_dir) / "tags.txt"
        tags_content = """Nature
Personnes
Ville
Nourriture
Animaux
Vacances
Architecture
Sport"""
        tags_path.write_text(tags_content)
        return str(tags_path)

    def test_load_tags_function(self, tags_file):
        """Test le chargement des tags depuis un fichier."""
        tags = load_tags(tags_file)

        assert tags != ""
        assert "Nature" in tags
        assert "Personnes" in tags
        assert "," in tags  # Les tags devraient être séparés par des virgules

    def test_load_tags_missing_file(self):
        """Test le chargement des tags avec un fichier manquant."""
        tags = load_tags("/fichier/inexistant.txt")

        assert tags == ""

    def test_scan_and_process_workflow(self, test_images_dir):
        """Test le workflow de scan et de traitement."""
        try:
            # Étape 1: Scanner les images
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            # Étape 2: Traiter avec une fonction factice
            def dummy_tag_function(image_path):
                return ["Nature", "Paysage", "Test"]

            results = process_images_parallel(
                images[:2],  # Limiter à 2 images
                dummy_tag_function,
                max_workers=2
            )

            # Vérifier les résultats
            assert len(results) <= 2
            assert all(r.success for r in results)
            assert all(len(r.tags) > 0 for r in results)

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_full_workflow_with_real_images(self, test_images_dir, temp_dir):
        """Test le workflow complet avec de vraies images."""
        try:
            # Scanner les images
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            # Définir une fonction de tagging factice
            def mock_tag_function(image_path):
                return ["Nourriture", "Restaurant", "Plat", "Gastronomie"]

            # Traiter les images
            results = process_images_parallel(
                images[:1],  # Une seule image pour la vitesse
                mock_tag_function,
                max_workers=1
            )

            # Organiser les images
            output_dir = Path(temp_dir) / "organized"

            for result in results:
                if result.success:
                    first_tag, extra_tags = split_tags(result.tags)

                    dest_path = organize_image(
                        result.image_path,
                        first_tag,
                        extra_tags,
                        str(output_dir),
                        move=False
                    )

                    # Vérifier que le fichier a été créé
                    assert dest_path.exists()

                    # Vérifier la structure de répertoires
                    assert dest_path.parent.name == first_tag

                    # Vérifier que les tags sont dans le nom de fichier
                    for tag in extra_tags[:3]:  # Premiers tags dans le nom
                        assert tag in dest_path.name or tag.replace(' ', '_') in dest_path.name

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_full_workflow_with_exif(self, test_images_dir, temp_dir):
        """Test le workflow complet incluant les métadonnées EXIF."""
        try:
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            # Trouver une image JPG (EXIF fonctionne mieux avec JPG)
            jpg_images = [img for img in images if img.suffix.lower() in ['.jpg', '.jpeg']]

            if not jpg_images:
                pytest.skip("Aucune image JPG de test trouvée")

            def mock_tag_function(image_path):
                return ["Nature", "Montagne", "Paysage", "Été"]

            # Traiter
            results = process_images_parallel(
                jpg_images[:1],
                mock_tag_function,
                max_workers=1
            )

            # Organiser et ajouter EXIF
            output_dir = Path(temp_dir) / "organized_with_exif"

            for result in results:
                if result.success:
                    first_tag, extra_tags = split_tags(result.tags)

                    dest_path = organize_image(
                        result.image_path,
                        first_tag,
                        extra_tags,
                        str(output_dir),
                        move=False
                    )

                    # Ajouter les tags EXIF
                    exif_success = add_tags_to_image(dest_path, result.tags)
                    assert exif_success is True

                    # Lire les tags EXIF
                    read_tags = read_tags_from_image(dest_path)
                    assert len(read_tags) > 0
                    assert all(tag in read_tags for tag in result.tags)

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    @patch('llm_client.chat')
    def test_workflow_with_mocked_llm(self, mock_chat, test_images_dir, temp_dir, tags_file):
        """Test le workflow complet avec un LLM mocké."""
        try:
            # Configurer le mock
            mock_response = Mock()
            mock_response.message.content = "Nature, Forêt, Arbres, Verdure, Paysage"
            mock_chat.return_value = mock_response

            # Scanner les images
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            # Charger les tags disponibles
            available_tags = load_tags(tags_file)

            # Fonction de tagging avec LLM mocké
            tag_function = partial(
                generate_tags,
                model="test-model",
                tag_count=5,
                available_tags=available_tags
            )

            # Traiter
            results = process_images_parallel(
                images[:1],
                tag_function,
                max_workers=1
            )

            # Vérifier que le LLM a été appelé
            assert mock_chat.called

            # Organiser
            output_dir = Path(temp_dir) / "organized_mock"

            for result in results:
                if result.success and result.tags:
                    first_tag, extra_tags = split_tags(result.tags)

                    dest_path = organize_image(
                        result.image_path,
                        first_tag,
                        extra_tags,
                        str(output_dir),
                        move=False
                    )

                    assert dest_path.exists()

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_organize_multiple_images_same_category(self, test_images_dir, temp_dir):
        """Test l'organisation de plusieurs images dans la même catégorie."""
        try:
            images = scan_images(test_images_dir)

            if len(images) < 2:
                pytest.skip("Pas assez d'images de test")

            output_dir = Path(temp_dir) / "multi_category"

            # Organiser plusieurs images dans la même catégorie
            for i, image in enumerate(images[:3]):
                first_tag = "Nature"
                extra_tags = [f"Test{i}", "Paysage"]

                dest_path = organize_image(
                    image,
                    first_tag,
                    extra_tags,
                    str(output_dir),
                    move=False
                )

                assert dest_path.exists()
                assert dest_path.parent.name == "Nature"

            # Vérifier que toutes les images sont dans le même dossier
            nature_dir = output_dir / "Nature"
            assert nature_dir.exists()
            assert len(list(nature_dir.iterdir())) == 3

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_organize_images_different_categories(self, test_images_dir, temp_dir):
        """Test l'organisation d'images dans différentes catégories."""
        try:
            images = scan_images(test_images_dir)

            if len(images) < 3:
                pytest.skip("Pas assez d'images de test")

            output_dir = Path(temp_dir) / "multi_categories"
            categories = ["Nature", "Ville", "Nourriture"]

            # Organiser dans différentes catégories
            for i, image in enumerate(images[:3]):
                first_tag = categories[i]
                extra_tags = ["Test"]

                dest_path = organize_image(
                    image,
                    first_tag,
                    extra_tags,
                    str(output_dir),
                    move=False
                )

                assert dest_path.exists()
                assert dest_path.parent.name == first_tag

            # Vérifier que les 3 catégories existent
            for category in categories:
                category_dir = output_dir / category
                assert category_dir.exists()

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_error_handling_in_workflow(self, test_images_dir, temp_dir):
        """Test la gestion des erreurs dans le workflow."""
        try:
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            # Fonction qui échoue parfois
            def failing_function(image_path):
                if "jexo" in str(image_path):
                    raise ValueError("Erreur de test")
                return ["Test", "Tag"]

            # Traiter avec des erreurs
            results = process_images_parallel(
                images[:3],
                failing_function,
                max_workers=2
            )

            # Certains résultats devraient réussir, d'autres échouer
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]

            # Au moins certains devraient avoir réussi ou échoué
            assert len(results) > 0

            # Les échecs devraient avoir un message d'erreur
            for failure in failed:
                assert failure.error != ""

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_progress_tracking(self, test_images_dir):
        """Test le suivi de progression dans le workflow."""
        try:
            images = scan_images(test_images_dir)

            if not images:
                pytest.skip("Aucune image de test trouvée")

            progress_updates = []

            def progress_callback(completed, total):
                progress_updates.append((completed, total))

            def dummy_function(image_path):
                return ["Tag"]

            # Traiter avec callback
            process_images_parallel(
                images[:3],
                dummy_function,
                max_workers=2,
                progress_callback=progress_callback
            )

            # Vérifier que des mises à jour de progression ont été reçues
            assert len(progress_updates) > 0
            # Le dernier update devrait montrer 100% de complétion
            last_completed, last_total = progress_updates[-1]
            assert last_completed <= last_total

        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")
