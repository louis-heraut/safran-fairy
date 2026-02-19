# SAFRAN Fairy

Pipeline automatisé de téléchargement, traitement et publication des données SAFRAN-ISBA-MODCOU (SIM2) au format NetCDF pour chaque variable disponible pour l'ensemble de la période de réanalyse depuis [meteo.data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-changement-climatique-sim-quotidienne) vers [https://entrepot.recherche.data.gouv.fr](https://doi.org/10.57745/BAZ12C).


## Vue d'ensemble
Ce projet automatise :
1. **Téléchargement** des fichiers CSV depuis l'API Météo-France
2. **Décompression** des archives `.csv.gz`
3. **Découpage** par variable climatique
4. **Conversion** en NetCDF avec métadonnées CF-compliant
5. **Fusion** temporelle (historical/previous/latest)
6. **Publication** sur un dépôt de l'entrepôt Recherche Data Gouv.


## Structure des données
```
00_SAFRAN-data_download/     # Fichiers .csv.gz bruts téléchargés
01_SAFRAN-data_raw/          # Fichiers .csv décompressés
02_SAFRAN-data_split/        # Fichiers .parquet par variable
03_SAFRAN-data_convert/      # Fichiers .nc individuels
04_SAFRAN-data_output/       # Fichiers .nc fusionnés (historical/previous/latest)
```


## Architecture
```
safran_fairy/
├── download.py      # Téléchargement depuis meteo.data.gouv.fr
├── decompress.py    # Extraction des .csv.gz
├── split.py         # Découpage par variable
├── convert.py       # Conversion CSV → NetCDF
├── merge.py         # Fusion temporelle
├── upload.py        # Publication Dataverse
└── clean.py         # Nettoyage des anciennes versions
```

## Installation rapide

### Prérequis
- Python 3.10+
- NCO (NetCDF Operators) : `sudo apt install nco`

### Installation
```bash
# Cloner le dépôt
git clone <repo_url>
cd safran-fairy

# Installation automatique
make install
```

Voir [INSTALL.md](INSTALL.md) pour l'installation détaillée sur serveur Linux.


## Utilisation

### Exécution manuelle
```bash
# Pipeline complet
make run

# Étapes individuelles
make download    # Télécharger les nouvelles données
make process     # Traiter (décompresser, découper, convertir, fusionner)
make upload      # Publier sur Dataverse
make clean-old   # Nettoyer les anciennes versions
```

### Service systemd (production)
```bash
# Installation du service
sudo make install-service

# Vérifier le statut
sudo systemctl status safran-sync.timer
sudo journalctl -u safran-sync.service -f
```

Le service s'exécute quotidiennement à 02:00 UTC.


## Variables disponibles
26 variables climatiques quotidiennes sur grille Lambert II étendu (8 km) :

| Variable | Description | Unité |
|----------|-------------|-------|
| `PRENEI` | Précipitations solides | mm |
| `PRELIQ` | Précipitations liquides | mm |
| `T` | Température moyenne | °C |
| `TINF_H` | Température minimale | °C |
| `TSUP_H` | Température maximale | °C |
| `FF` | Vent moyen | m/s |
| `HU` | Humidité relative | % |
| ... | ... | ... |

Voir `resources/safran_variables.csv` pour la liste complète.


## Monitoring
```bash
# Logs en temps réel
make logs

# Statut du service
make status

# Dernière exécution
make last-run
```


## Développement
```bash
# Environnement virtuel
python -m venv .python_env
source .python_env/bin/activate
pip install -r requirements.txt
```


## Licence
Voir [LICENSE](LICENSE)


## Contact
Maintenu par Lou Heraut - INRAE
