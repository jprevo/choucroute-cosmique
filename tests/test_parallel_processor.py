"""Tests pour le module parallel_processor."""

import pytest
from pathlib import Path
import time
from parallel_processor import process_images_parallel, ImageTagResult


class TestImageTagResult:
    """Tests pour la classe ImageTagResult."""

    def test_image_tag_result_success(self):
        """Test la création d'un résultat réussi."""
        result = ImageTagResult(
            image_path=Path("test.jpg"),
            tags=["Tag1", "Tag2"],
            success=True
        )

        assert result.image_path == Path("test.jpg")
        assert result.tags == ["Tag1", "Tag2"]
        assert result.success is True
        assert result.error == ""

    def test_image_tag_result_failure(self):
        """Test la création d'un résultat échoué."""
        result = ImageTagResult(
            image_path=Path("test.jpg"),
            tags=[],
            success=False,
            error="Erreur de test"
        )

        assert result.image_path == Path("test.jpg")
        assert result.tags == []
        assert result.success is False
        assert result.error == "Erreur de test"


class TestProcessImagesParallel:
    """Tests pour la fonction process_images_parallel."""

    def dummy_processing_function(self, image_path: Path):
        """Fonction de traitement factice pour les tests."""
        # Simuler un traitement qui retourne des tags basés sur le nom
        return [f"tag_{image_path.stem}", "general", "test"]

    def slow_processing_function(self, image_path: Path):
        """Fonction de traitement lente pour tester le parallélisme."""
        time.sleep(0.1)
        return ["slow", "tag"]

    def failing_processing_function(self, image_path: Path):
        """Fonction de traitement qui échoue."""
        raise ValueError("Erreur de traitement intentionnelle")

    def test_process_single_image(self):
        """Test le traitement d'une seule image."""
        images = [Path("image1.jpg")]

        results = process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=1
        )

        assert len(results) == 1
        assert results[0].success is True
        assert len(results[0].tags) > 0
        assert results[0].image_path == Path("image1.jpg")

    def test_process_multiple_images(self):
        """Test le traitement de plusieurs images."""
        images = [Path(f"image{i}.jpg") for i in range(5)]

        results = process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=2
        )

        assert len(results) == 5
        assert all(r.success for r in results)
        assert all(len(r.tags) > 0 for r in results)

    def test_process_empty_list(self):
        """Test le traitement d'une liste vide."""
        images = []

        results = process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=2
        )

        assert len(results) == 0

    def test_process_with_errors(self):
        """Test le traitement quand certaines images échouent."""
        images = [Path(f"image{i}.jpg") for i in range(3)]

        results = process_images_parallel(
            images,
            self.failing_processing_function,
            max_workers=2
        )

        assert len(results) == 3
        assert all(not r.success for r in results)
        assert all(r.error != "" for r in results)
        assert all("Erreur de traitement intentionnelle" in r.error for r in results)

    def test_process_with_progress_callback(self):
        """Test le callback de progression."""
        images = [Path(f"image{i}.jpg") for i in range(5)]
        progress_calls = []

        def progress_callback(completed, total):
            progress_calls.append((completed, total))

        results = process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=2,
            progress_callback=progress_callback
        )

        # Le callback devrait avoir été appelé 5 fois (une fois par image)
        assert len(progress_calls) == 5

        # Vérifier que le total est toujours 5
        assert all(total == 5 for completed, total in progress_calls)

        # Vérifier que completed va de 1 à 5
        completed_values = sorted([completed for completed, total in progress_calls])
        assert completed_values == [1, 2, 3, 4, 5]

    def test_process_with_different_worker_counts(self):
        """Test avec différents nombres de workers."""
        images = [Path(f"image{i}.jpg") for i in range(10)]

        # Test avec 1 worker
        results_1 = process_images_parallel(images, self.dummy_processing_function, max_workers=1)
        assert len(results_1) == 10

        # Test avec 4 workers
        results_4 = process_images_parallel(images, self.dummy_processing_function, max_workers=4)
        assert len(results_4) == 10

        # Test avec 8 workers
        results_8 = process_images_parallel(images, self.dummy_processing_function, max_workers=8)
        assert len(results_8) == 10

    def test_parallel_processing_is_faster(self):
        """Test que le traitement parallèle est plus rapide."""
        images = [Path(f"image{i}.jpg") for i in range(4)]

        # Traitement séquentiel (1 worker)
        start_time = time.time()
        process_images_parallel(images, self.slow_processing_function, max_workers=1)
        sequential_time = time.time() - start_time

        # Traitement parallèle (4 workers)
        start_time = time.time()
        process_images_parallel(images, self.slow_processing_function, max_workers=4)
        parallel_time = time.time() - start_time

        # Le traitement parallèle devrait être plus rapide
        # (avec une marge pour tenir compte de l'overhead)
        assert parallel_time < sequential_time * 0.8

    def test_process_preserves_image_paths(self):
        """Test que les chemins d'images sont préservés dans les résultats."""
        images = [Path(f"dir{i}/image{i}.jpg") for i in range(3)]

        results = process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=2
        )

        result_paths = {r.image_path for r in results}
        assert result_paths == set(images)

    def test_process_with_mixed_success_failure(self):
        """Test le traitement avec un mélange de succès et d'échecs."""
        images = [Path(f"image{i}.jpg") for i in range(5)]
        processed_count = [0]

        def mixed_processing_function(image_path: Path):
            processed_count[0] += 1
            # Faire échouer les images paires
            if int(image_path.stem[-1]) % 2 == 0:
                raise ValueError("Échec pour image paire")
            return ["success", "tag"]

        results = process_images_parallel(
            images,
            mixed_processing_function,
            max_workers=2
        )

        assert len(results) == 5
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        # Images 1, 3 devraient réussir (indices 1, 3)
        # Images 0, 2, 4 devraient échouer (indices 0, 2, 4)
        assert len(successful) == 2
        assert len(failed) == 3

    def test_process_returns_all_results(self):
        """Test que tous les résultats sont retournés même en cas d'erreur."""
        images = [Path(f"image{i}.jpg") for i in range(10)]

        results = process_images_parallel(
            images,
            self.failing_processing_function,
            max_workers=3
        )

        # Tous les résultats devraient être retournés
        assert len(results) == 10

    def test_process_with_real_test_images(self):
        """Test le traitement avec de vraies images de test."""
        from image_scanner import scan_images

        try:
            images = scan_images("./tests/images")
            if not images:
                pytest.skip("Aucune image de test trouvée")

            results = process_images_parallel(
                images[:3],  # Limiter à 3 images pour la vitesse
                self.dummy_processing_function,
                max_workers=2
            )

            assert len(results) <= 3
            assert all(isinstance(r, ImageTagResult) for r in results)
        except (FileNotFoundError, NotADirectoryError):
            pytest.skip("Répertoire d'images de test non disponible")

    def test_progress_callback_receives_correct_total(self):
        """Test que le callback de progression reçoit le bon total."""
        images = [Path(f"image{i}.jpg") for i in range(7)]
        totals = []

        def progress_callback(completed, total):
            totals.append(total)

        process_images_parallel(
            images,
            self.dummy_processing_function,
            max_workers=3,
            progress_callback=progress_callback
        )

        # Tous les totaux devraient être 7
        assert all(t == 7 for t in totals)

    def test_tags_are_properly_returned(self):
        """Test que les tags sont correctement retournés."""
        images = [Path("test.jpg")]

        def tag_function(image_path):
            return ["Tag1", "Tag2", "Tag3"]

        results = process_images_parallel(images, tag_function, max_workers=1)

        assert results[0].tags == ["Tag1", "Tag2", "Tag3"]

    def test_error_message_captured(self):
        """Test que le message d'erreur est capturé."""
        images = [Path("test.jpg")]

        def error_function(image_path):
            raise RuntimeError("Message d'erreur spécifique")

        results = process_images_parallel(images, error_function, max_workers=1)

        assert not results[0].success
        assert "Message d'erreur spécifique" in results[0].error
