# 1. Activer l'environnement
source .venv/bin/activate

# 2. Installer les dépendances
uv pip install -e ".[dev]"

# 3. Initialiser DVC
dvc init
git add .dvc .dvcignore
git commit -m "chore: Initialize DVC"

# 4. Configurer DagHub
dvc remote add -d dagshub https://dagshub.com/adx.h2s/examen-dvc.dvc
dvc remote modify dagshub --local auth basic
dvc remote modify dagshub --local user "adx.h2s"
dvc remote modify dagshub --local password "8c8eb86114934fe30e6eeb0fb20cfd6fca9d3dbd"

# 5. Tracker les données brutes
dvc add data/raw_data/*.csv
git add data/raw_data/*.csv.dvc .gitignore
git commit -m "data: Add raw dataset"

# 6. Lancer le pipeline
chmod +x run_pipeline.sh
./run_pipeline.sh

# 7. Pousser vers DagHub
git push origin main
dvc push
