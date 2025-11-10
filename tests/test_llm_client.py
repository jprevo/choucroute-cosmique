"""Tests pour le module llm_client."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from llm_client import parse_tags, split_tags, generate_tags


class TestParseTags:
    """Tests pour la fonction parse_tags."""

    def test_parse_simple_tags(self):
        """Test le parsing de tags simples."""
        raw_tags = "Nature, Montagne, Ciel, Bleu"
        result = parse_tags(raw_tags)

        assert result == ["Nature", "Montagne", "Ciel", "Bleu"]

    def test_parse_tags_with_extra_spaces(self):
        """Test le parsing de tags avec des espaces supplémentaires."""
        raw_tags = "  Nature  ,   Montagne   ,  Ciel  "
        result = parse_tags(raw_tags)

        assert result == ["Nature", "Montagne", "Ciel"]

    def test_parse_tags_with_quotes(self):
        """Test le parsing de tags entourés de guillemets."""
        raw_tags = '"Nature, Montagne, Ciel"'
        result = parse_tags(raw_tags)

        assert result == ["Nature", "Montagne", "Ciel"]

    def test_parse_tags_with_single_quotes(self):
        """Test le parsing de tags avec des guillemets simples."""
        raw_tags = "'Nature, Montagne, Ciel'"
        result = parse_tags(raw_tags)

        assert result == ["Nature", "Montagne", "Ciel"]

    def test_parse_tags_removes_duplicates(self):
        """Test que les doublons sont supprimés."""
        raw_tags = "Nature, Montagne, Nature, Ciel, Montagne"
        result = parse_tags(raw_tags)

        assert result == ["Nature", "Montagne", "Ciel"]

    def test_parse_tags_with_special_characters(self):
        """Test le parsing de tags avec des caractères spéciaux."""
        raw_tags = "Nature!, @Montagne#, $Ciel%"
        result = parse_tags(raw_tags)

        # Les caractères spéciaux au début et à la fin devraient être retirés
        assert "Nature" in result
        assert "Montagne" in result
        assert "Ciel" in result

    def test_parse_tags_empty_string(self):
        """Test le parsing d'une chaîne vide."""
        raw_tags = ""
        result = parse_tags(raw_tags)

        assert result == []

    def test_parse_tags_only_commas(self):
        """Test le parsing d'une chaîne avec seulement des virgules."""
        raw_tags = ", , ,"
        result = parse_tags(raw_tags)

        assert result == []

    def test_parse_tags_with_hyphens(self):
        """Test le parsing de tags avec des tirets."""
        raw_tags = "Belle-île, Arc-en-ciel, Porte-monnaie"
        result = parse_tags(raw_tags)

        assert result == ["Belle-île", "Arc-en-ciel", "Porte-monnaie"]

    def test_parse_tags_with_unicode(self):
        """Test le parsing de tags avec des caractères Unicode."""
        raw_tags = "Été, Forêt, Château, Cœur"
        result = parse_tags(raw_tags)

        assert result == ["Été", "Forêt", "Château", "Cœur"]

    def test_parse_tags_preserves_order(self):
        """Test que l'ordre des tags est préservé."""
        raw_tags = "Premier, Deuxième, Troisième, Quatrième"
        result = parse_tags(raw_tags)

        assert result == ["Premier", "Deuxième", "Troisième", "Quatrième"]

    def test_parse_tags_with_newlines(self):
        """Test le parsing de tags avec des retours à la ligne."""
        raw_tags = "Nature,\nMontagne,\nCiel"
        result = parse_tags(raw_tags)

        assert "Nature" in result
        assert "Montagne" in result
        assert "Ciel" in result

    def test_parse_tags_single_tag(self):
        """Test le parsing d'un seul tag."""
        raw_tags = "Nature"
        result = parse_tags(raw_tags)

        assert result == ["Nature"]


