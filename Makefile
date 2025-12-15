# Makefile Examen MLOps DVC avec uv
# Utilisation : make init USER=pseudo REPO=projet TOKEN=xyz

DAGSHUB_USER ?= user_placeholder
REPO_NAME ?= repo_placeholder
DAGSHUB_TOKEN ?= token_placeholder

# Couleurs
GREEN = \033[0;32m
BLUE = \033[0;34m
RED = \033[0;31m
NC = \033[0m

.PHONY: help all init run save clean reset check

help: ## Affiche l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "${BLUE}%-15s${NC} %s\n", $$1, $$2}'

all: ## Cycle complet : Reset -> Init -> Run -> Save
	@echo "${BLUE}=== DÉMARRAGE DU CYCLE COMPLET ===${NC}"
	$(MAKE) reset
	$(MAKE) init
	$(MAKE) run
	$(MAKE) save
	@echo "${GREEN}✅ CYCLE COMPLET TERMINÉ AVEC SUCCÈS${NC}"

reset: ## ⚠️  HARD RESET (Supprime env, dvc config, data générée)
	@echo "${RED}=== HARD RESET ===${NC}"
	rm -rf .venv .dvc
	rm -f dvc.lock
	# On garde dvc.yaml !
	rm -rf data/processed_data/* models/* metrics/*
	rm -f data/raw_data/*.dvc
	@echo "Projet nettoyé."

init: ## Init complet (Deps, DVC, Remote) + Double Vérification
	@echo "${BLUE}=== Initialisation ===${NC}"
	
	# 1. Dépendances
	uv sync
	
	# 2. DVC Init
	@if [ ! -d ".dvc" ]; then uv run dvc init; fi

	# 3. Config Remote DVC (S3)
	@echo "Configuration DVC Remote..."
	uv run dvc remote add -f origin s3://dvc
	uv run dvc remote default origin
	uv run dvc remote modify origin endpointurl https://dagshub.com/$(DAGSHUB_USER)/$(REPO_NAME).s3
	uv run dvc remote modify origin --local access_key_id $(DAGSHUB_TOKEN)
	uv run dvc remote modify origin --local secret_access_key $(DAGSHUB_TOKEN)
	
	# 4. Tracking Raw Data
	@if [ -f "data/raw_data/raw.csv" ] && [ ! -f "data/raw_data/raw.csv.dvc" ]; then \
		echo "Tracking raw.csv..."; \
		uv run dvc add data/raw_data/raw.csv; \
	fi
	
	# 5. Vérifications finales
	@$(MAKE) check
	
	@echo "${GREEN}Projet prêt !${NC}"

check: ## Vérifie la connexion DVC (S3) ET Git (HTTPS/SSH)
	@echo "${BLUE}--- Test des connexions ---${NC}"
	
	# Test DVC
	@echo -n "Test connexion DVC (S3)... "
	@if uv run dvc status -r origin >/dev/null 2>&1; then \
		echo "${GREEN}OK${NC}"; \
	else \
		echo "${RED}ECHEC${NC}"; \
		echo "Vérifiez votre TOKEN et l'URL DagsHub."; \
		exit 1; \
	fi

	# Test Git
	@echo -n "Test connexion Git (Push Access)... "
	@if git ls-remote --heads origin >/dev/null 2>&1; then \
		echo "${GREEN}OK${NC}"; \
	else \
		echo "${RED}ECHEC${NC}"; \
		echo "Vérifiez vos clés SSH ou vos credentials Git."; \
		exit 1; \
	fi
	
	@echo "${GREEN}✅ Tous les voyants sont au vert.${NC}"

run: ## Lance le Pipeline DVC complet
	@echo "${BLUE}=== Lancement du Pipeline ===${NC}"
	uv run dvc repro
	@echo "${GREEN}Pipeline terminé.${NC}"
	@if [ -f "metrics/scores.json" ]; then cat metrics/scores.json; fi

save: ## Sauvegarde Git + Push Data/Code
	@echo "${BLUE}=== Sauvegarde Complète ===${NC}"
	
	# Pré-check
	@$(MAKE) check
	
	git add .
	-git commit -m "Pipeline run: $(shell date '+%Y-%m-%d %H:%M')"
	
	@echo "${BLUE}Push Data (DVC)...${NC}"
	uv run dvc push
	
	@echo "${BLUE}Push Code (Git)...${NC}"
	git push
	@echo "${GREEN}Projet synchronisé !${NC}"

clean: ## Nettoyage des fichiers générés
	rm -rf data/processed_data/* data/predictions.csv models/* metrics/*
	@echo "${GREEN}Nettoyé.${NC}"
