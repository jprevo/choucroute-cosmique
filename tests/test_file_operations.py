"""Tests pour le module file_operations."""

import pytest
from pathlib import Path
import tempfile
import shutil
from file_operations import sanitize_filename, build_new_filename, organize_image


class TestSanitizeFilename:
    """Tests pour la fonction sanitize_filename."""

    def test_sanitize_normal_filename(self):
        """Test qu'un nom de fichier normal reste inchangé."""
        name = "mon_fichier_normal.jpg"
        result = sanitize_filename(name)

        assert result == "mon_fichier_normal.jpg"

    def test_sanitize_removes_forbidden_characters(self):
        """Test que les caractères interdits sont remplacés."""
        name = 'fichier<avec>des:caractères"/interdits\\|?*.jpg'
        result = sanitize_filename(name)

        # Les caractères interdits devraient être remplacés par des underscores
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert '"' not in result
        assert '/' not in result
        assert '\\' not in result
        assert '|' not in result
        assert '?' not in result
        assert '*' not in result

    def test_sanitize_replaces_multiple_spaces(self):
        """Test que les espaces multiples sont remplacés par un seul."""
        name = "fichier    avec     beaucoup    d'espaces"
        result = sanitize_filename(name)

        assert "    " not in result
        assert "fichier avec beaucoup d'espaces" == result

    def test_sanitize_strips_spaces(self):
        """Test que les espaces au début et à la fin sont supprimés."""
        name = "   fichier avec espaces   "
        result = sanitize_filename(name)

        assert result == "fichier avec espaces"

    def test_sanitize_long_filename(self):
        """Test que les noms trop longs sont tronqués."""
        name = "a" * 300
        result = sanitize_filename(name)

        assert len(result) <= 200

    def test_sanitize_unicode_characters(self):
        """Test que les caractères Unicode sont préservés."""
        name = "été_forêt_château_cœur.jpg"
        result = sanitize_filename(name)

        assert result == "été_forêt_château_cœur.jpg"

    def test_sanitize_empty_string(self):
        """Test le comportement avec une chaîne vide."""
        name = ""
        result = sanitize_filename(name)

        assert result == ""

    def test_sanitize_only_forbidden_characters(self):
        """Test une chaîne composée uniquement de caractères interdits."""
        name = "<>:\"/\\|?*"
        result = sanitize_filename(name)

        # Devrait être remplacé par des underscores
        assert all(c == '_' for c in result)


class TestBuildNewFilename:
    """Tests pour la fonction build_new_filename."""

    def test_build_filename_with_tags(self):
        """Test la construction d'un nom de fichier avec des tags."""
        original_path = Path("vacation.jpg")
        extra_tags = ["Plage", "Été", "Soleil"]

        result = build_new_filename(original_path, extra_tags)

        assert result == "vacation_Plage_Été_Soleil.jpg"

    def test_build_filename_without_tags(self):
        """Test la construction d'un nom de fichier sans tags."""
        original_path = Path("photo.jpg")
        extra_tags = []

        result = build_new_filename(original_path, extra_tags)

        assert result == "photo.jpg"

    def test_build_filename_preserves_extension(self):
        """Test que l'extension est préservée."""
        original_path = Path("image.png")
        extra_tags = ["Nature", "Montagne"]

        result = build_new_filename(original_path, extra_tags)

        assert result.endswith(".png")

    def test_build_filename_max_tags(self):
        """Test que le nombre de tags est limité."""
        original_path = Path("photo.jpg")
        extra_tags = ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5", "Tag6", "Tag7", "Tag8"]

        result = build_new_filename(original_path, extra_tags, max_tags_in_filename=3)

        # Devrait utiliser seulement les 3 premiers tags
        assert "Tag1" in result
        assert "Tag2" in result
        assert "Tag3" in result
        assert "Tag6" not in result
        assert "Tag7" not in result

    def test_build_filename_sanitizes_tags(self):
        """Test que les tags sont sanitizés."""
        original_path = Path("photo.jpg")
        extra_tags = ["Tag<Spécial>", "Tag/Interdit"]

        result = build_new_filename(original_path, extra_tags)

        # Les caractères interdits devraient être remplacés
        assert "<" not in result
        assert ">" not in result
        assert "/" not in result

    def test_build_filename_with_complex_extension(self):
        """Test avec des extensions multiples."""
        original_path = Path("archive.tar.gz")
        extra_tags = ["Backup", "2024"]

        result = build_new_filename(original_path, extra_tags)

        # Devrait préserver seulement la dernière extension
        assert result.endswith(".gz")
        assert "archive" in result

    def test_build_filename_no_extension(self):
        """Test avec un fichier sans extension."""
        original_path = Path("fichier")
        extra_tags = ["Tag1", "Tag2"]

        result = build_new_filename(original_path, extra_tags)

        assert result == "fichier_Tag1_Tag2"


