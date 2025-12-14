# ================================================================
# SETUP MANUEL
# Configuration complète DVC + Git + DagHub
# ================================================================

# ---------------------------------------------------------------
# ÉTAPE 1: Vérification de l'environnement
# ---------------------------------------------------------------

# Vérifier Python 3.11
python3 --version

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer toutes les dépendances
uv pip install -e ".[dev]"

# Vérifier les installations
python -c "import sklearn, pandas, dvc, dagshub; print('✓ All imports successful')"


# ---------------------------------------------------------------
# ÉTAPE 2: Initialisation Git (si pas déjà fait)
# ---------------------------------------------------------------

# Si dépôt non initialisé
git init
git branch -M main

# Ajouter les fichiers de configuration
git add .gitignore pyproject.toml params.yaml
git commit -m "chore: Initial project configuration"


# ---------------------------------------------------------------
# ÉTAPE 3: Initialisation DVC
# ---------------------------------------------------------------

# Initialiser DVC dans le projet
dvc init

# Committer la configuration DVC
git add .dvc .dvcignore
git commit -m "chore: Initialize DVC"


# ---------------------------------------------------------------
# ÉTAPE 4: Configuration DagHub
# ---------------------------------------------------------------

# Remplacez YOUR_USERNAME et YOUR_REPO par vos valeurs
export DAGSHUB_USER="YOUR_USERNAME"
export DAGSHUB_REPO="YOUR_REPO"

# Configurer le remote DVC pour DagHub
dvc remote add -d dagshub https://dagshub.com/${DAGSHUB_USER}/${DAGSHUB_REPO}.dvc

# Configurer l'authentification (local uniquement, pas versionné)
dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user "${DAGSHUB_USER}"

# Entrez votre token DagHub (obtenez-le sur: https://dagshub.com/user/settings/tokens)
read -s DAGSHUB_TOKEN
dvc remote modify dagshub --local password "${DAGSHUB_TOKEN}"

# Committer la configuration du remote
git add .dvc/config
git commit -m "chore: Configure DVC remote with DagHub"


# ---------------------------------------------------------------
# ÉTAPE 5: Configurer le remote Git (DagHub)
# ---------------------------------------------------------------

# Ajouter DagHub comme remote Git
git remote add origin https://dagshub.com/${DAGSHUB_USER}/${DAGSHUB_REPO}.git

# Ou si remote existe déjà, le modifier
git remote set-url origin https://dagshub.com/${DAGSHUB_USER}/${DAGSHUB_REPO}.git

# Vérifier la configuration
git remote -v


# ---------------------------------------------------------------
# ÉTAPE 6: Tracker les données brutes avec DVC
# ---------------------------------------------------------------

# Ajouter votre dataset dans data/raw_data/
# Exemple: cp ~/Downloads/your_data.csv data/raw_data/

# Tracker avec DVC (fichiers volumineux)
dvc add data/raw_data/*.csv

# Committer les fichiers .dvc (légers, dans Git)
git add data/raw_data/*.csv.dvc .gitignore
git commit -m "data: Add raw dataset"

# Pousser les données vers DagHub
dvc push


# ---------------------------------------------------------------
# ÉTAPE 7: Ajouter les scripts Python
# ---------------------------------------------------------------

# Créer la structure de répertoires
mkdir -p src/data src/models metrics

# Ajouter vos scripts (déjà fournis précédemment)
# - src/data/split.py
# - src/models/training.py
# - src/models/evaluate.py

# Committer les scripts
git add src/ params.yaml
git commit -m "feat: Add ML pipeline scripts (Approach A)"


# ---------------------------------------------------------------
# ÉTAPE 8: Exécuter le pipeline complet
# ---------------------------------------------------------------

# Rendre le script exécutable
chmod +x run_pipeline.sh

# Lancer le pipeline
./run_pipeline.sh

# OU exécuter étape par étape:
# ./run_pipeline.sh split
# ./run_pipeline.sh training
# ./run_pipeline.sh evaluate


# ---------------------------------------------------------------
# ÉTAPE 9: Pousser tout vers DagHub
# ---------------------------------------------------------------

# Pousser le code vers Git
git push origin main

# Pousser les données/modèles vers DVC
dvc push


# ---------------------------------------------------------------
# ÉTAPE 10: Vérification finale
# ---------------------------------------------------------------

# Vérifier le statut DVC
dvc status

# Afficher les métriques
cat metrics/scores.json

# Visualiser le pipeline
dvc dag

# Voir l'historique Git
git log --oneline --graph


# ================================================================
# WORKFLOW ITÉRATIF (après le setup initial)
# ================================================================

# 1. Modifier params.yaml avec de nouveaux hyperparamètres

# 2. Ré-exécuter le pipeline
./run_pipeline.sh

# 3. Comparer les résultats
dvc metrics diff

# 4. Si satisfait, pousser les changements
git add params.yaml dvc.lock metrics/scores.json
git commit -m "experiment: Test new hyperparameters"
git push && dvc push


# ================================================================
# COMMANDES UTILES
# ================================================================

# Récupérer les données depuis DagHub
dvc pull

# Afficher les différences de métriques entre commits
dvc metrics diff HEAD~1

# Revenir à une version précédente
git checkout <commit-hash>
dvc checkout

# Lister les expériences
dvc exp list

# Comparer des expériences
dvc exp show --include-params all

# Nettoyer le cache DVC
dvc gc -w -c


# ================================================================
# DÉPANNAGE
# ================================================================

# Si "dvc push" échoue:
# 1. Vérifier les credentials DagHub
dvc remote modify dagshub --local user "YOUR_USERNAME"
dvc remote modify dagshub --local password "YOUR_TOKEN"

# 2. Vérifier la connexion
dvc remote list

# Si conflit Git:
git pull origin main --rebase
git push origin main

# Si problème de dépendances:
uv pip install --upgrade pip
uv pip install -e ".[dev]" --force-reinstall
