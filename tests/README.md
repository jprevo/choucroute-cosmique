# Tests pour Choucroute Cosmique

Ce répertoire contient une suite de tests complète pour le projet Choucroute Cosmique.

## Structure des tests

- `test_image_scanner.py` : Tests pour le scanning d'images
- `test_llm_client.py` : Tests pour le client LLM et le parsing de tags
- `test_file_operations.py` : Tests pour les opérations de fichiers (copie, déplacement, organisation)
- `test_exif_tagger.py` : Tests pour l'ajout et la lecture de métadonnées EXIF
- `test_parallel_processor.py` : Tests pour le traitement parallèle
- `test_integration.py` : Tests d'intégration end-to-end

Merci à https://unsplash.com/ pour les images de test.

## Installation des dépendances de test

```bash
pip install -r requirements.txt
```

Cela installera pytest et pytest-cov nécessaires pour les tests.

## Exécution des tests

### Tous les tests

```bash
pytest
```

### Tests spécifiques

```bash
# Un fichier de test
pytest tests/test_image_scanner.py

# Une classe de test
pytest tests/test_image_scanner.py::TestScanImages

# Un test individuel
pytest tests/test_image_scanner.py::TestScanImages::test_scan_images_with_real_images
```

### Tests avec verbosité

```bash
pytest -v
```

### Tests avec couverture de code

```bash
pytest --cov=. --cov-report=html
```

Le rapport HTML sera généré dans le répertoire `htmlcov/`.

### Tests rapides (sans les tests lents)

```bash
pytest -m "not slow"
```

## Organisation des tests

### Tests unitaires

La plupart des tests sont des tests unitaires qui testent des fonctions individuelles de manière isolée.

### Tests d'intégration

Les tests dans `test_integration.py` testent le système complet avec plusieurs composants travaillant ensemble.

### Fixtures

Les tests utilisent des fixtures pytest pour :
- Créer des répertoires temporaires
- Générer des images de test
- Mocker les appels LLM

## Images de test

Le répertoire `tests/images/` contient des images réelles utilisées pour les tests. Ces images sont utilisées pour :
- Tester le scanning de fichiers
- Tester l'ajout de métadonnées EXIF
- Tester l'organisation de fichiers
- Tests d'intégration

## Mocking

Les tests qui nécessitent Ollama utilisent le mocking (`unittest.mock`) pour simuler les réponses du LLM, permettant aux tests de s'exécuter sans avoir besoin d'Ollama en cours d'exécution.

## Coverage

Pour voir un rapport de couverture de code détaillé :

```bash
pytest --cov=. --cov-report=term-missing
```

Pour générer un rapport HTML :

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Conseils

1. Exécutez les tests fréquemment pendant le développement
2. Visez une couverture de code élevée (>80%)
3. Ajoutez des tests pour chaque nouveau bug corrigé
4. Gardez les tests rapides et isolés
5. Utilisez des fixtures pour éviter la duplication de code

## Résolution de problèmes

### Erreur : "PIL/Pillow non disponible"

Installez Pillow :
```bash
pip install Pillow piexif
```

### Erreur : "Aucune image de test trouvée"

Assurez-vous que le répertoire `tests/images/` contient des images.

### Tests qui échouent de manière intermittente

Certains tests de parallélisme peuvent être sensibles au timing. Si un test échoue de manière intermittente, vérifiez les tests marqués `slow`.