class TestOrganizeImage:
    """Tests pour la fonction organize_image."""

    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def source_image(self, temp_dir):
        """Crée une image source pour les tests."""
        source_path = Path(temp_dir) / "source_image.jpg"
        source_path.write_text("fake image content")
        return source_path

    def test_organize_image_copy(self, source_image, temp_dir):
        """Test la copie d'une image."""
        output_dir = Path(temp_dir) / "output"
        first_tag = "Nature"
        extra_tags = ["Montagne", "Ciel"]

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=False
        )

        # Le fichier source devrait toujours exister (copie)
        assert source_image.exists()
        # Le fichier destination devrait exister
        assert dest_path.exists()
        # Le fichier devrait être dans le bon répertoire
        assert dest_path.parent.name == "Nature"

    def test_organize_image_move(self, source_image, temp_dir):
        """Test le déplacement d'une image."""
        output_dir = Path(temp_dir) / "output"
        first_tag = "Ville"
        extra_tags = ["Paris", "Tour Eiffel"]

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=True
        )

        # Le fichier source ne devrait plus exister (déplacement)
        assert not source_image.exists()
        # Le fichier destination devrait exister
        assert dest_path.exists()

    def test_organize_image_creates_category_directory(self, source_image, temp_dir):
        """Test que le répertoire de catégorie est créé."""
        output_dir = Path(temp_dir) / "output"
        first_tag = "Animaux"
        extra_tags = ["Chat"]

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=False
        )

        # Le répertoire de catégorie devrait exister
        category_dir = Path(output_dir) / "Animaux"
        assert category_dir.exists()
        assert category_dir.is_dir()

    def test_organize_image_handles_name_conflicts(self, temp_dir):
        """Test la gestion des conflits de noms."""
        # Créer deux images sources identiques
        source1 = Path(temp_dir) / "image.jpg"
        source2 = Path(temp_dir) / "image.jpg"
        source1.write_text("image 1")

        output_dir = Path(temp_dir) / "output"
        first_tag = "Photos"
        extra_tags = ["Tag1"]

        # Organiser la première image
        dest1 = organize_image(source1, first_tag, extra_tags, str(output_dir), move=False)

        # Créer une deuxième image source
        source2 = Path(temp_dir) / "source2" / "image.jpg"
        source2.parent.mkdir(exist_ok=True)
        source2.write_text("image 2")

        # Organiser la deuxième image (même nom)
        dest2 = organize_image(source2, first_tag, extra_tags, str(output_dir), move=False)

        # Les deux fichiers devraient exister avec des noms différents
        assert dest1.exists()
        assert dest2.exists()
        assert dest1 != dest2

    def test_organize_image_filename_format(self, source_image, temp_dir):
        """Test que le format du nom de fichier est correct."""
        output_dir = Path(temp_dir) / "output"
        first_tag = "Personnes"
        extra_tags = ["Famille", "Vacances"]

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=False
        )

        # Vérifier le format du nom
        assert "source_image" in dest_path.name
        assert "Famille" in dest_path.name
        assert "Vacances" in dest_path.name
        assert dest_path.suffix == ".jpg"

    def test_organize_image_sanitizes_category_name(self, source_image, temp_dir):
        """Test que le nom de catégorie est sanitized."""
        output_dir = Path(temp_dir) / "output"
        first_tag = "Catégorie/Interdite<>"
        extra_tags = []

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=False
        )

        # Les caractères interdits ne devraient pas être dans le nom du répertoire
        assert "/" not in dest_path.parent.name
        assert "<" not in dest_path.parent.name
        assert ">" not in dest_path.parent.name

    def test_organize_image_preserves_content(self, source_image, temp_dir):
        """Test que le contenu du fichier est préservé."""
        content = "Contenu de test unique 12345"
        source_image.write_text(content)

        output_dir = Path(temp_dir) / "output"
        first_tag = "Test"
        extra_tags = []

        dest_path = organize_image(
            source_image,
            first_tag,
            extra_tags,
            str(output_dir),
            move=False
        )

        # Le contenu devrait être identique
        assert dest_path.read_text() == content

    def test_organize_image_with_real_image(self, temp_dir):
        """Test avec une vraie image du répertoire de test."""
        real_image = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")

        if real_image.exists():
            output_dir = Path(temp_dir) / "output"
            first_tag = "Nourriture"
            extra_tags = ["Restaurant", "Plat"]

            dest_path = organize_image(
                real_image,
                first_tag,
                extra_tags,
                str(output_dir),
                move=False
            )

            # Vérifier que l'image a été copiée
            assert dest_path.exists()
            assert dest_path.parent.name == "Nourriture"
            assert real_image.exists()  # L'original devrait toujours exister
            # Vérifier que les tailles sont identiques
            assert dest_path.stat().st_size == real_image.stat().st_size
