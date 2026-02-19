#!/bin/bash
set -e

# Répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activer l'environnement virtuel
source .python_env/bin/activate

# Exécuter le pipeline complet
echo "=================================================="
echo "SAFRAN Fairy - Démarrage du pipeline"
echo "Date : $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="

python main.py --all

echo "=================================================="
echo "Pipeline terminé avec succès"
echo "Date : $(date '+%Y-%m-%d %H:%M:%S')"
echo "=================================================="
