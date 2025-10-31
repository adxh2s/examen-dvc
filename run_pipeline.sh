#!/bin/bash

# ================================================================
# ML Pipeline Execution Script with DVC/Git/DagHub Integration
# ================================================================
# This script runs the complete ML pipeline (Approach A) and
# handles versioning at each stage with DVC and Git.
#
# Usage:
#   ./run_pipeline.sh [--stage STAGE_NAME]
#
# Stages:
#   all       - Run complete pipeline (default)
#   split     - Run only data split
#   training  - Run only training (requires split)
#   evaluate  - Run only evaluation (requires training)
# ================================================================

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Configuration
readonly PROJECT_NAME="ml-pipeline-dvc-dagshub"
readonly PYTHON_VERSION="3.11"

# Parse arguments
STAGE="${1:-all}"

# ================================================================
# Helper Functions
# ================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

section_header() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  $1${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# ================================================================
# Pre-flight Checks
# ================================================================

preflight_checks() {
    section_header "Pre-flight Checks"
    
    log_info "Checking required tools..."
    check_command "python3"
    check_command "git"
    check_command "dvc"
    
    # Check Python version
    PYTHON_INSTALLED=$(python3 --version | awk '{print $2}')
    log_info "Python version: $PYTHON_INSTALLED"
    
    # Check if virtual environment is activated
    if [[ -z "${VIRTUAL_ENV}" ]]; then
        log_warning "Virtual environment not activated!"
        log_info "Activating .venv..."
        source .venv/bin/activate || {
            log_error "Failed to activate virtual environment"
            exit 1
        }
    fi
    
    # Check if raw data exists
    if [ ! "$(ls -A data/raw_data/*.csv 2>/dev/null)" ]; then
        log_error "No CSV files found in data/raw_data/"
        log_info "Please add your dataset to data/raw_data/ before running the pipeline"
        exit 1
    fi
    
    log_success "All checks passed!"
}

# ================================================================
# DVC/Git Helper Functions
# ================================================================

git_commit_stage() {
    local stage=$1
    local message=$2
    
    log_info "Committing changes for stage: $stage"
    git add dvc.lock params.yaml src/ 2>/dev/null || true
    
    if [ -n "$(git status --porcelain)" ]; then
        git commit -m "$message" || log_warning "Nothing new to commit"
    else
        log_info "No changes to commit"
    fi
}

push_to_remote() {
    log_info "Pushing to remote repositories..."
    
    # Push to Git
    log_info "Pushing code to Git..."
    git push origin master || git push origin main || log_warning "Git push failed (may need to set up remote)"
    
    # Push to DVC/DagHub
    log_info "Pushing data and models to DVC remote..."
    dvc push || log_warning "DVC push failed (check remote configuration)"
    
    log_success "Push completed!"
}

# ================================================================
# Pipeline Stages
# ================================================================

stage_split() {
    section_header "Stage 1: Data Split"
    
    log_info "Running data split script..."
    python src/data/split.py
    
    log_success "Data split completed!"
    
    # Note: Les outputs sont automatiquement trackés par DVC via dvc.yaml
    # Pas besoin de dvc add manuel ici
    log_info "Outputs tracked automatically by DVC pipeline (dvc.yaml)"
    
    # Commit changes
    git_commit_stage "split" "feat: Run data split stage"
    
    log_success "Stage 1 completed and versioned!"
}

stage_training() {
    section_header "Stage 2: Model Training"
    
    # Check dependencies
    if [ ! -d "data/processed_data" ]; then
        log_error "Processed data not found. Run stage 'split' first."
        exit 1
    fi
    
    log_info "Running model training with GridSearchCV..."
    python src/models/training.py
    
    log_success "Model training completed!"
    
    # Note: Les modèles sont automatiquement trackés par DVC via dvc.yaml
    log_info "Models tracked automatically by DVC pipeline (dvc.yaml)"
    
    # Commit changes
    git_commit_stage "training" "feat: Train models with GridSearchCV"
    
    log_success "Stage 2 completed and versioned!"
}

stage_evaluate() {
    section_header "Stage 3: Model Evaluation"
    
    # Check dependencies
    if [ ! -d "models" ] || [ ! -f "models/best_pipeline.pkl" ]; then
        log_error "Trained model not found. Run stage 'training' first."
        exit 1
    fi
    
    log_info "Running model evaluation..."
    python src/models/evaluate.py
    
    log_success "Model evaluation completed!"
    
    # Note: Les prédictions sont automatiquement trackées par DVC via dvc.yaml
    log_info "Predictions tracked automatically by DVC pipeline (dvc.yaml)"
    
    # Metrics are tracked by Git (not DVC)
    log_info "Adding metrics to Git..."
    git add metrics/scores.json 2>/dev/null || true
    
    # Commit changes
    git_commit_stage "evaluate" "feat: Evaluate model and generate predictions"
    
    # Display metrics
    if [ -f "metrics/scores.json" ]; then
        echo ""
        log_info "📊 Evaluation Metrics:"
        cat metrics/scores.json
        echo ""
    fi
    
    log_success "Stage 3 completed and versioned!"
}

# ================================================================
# Main Pipeline Execution
# ================================================================

run_complete_pipeline() {
    section_header "Running Complete ML Pipeline"
    
    preflight_checks
    
    log_info "Pipeline stages: split → training → evaluate"
    
    # Run all stages
    stage_split
    stage_training
    stage_evaluate
    
    section_header "Pipeline Execution Summary"
    
    echo -e "${GREEN}✓${NC} Data split completed"
    echo -e "${GREEN}✓${NC} Model training completed"
    echo -e "${GREEN}✓${NC} Model evaluation completed"
    echo ""
    
    # Show DVC pipeline status
    log_info "DVC Pipeline Status:"
    dvc status
    
    # Ask for push
    echo ""
    read -p "$(echo -e ${YELLOW}Push to remote repositories? [y/N]:${NC} )" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_to_remote
    else
        log_info "Skipping push. Run 'git push && dvc push' manually when ready."
    fi
    
    section_header "Pipeline Completed Successfully! 🎉"
    
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Review metrics in metrics/scores.json"
    echo "  2. Check predictions in data/predictions.csv"
    echo "  3. View pipeline on DagHub dashboard"
    echo "  4. Experiment with different parameters in params.yaml"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  dvc dag              - Visualize pipeline DAG"
    echo "  dvc metrics show     - Display metrics"
    echo "  git log --oneline    - View commit history"
    echo "  dvc repro            - Reproduce pipeline from dvc.yaml"
    echo ""
}

# ================================================================
# Script Entry Point
# ================================================================

main() {
    case "$STAGE" in
        all)
            run_complete_pipeline
            ;;
        split)
            preflight_checks
            stage_split
            ;;
        training)
            preflight_checks
            stage_training
            ;;
        evaluate)
            preflight_checks
            stage_evaluate
            ;;
        *)
            log_error "Unknown stage: $STAGE"
            echo "Usage: $0 [all|split|training|evaluate]"
            exit 1
            ;;
    esac
}

# Run main function
main
