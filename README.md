# 🌌 Choucroute Cosmique

**Organisateur d'images intelligent et autonome**

Choucroute Cosmique est un outil qui analyse automatiquement vos photos à l'aide d'un modèle de langage (LLM), génère des tags pertinents, et organise vos images dans une structure de dossiers claire et logique.

## ✨ Fonctionnalités

- 🤖 **Analyse intelligente** : Utilise un LLM local (via Ollama) pour analyser le contenu de vos images
- 🏷️ **Génération de tags** : Crée automatiquement des mots-clés descriptifs en français
- 📁 **Organisation automatique** : Range vos photos dans des dossiers thématiques
- ⚡ **Traitement parallèle** : Analyse plusieurs images simultanément pour plus de rapidité
- 📝 **Métadonnées EXIF** : Ajoute les tags directement dans les métadonnées des images
- 🔒 **Non destructif** : Copie vos images par défaut (option de déplacement disponible)

## 📋 Prérequis

Avant d'installer Choucroute Cosmique, vous devez avoir :

1. **Python 3.8 ou supérieur**
2. **Ollama** (pour exécuter les modèles LLM localement)

---

## 🔧 Installation

### 1. Installer Python

#### Windows
1. Téléchargez Python depuis [python.org](https://www.python.org/downloads/)
2. Lancez l'installateur
3. ⚠️ **IMPORTANT** : Cochez "Add Python to PATH" pendant l'installation
4. Cliquez sur "Install Now"
5. Vérifiez l'installation en ouvrant un terminal (cmd) et tapez :
   ```bash
   python --version
   ```

#### macOS
1. **Option 1 - Via Homebrew (recommandé)** :
   ```bash
   brew install python3
   ```

2. **Option 2 - Via le site officiel** :
   - Téléchargez depuis [python.org](https://www.python.org/downloads/macos/)
   - Installez le package .pkg

3. Vérifiez l'installation :
   ```bash
   python3 --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

Vérifiez l'installation :
```bash
python3 --version
```

---

### 2. Installer Ollama

Ollama permet d'exécuter des modèles d'IA localement sur votre machine.

#### Windows
1. Téléchargez Ollama depuis [ollama.com](https://ollama.com/download)
2. Exécutez l'installateur
3. Ouvrez un terminal et vérifiez :
   ```bash
   ollama --version
   ```

#### macOS
1. Téléchargez depuis [ollama.com](https://ollama.com/download)
2. Installez l'application
3. Vérifiez dans le terminal :
   ```bash
   ollama --version
   ```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Vérifiez l'installation :
```bash
ollama --version
```

---

### 3. Télécharger un modèle LLM

Une fois Ollama installé, téléchargez le modèle par défaut (en ligne de commande) :

```bash
ollama pull gemma3:4b
```

**Note** : Le téléchargement peut prendre quelques minutes (environ 2-3 GB).

Modèles recommandés selon votre machine :
- `gemma3:4b` - Rapide, nécessite ~4 GB de RAM (recommandé, par défaut)
- `llama3.2-vision:11b` - Plus précis, nécessite ~8 GB de RAM
- `llava:7b` - Bon compromis, nécessite ~6 GB de RAM

---

### 4. Installer Choucroute Cosmique

#### Téléchargement manuel

1. Téléchargez le code source depuis GitHub (Bouton vert "Code" > "Téléchager ZIP")
2. Décompressez l'archive
3. Ouvrez un terminal dans le dossier décompressé

---

### 5. Créer un environnement virtuel Python

C'est une bonne pratique pour isoler les dépendances du projet.

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.

---

### 6. Installer les dépendances

Avec l'environnement virtuel activé :

```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### Utilisation basique

La commande la plus simple pour organiser vos photos :

```bash
python run.py /chemin/vers/vos/photos
```

Cette commande va :
1. Analyser toutes les images dans le dossier spécifié
2. Générer 8 tags par image
3. Copier les images organisées dans `./choucroute-cosmique/`

### Structure de sortie

Les images sont organisées de cette manière :

```
choucroute-cosmique/
├── Personnes/
│   ├── vacances_2024_Groupe_Amis_Plage_Été_Soleil.jpg
│   └── mariage_Famille_Cérémonie_Église_Bonheur.jpg
├── Nature/
│   ├── foret_Arbres_Automne_Feuilles_Paysage.jpg
│   └── montagne_Sommet_Neige_Panorama_Altitude.jpg
└── Nourriture/
    └── restaurant_Pizza_Italien_Repas_Dîner.jpg
```

- Le **premier tag** détermine le dossier (catégorie principale)
- Les **tags suivants** sont ajoutés au nom du fichier
- Le **nom original** est conservé au début

---

## ⚙️ Options avancées

### Afficher l'aide

```bash
python run.py --help
```

### Options disponibles

| Option | Description | Valeur par défaut |
|--------|-------------|-------------------|
| `directory` | Dossier contenant vos images (obligatoire) | - |
| `--model` | Modèle LLM à utiliser | `gemma3:4b` |
| `--tagcount` | Nombre de tags à générer par image | `8` |
| `--outdir` | Dossier de destination | `choucroute-cosmique` |
| `--max-parallel` | Nombre d'images traitées en parallèle | `4` |
| `--move` | Déplacer au lieu de copier les images | `False` |

---

## 📚 Exemples d'utilisation

### Exemple 1 : Organisation simple
```bash
python run.py ./mes-photos
```
Analyse toutes les photos dans `./mes-photos` et les organise dans `./choucroute-cosmique/`

### Exemple 2 : Changer le dossier de sortie
```bash
python run.py ./vacances-2024 --outdir ./vacances-organisees
```

### Exemple 3 : Utiliser un modèle différent
```bash
python run.py ./photos --model llava:7b
```

### Exemple 4 : Générer plus de tags
```bash
python run.py ./photos --tagcount 12
```

### Exemple 5 : Traitement plus rapide (plus de parallélisme)
```bash
python run.py ./photos --max-parallel 8
```

### Exemple 6 : Déplacer au lieu de copier
```bash
python run.py ./photos --move
```
⚠️ **Attention** : Cette option déplace vos fichiers originaux !

### Exemple 7 : Configuration complète
```bash
python run.py ./mes-vacances \
  --outdir ./vacances-triees \
  --model gemma3:4b \
  --tagcount 10 \
  --max-parallel 6
```

---

## 📝 Configuration des catégories

Le fichier `tags.txt` contient les catégories principales. Le premier tag généré par le LLM sera **toujours** choisi dans cette liste.

Vous pouvez modifier ce fichier pour adapter les catégories à vos besoins :

```
Personnes
Selfie
Mariage
Anniversaire
Vacances
Nature
Animaux
Nourriture
Ville
...
```

---

## 🐛 Dépannage

### Problème : "ModuleNotFoundError: No module named 'ollama'"

**Solution** : Assurez-vous que l'environnement virtuel est activé et installez les dépendances :
```bash
pip install -r requirements.txt
```

---

### Problème : "Connection refused" ou "Ollama not running"

**Solution** : Vérifiez qu'Ollama est bien lancé :

#### Windows
Ollama devrait démarrer automatiquement. Vérifiez dans la barre des tâches.

#### macOS
Lancez l'application Ollama depuis le Launchpad.

#### Linux
```bash
systemctl start ollama
# ou
ollama serve
```

---

### Problème : "Model 'gemma3:4b' not found"

**Solution** : Téléchargez le modèle :
```bash
ollama pull gemma3:4b
```

---

### Problème : Traitement très lent

**Solutions** :
1. Réduisez `--max-parallel` si votre machine a peu de RAM :
   ```bash
   python run.py ./photos --max-parallel 2
   ```

2. Utilisez un modèle plus petit :
   ```bash
   python run.py ./photos --model gemma3:4b
   ```

3. Vérifiez que votre GPU est bien utilisé (si disponible)

---

### Problème : "Permission denied" sous Linux/macOS

**Solution** : Vérifiez les permissions du dossier :
```bash
chmod +x run.py
```

Ou exécutez avec Python explicitement :
```bash
python3 run.py ./photos
```

---

## 🏗️ Architecture du projet

```
choucroute-cosmique/
├── run.py                  # Point d'entrée principal
├── image_scanner.py        # Scan des images dans un dossier
├── llm_client.py          # Interaction avec le LLM
├── parallel_processor.py   # Traitement parallèle
├── file_operations.py      # Gestion des fichiers
├── exif_tagger.py         # Ajout de métadonnées EXIF
├── tags.txt               # Liste des catégories principales
├── requirements.txt        # Dépendances Python
└── README.md              # Ce fichier
```

---

## 📊 Formats d'images supportés

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- BMP (`.bmp`)
- WebP (`.webp`)
- TIFF (`.tiff`, `.tif`)

---

## 📜 Licence

MIT

---

## 🙏 Remerciements

- [Ollama](https://ollama.com) pour l'infrastructure LLM locale
- [Pillow](https://pypi.org/project/pillow/) pour la manipulation d'images
- [piexif](https://pypi.org/project/piexif/) pour la gestion des métadonnées EXIF

---

## ❓ FAQ

### Puis-je utiliser Choucroute Cosmique sans connexion Internet ?

Oui ! Une fois Ollama et le modèle LLM installés, tout fonctionne localement sur votre machine.

### Mes photos originales sont-elles modifiées ?

Non, par défaut l'application **copie** vos images. Les originaux restent intacts. Utilisez `--move` seulement si vous voulez déplacer les fichiers.

### Puis-je annuler l'organisation ?

Si vous avez utilisé l'option par défaut (copie), vos photos originales sont toujours dans le dossier source. Supprimez simplement le dossier de sortie.

### Combien de temps prend le traitement ?

Cela dépend de :
- Nombre d'images
- Modèle LLM utilisé
- Puissance de votre machine
- Paramètre `--max-parallel`

En moyenne : compter 3 minutes pour 100 images sur une machine relativement récente avec une carte graphique.

### Les tags sont en quelle langue ?

Les tags sont générés en **français** par défaut. Vous pouvez modifier le prompt dans `llm_client.py` pour changer la langue.

---

```
Sur le velours noir du vide, piqué d'étoiles-moutarde.

Chou-nébuleuse, fermenté au laser supernova. Baies-trous noirs, silence poivré.
Lunes de méthane tièdes.

Saucisses-comètes fumées à l'hélium 3. Le jus : une acidité primordiale.

Le confort d'un plat d'hiver et le vertige absolu de l'infini.
```