class TestSplitTags:
    """Tests pour la fonction split_tags."""

    def test_split_tags_normal(self):
        """Test le split de tags normal."""
        tags = ["Personnes", "Famille", "Plage", "Été"]
        first_tag, extra_tags = split_tags(tags)

        assert first_tag == "Personnes"
        assert extra_tags == ["Famille", "Plage", "Été"]

    def test_split_tags_single_tag(self):
        """Test le split avec un seul tag."""
        tags = ["Nature"]
        first_tag, extra_tags = split_tags(tags)

        assert first_tag == "Nature"
        assert extra_tags == []

    def test_split_tags_empty_list(self):
        """Test le split avec une liste vide."""
        tags = []
        first_tag, extra_tags = split_tags(tags)

        assert first_tag == "Sans-categorie"
        assert extra_tags == []

    def test_split_tags_two_tags(self):
        """Test le split avec deux tags."""
        tags = ["Nourriture", "Pizza"]
        first_tag, extra_tags = split_tags(tags)

        assert first_tag == "Nourriture"
        assert extra_tags == ["Pizza"]

    def test_split_tags_many_tags(self):
        """Test le split avec beaucoup de tags."""
        tags = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        first_tag, extra_tags = split_tags(tags)

        assert first_tag == "A"
        assert extra_tags == ["B", "C", "D", "E", "F", "G", "H", "I", "J"]
        assert len(extra_tags) == 9


class TestGenerateTags:
    """Tests pour la fonction generate_tags (avec mocking)."""

    @patch('llm_client.chat')
    def test_generate_tags_success(self, mock_chat):
        """Test la génération de tags avec succès."""
        # Créer un mock de la réponse
        mock_response = Mock()
        mock_response.message.content = "Nature, Montagne, Ciel, Bleu, Paysage"
        mock_chat.return_value = mock_response

        # Utiliser une image de test
        image_path = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")
        if image_path.exists():
            tags = generate_tags(
                image_path=image_path,
                model="test-model",
                tag_count=5,
                available_tags="Nature, Personnes, Ville"
            )

            assert len(tags) > 0
            assert all(isinstance(tag, str) for tag in tags)
            mock_chat.assert_called_once()

    @patch('llm_client.chat')
    def test_generate_tags_calls_parse_tags(self, mock_chat):
        """Test que generate_tags appelle parse_tags."""
        mock_response = Mock()
        mock_response.message.content = "  Tag1  ,  Tag2  ,  Tag3  "
        mock_chat.return_value = mock_response

        image_path = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")
        if image_path.exists():
            tags = generate_tags(
                image_path=image_path,
                model="test-model",
                tag_count=3,
                available_tags="Tag1, Tag2, Tag3"
            )

            # parse_tags devrait nettoyer les espaces
            assert "Tag1" in tags
            assert "Tag2" in tags
            assert "Tag3" in tags

    @patch('llm_client.chat')
    def test_generate_tags_with_quoted_response(self, mock_chat):
        """Test la génération de tags quand la réponse contient des guillemets."""
        mock_response = Mock()
        mock_response.message.content = '"Nourriture, Pizza, Italien, Restaurant"'
        mock_chat.return_value = mock_response

        image_path = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")
        if image_path.exists():
            tags = generate_tags(
                image_path=image_path,
                model="test-model",
                tag_count=4,
                available_tags="Nourriture, Nature, Ville"
            )

            assert "Nourriture" in tags
            assert "Pizza" in tags

    @patch('llm_client.chat')
    def test_generate_tags_prompt_format(self, mock_chat):
        """Test que le prompt est correctement formaté."""
        mock_response = Mock()
        mock_response.message.content = "Tag1, Tag2"
        mock_chat.return_value = mock_response

        image_path = Path("./tests/images/brooke-lark-pGM4sjt_BdQ-unsplash.jpg")
        if image_path.exists():
            available_tags = "Nature, Ville, Personnes"
            tag_count = 8

            generate_tags(
                image_path=image_path,
                model="test-model",
                tag_count=tag_count,
                available_tags=available_tags
            )

            # Vérifier que chat a été appelé avec les bons arguments
            call_args = mock_chat.call_args
            assert call_args[1]['model'] == "test-model"
            assert len(call_args[1]['messages']) == 1

            message = call_args[1]['messages'][0]
            assert 'role' in message
            assert message['role'] == 'user'
            assert 'content' in message
            assert str(tag_count) in message['content']
            assert available_tags in message['content']
            assert 'images' in message
            assert str(image_path) in message['images']
