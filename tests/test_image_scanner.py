"""Tests pour le module image_scanner."""

import pytest
from pathlib import Path
import tempfile
import shutil
from image_scanner import scan_images, IMAGE_EXTENSIONS


class TestScanImages:
    """Tests pour la fonction scan_images."""

    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def image_test_dir(self):
        """Utilise le répertoire d'images de test existant."""
        return "./tests/images"

    def test_scan_images_with_real_images(self, image_test_dir):
        """Test le scan du répertoire d'images de test réelles."""
        images = scan_images(image_test_dir)

        assert len(images) > 0, "Devrait trouver au moins une image"
        assert all(isinstance(img, Path) for img in images), "Tous les résultats devraient être des Path"
        assert all(img.exists() for img in images), "Toutes les images devraient exister"

    def test_scan_images_filters_by_extension(self, image_test_dir):
        """Test que seules les images avec les bonnes extensions sont retournées."""
        images = scan_images(image_test_dir)

        for img in images:
            assert img.suffix.lower() in IMAGE_EXTENSIONS, f"{img.suffix} devrait être une extension d'image valide"

    def test_scan_images_sorted(self, image_test_dir):
        """Test que les résultats sont triés."""
        images = scan_images(image_test_dir)

        # Vérifier que la liste est triée
        assert images == sorted(images), "Les images devraient être triées"

    def test_scan_images_empty_directory(self, temp_dir):
        """Test le scan d'un répertoire vide."""
        images = scan_images(temp_dir)

        assert images == [], "Un répertoire vide devrait retourner une liste vide"

    def test_scan_images_nonexistent_directory(self):
        """Test le scan d'un répertoire qui n'existe pas."""
        with pytest.raises(FileNotFoundError) as exc_info:
            scan_images("/chemin/qui/nexiste/pas")

        assert "n'existe pas" in str(exc_info.value)

    def test_scan_images_file_not_directory(self, temp_dir):
        """Test le scan d'un fichier au lieu d'un répertoire."""
        # Créer un fichier
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("contenu")

        with pytest.raises(NotADirectoryError) as exc_info:
            scan_images(str(test_file))

        assert "n'est pas un répertoire" in str(exc_info.value)

    def test_scan_images_with_subdirectories(self, temp_dir):
        """Test le scan récursif dans les sous-répertoires."""
        # Créer une structure de répertoires avec des images
        subdir1 = Path(temp_dir) / "subdir1"
        subdir2 = Path(temp_dir) / "subdir1" / "subdir2"
        subdir1.mkdir()
        subdir2.mkdir()

        # Créer des fichiers image factices (vides mais avec les bonnes extensions)
        img1 = Path(temp_dir) / "image1.jpg"
        img2 = subdir1 / "image2.png"
        img3 = subdir2 / "image3.gif"

        img1.touch()
        img2.touch()
        img3.touch()

        images = scan_images(temp_dir)

        assert len(images) == 3, "Devrait trouver les 3 images dans la hiérarchie"
        assert img1 in images
        assert img2 in images
        assert img3 in images

    def test_scan_images_ignores_non_image_files(self, temp_dir):
        """Test que les fichiers non-images sont ignorés."""
        # Créer divers types de fichiers
        (Path(temp_dir) / "image.jpg").touch()
        (Path(temp_dir) / "document.txt").touch()
        (Path(temp_dir) / "video.mp4").touch()
        (Path(temp_dir) / "script.py").touch()
        (Path(temp_dir) / "readme.md").touch()

        images = scan_images(temp_dir)

        assert len(images) == 1, "Devrait trouver seulement 1 image"
        assert images[0].suffix == ".jpg"

    def test_scan_images_case_insensitive_extensions(self, temp_dir):
        """Test que les extensions sont traitées de manière insensible à la casse."""
        # Créer des fichiers avec différentes casses
        (Path(temp_dir) / "image1.JPG").touch()
        (Path(temp_dir) / "image2.Png").touch()
        (Path(temp_dir) / "image3.GIF").touch()

        images = scan_images(temp_dir)

        assert len(images) == 3, "Devrait trouver les 3 images quelle que soit la casse"

    def test_scan_images_all_supported_extensions(self, temp_dir):
        """Test que toutes les extensions supportées sont détectées."""
        # Créer un fichier pour chaque extension supportée
        for ext in IMAGE_EXTENSIONS:
            (Path(temp_dir) / f"image{ext}").touch()

        images = scan_images(temp_dir)

        assert len(images) == len(IMAGE_EXTENSIONS), f"Devrait trouver {len(IMAGE_EXTENSIONS)} images"

    def test_image_extensions_constant(self):
        """Test que IMAGE_EXTENSIONS contient les extensions attendues."""
        expected_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

        assert IMAGE_EXTENSIONS == expected_extensions, "IMAGE_EXTENSIONS devrait contenir toutes les extensions attendues"
