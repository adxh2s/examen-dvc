# Makefile Examen MLOps
# Utilisation : make init USER=... REPO=... TOKEN=...

DAGSHUB_USER ?= adx.h2s
REPO_NAME ?= adxh2s
DAGSHUB_TOKEN ?= 8c8eb86114934fe30e6eeb0fb20cfd6fca9d3dbd

.PHONY: help init run save clean reset

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

reset: ## ⚠️  DANGER : Supprime tout (.venv, .dvc, lock, data générée) pour repartir de zéro
	@echo "\033[31m=== HARD RESET ===\033[0m"
	rm -rf .venv
	rm -rf .dvc
	rm -f dvc.lock
	rm -rf data/processed_data/*
	rm -rf models/*
	rm -rf metrics/*
	# On garde raw.csv s'il est là, mais on supprime le tracking dvc associé pour le refaire
	rm -f data/raw_data/*.dvc
	@echo "Projet nettoyé. Lancez 'make init' pour recommencer."

init: ## Installe l'environnement et configure DVC (Idempotent)
	@echo "\033[34m=== Initialisation ===\033[0m"
	
	# 1. Python Venv avec uv
	uv sync
	
	# 2. DVC Init (si pas fait)
	@if [ ! -d ".dvc" ]; then \
		echo "Initialisation DVC..."; \
		uv run dvc init; \
	fi

	# 3. Config Dagshub (Force la mise à jour)
	uv run dvc remote add -f origin s3://dvc
	uv run dvc remote modify origin endpointurl https://dagshub.com/$(DAGSHUB_USER)/$(REPO_NAME).s3
	uv run dvc remote modify origin --local access_key_id $(DAGSHUB_TOKEN)
	uv run dvc remote modify origin --local secret_access_key $(DAGSHUB_TOKEN)
	
	# 4. Tracking du fichier Raw (Spécifique pour le démarrage)
	@if [ -f "data/raw_data/raw.csv" ] && [ ! -f "data/raw_data/raw.csv.dvc" ]; then \
		echo "Tracking du fichier raw.csv..."; \
		uv run dvc add data/raw_data/raw.csv; \
	fi
	
	@echo "\033[32mPrêt à travailler.\033[0m"

run: ## Lance le pipeline (dvc repro)
	uv run dvc repro

save: ## Git push + DVC push
	git add .
	-git commit -m "Save pipeline $(shell date +%F_%H-%M)"
	uv run dvc push
	git push
