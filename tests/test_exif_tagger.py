"""Tests pour le module exif_tagger."""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
from exif_tagger import add_tags_to_image, read_tags_from_image, EXIF_AVAILABLE


class TestExifTagger:
    """Tests pour les fonctions EXIF."""

    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def test_image_jpg(self, temp_dir):
        """Crée une image JPG de test."""
        img_path = Path(temp_dir) / "test_image.jpg"
        # Créer une petite image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(str(img_path))
        return img_path

    @pytest.fixture
    def test_image_png(self, temp_dir):
        """Crée une image PNG de test."""
        img_path = Path(temp_dir) / "test_image.png"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(str(img_path))
        return img_path

    @pytest.fixture
    def real_test_image(self):
        """Utilise une vraie image de test si disponible."""
        img_path = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")
        if img_path.exists():
            # Créer une copie pour ne pas modifier l'original
            temp_copy = Path(tempfile.gettempdir()) / "test_real_image_copy.jpg"
            shutil.copy2(img_path, temp_copy)
            yield temp_copy
            if temp_copy.exists():
                temp_copy.unlink()
        else:
            yield None

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_to_jpg_image(self, test_image_jpg):
        """Test l'ajout de tags à une image JPG."""
        tags = ["Nature", "Montagne", "Paysage", "Été"]

        result = add_tags_to_image(test_image_jpg, tags)

        assert result is True
        assert test_image_jpg.exists()

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_read_tags_from_image(self, test_image_jpg):
        """Test la lecture de tags depuis une image."""
        tags = ["Vacances", "Plage", "Soleil"]

        # Ajouter les tags
        add_tags_to_image(test_image_jpg, tags)

        # Lire les tags
        read_tags = read_tags_from_image(test_image_jpg)

        assert len(read_tags) > 0
        assert all(tag in read_tags for tag in tags)

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_preserves_image(self, test_image_jpg):
        """Test que l'ajout de tags préserve l'image."""
        original_size = test_image_jpg.stat().st_size

        tags = ["Test", "Image"]
        add_tags_to_image(test_image_jpg, tags)

        # L'image devrait toujours être lisible
        img = Image.open(test_image_jpg)
        assert img.size == (100, 100)

        # La taille ne devrait pas changer dramatiquement
        new_size = test_image_jpg.stat().st_size
        # EXIF ajoute quelques octets, mais pas énorme
        assert abs(new_size - original_size) < 10000

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_with_special_characters(self, test_image_jpg):
        """Test l'ajout de tags avec des caractères spéciaux."""
        tags = ["Été", "Forêt", "Château", "Noël"]

        result = add_tags_to_image(test_image_jpg, tags)

        assert result is True

        # Vérifier qu'on peut lire les tags
        read_tags = read_tags_from_image(test_image_jpg)
        assert len(read_tags) > 0

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_multiple_tags(self, test_image_jpg):
        """Test l'ajout de plusieurs tags."""
        tags = ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5", "Tag6", "Tag7", "Tag8"]

        result = add_tags_to_image(test_image_jpg, tags)

        assert result is True

        read_tags = read_tags_from_image(test_image_jpg)
        assert len(read_tags) == len(tags)

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_empty_tags_list(self, test_image_jpg):
        """Test l'ajout d'une liste vide de tags."""
        tags = []

        result = add_tags_to_image(test_image_jpg, tags)

        # Devrait réussir même avec une liste vide
        assert result is True

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_read_tags_from_image_without_tags(self, test_image_jpg):
        """Test la lecture de tags d'une image sans tags."""
        tags = read_tags_from_image(test_image_jpg)

        # Devrait retourner une liste vide
        assert isinstance(tags, list)

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_update_existing_tags(self, test_image_jpg):
        """Test la mise à jour de tags existants."""
        # Ajouter des tags initiaux
        initial_tags = ["Tag1", "Tag2"]
        add_tags_to_image(test_image_jpg, initial_tags)

        # Ajouter de nouveaux tags
        new_tags = ["Tag3", "Tag4", "Tag5"]
        add_tags_to_image(test_image_jpg, new_tags)

        # Les nouveaux tags devraient remplacer les anciens
        read_tags = read_tags_from_image(test_image_jpg)
        assert "Tag3" in read_tags
        assert "Tag4" in read_tags

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_tags_with_semicolons(self, test_image_jpg):
        """Test que les tags sont correctement séparés par des points-virgules."""
        tags = ["Nature", "Montagne", "Ciel"]

        add_tags_to_image(test_image_jpg, tags)
        read_tags = read_tags_from_image(test_image_jpg)

        # Tous les tags devraient être présents
        assert len(read_tags) == len(tags)

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_to_real_image(self, real_test_image):
        """Test l'ajout de tags à une vraie image de test."""
        if real_test_image is None:
            pytest.skip("Image de test non disponible")

        tags = ["Nourriture", "Restaurant", "Gastronomie"]

        result = add_tags_to_image(real_test_image, tags)

        assert result is True

        # Vérifier que l'image est toujours valide
        img = Image.open(real_test_image)
        assert img.size[0] > 0
        assert img.size[1] > 0

        # Lire les tags
        read_tags = read_tags_from_image(real_test_image)
        assert len(read_tags) > 0

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_preserves_original_exif(self, real_test_image):
        """Test que l'ajout de tags préserve les données EXIF existantes."""
        if real_test_image is None:
            pytest.skip("Image de test non disponible")

        # Charger l'image pour vérifier qu'elle a des données EXIF
        img = Image.open(real_test_image)
        original_exif = img.getexif()

        tags = ["Test", "Préservation", "EXIF"]
        add_tags_to_image(real_test_image, tags)

        # Recharger et vérifier que des données EXIF existent toujours
        img_after = Image.open(real_test_image)
        new_exif = img_after.getexif()

        # L'image devrait toujours avoir des données EXIF
        assert len(new_exif) > 0

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_add_tags_to_png_image(self, test_image_png):
        """Test l'ajout de tags à une image PNG."""
        tags = ["Test", "PNG"]

        # PNG ne supporte pas EXIF de la même manière que JPG
        # Le comportement peut varier
        result = add_tags_to_image(test_image_png, tags)

        # Le résultat devrait être booléen
        assert isinstance(result, bool)

    def test_read_tags_when_exif_not_available(self, test_image_jpg, monkeypatch):
        """Test la lecture de tags quand EXIF n'est pas disponible."""
        # Simuler l'indisponibilité d'EXIF
        import exif_tagger
        monkeypatch.setattr(exif_tagger, 'EXIF_AVAILABLE', False)

        tags = read_tags_from_image(test_image_jpg)

        # Devrait retourner une liste vide
        assert tags == []

    def test_add_tags_when_exif_not_available(self, test_image_jpg, monkeypatch):
        """Test l'ajout de tags quand EXIF n'est pas disponible."""
        import exif_tagger
        monkeypatch.setattr(exif_tagger, 'EXIF_AVAILABLE', False)

        result = add_tags_to_image(test_image_jpg, ["Test"])

        # Devrait retourner False
        assert result is False

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_tags_format_in_exif(self, test_image_jpg):
        """Test que les tags sont formatés correctement dans EXIF."""
        tags = ["Tag1", "Tag2", "Tag3"]

        add_tags_to_image(test_image_jpg, tags)

        # Lire les tags
        read_tags = read_tags_from_image(test_image_jpg)

        # Vérifier que les tags sont séparés correctement
        assert len(read_tags) == 3
        assert all(tag.strip() for tag in read_tags)  # Pas d'espaces vides

    @pytest.mark.skipif(not EXIF_AVAILABLE, reason="PIL/piexif non disponibles")
    def test_long_tags_list(self, test_image_jpg):
        """Test l'ajout d'une longue liste de tags."""
        tags = [f"Tag{i}" for i in range(20)]

        result = add_tags_to_image(test_image_jpg, tags)

        assert result is True

        read_tags = read_tags_from_image(test_image_jpg)
        assert len(read_tags) == 20
