# Installation


## Installation sur serveur Linux
### 1. Prérequis système
```bash
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Dépendances système
sudo apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    nco \
    git
```

### 2. Installation du projet
```bash
# Créer le répertoire d'installation
sudo mkdir -p /opt/safran-fairy
sudo chown $USER:$USER /opt/safran-fairy

# Cloner le projet
cd /opt/safran-fairy
git clone https://github.com/louis-heraut/safran-fairy.git .

# Installer les dépendances Python
make install
```

### 3. Configuration
```bash
# Copier et éditer le fichier d'environnement
cp env.dist .env
nano .env
```

Remplir avec vos identifiants :
```ini
# API Dataverse
RDG_API_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 4. Test manuel
```bash
# Tester le pipeline complet
make run

# Vérifier les logs
ls -lh 04_SAFRAN-data_output/
```

### 5. Installation du service systemd
```bash
# Installer le service et le timer
sudo make install-service

# Activer le service
sudo systemctl enable safran-sync.timer
sudo systemctl start safran-sync.timer

# Vérifier l'installation
sudo systemctl status safran-sync.timer
```

### 6. Vérification
```bash
# Voir les prochaines exécutions planifiées
systemctl list-timers safran-sync.timer

# Tester une exécution manuelle
sudo systemctl start safran-sync.service

# Suivre les logs en temps réel
sudo journalctl -u safran-sync.service -f
```


## Configuration avancée
### Changer l'heure d'exécution
Éditer le timer :
```bash
sudo systemctl edit safran-sync.timer
```

Ajouter :
```ini
[Timer]
OnCalendar=
OnCalendar=*-*-* 03:00:00
```

Recharger :
```bash
sudo systemctl daemon-reload
sudo systemctl restart safran-sync.timer
```

### Notifications par email
Installer postfix :
```bash
sudo apt install postfix mailutils
```

Modifier le service pour envoyer un email en cas d'erreur :
```bash
sudo systemctl edit safran-sync.service
```

Ajouter :
```ini
[Service]
OnFailure=status-email@%n.service
```

### Rotation des logs
Créer `/etc/logrotate.d/safran-fairy` :
```
/var/log/safran-fairy/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 safran-user safran-user
    sharedscripts
}
```


## Monitoring
### Vérifier la santé du service
```bash
# Statut général
make status

# Dernière exécution
make last-run

# Logs des 24 dernières heures
sudo journalctl -u safran-sync.service --since "24 hours ago"

# Erreurs uniquement
sudo journalctl -u safran-sync.service -p err
```

### Métriques utiles
```bash
# Taille des données
du -sh 0*_SAFRAN-data_*/

# Nombre de fichiers traités
ls 04_SAFRAN-data_output/*.nc | wc -l

# Dernière mise à jour
stat -c '%y' 04_SAFRAN-data_output/*.nc | sort | tail -1
```


## Désinstallation
```bash
# Arrêter et désactiver le service
sudo systemctl stop safran-sync.timer
sudo systemctl disable safran-sync.timer
sudo systemctl stop safran-sync.service

# Supprimer les fichiers systemd
sudo rm /etc/systemd/system/safran-sync.service
sudo rm /etc/systemd/system/safran-sync.timer
sudo systemctl daemon-reload

# Supprimer le projet (attention : supprime toutes les données !)
sudo rm -rf /opt/safran-fairy
```


## Dépannage
### Le service ne démarre pas
```bash
# Vérifier les permissions
ls -la /opt/safran-fairy
sudo chown -R safran-user:safran-user /opt/safran-fairy

# Vérifier la syntaxe du service
systemd-analyze verify safran-sync.service

# Logs détaillés
sudo journalctl -xe -u safran-sync.service
```

### Problèmes de téléchargement
```bash
# Tester la connexion à l'API
curl -I https://meteo.data.gouv.fr/

# Vérifier les credentials Dataverse
curl -H "X-Dataverse-key: $RDG_API_TOKEN" \
     "$RDG_BASE_URL/api/datasets/:persistentId/?persistentId=$RDG_DATASET_DOI"
```

### Espace disque insuffisant
```bash
# Vérifier l'espace disponible
df -h /opt/safran-fairy

# Nettoyer les fichiers intermédiaires
make clean

# Nettoyer uniquement les fichiers temporaires (garde les outputs)
rm -rf 01_SAFRAN-data_raw/* 02_SAFRAN-data_split/* 03_SAFRAN-data_convert/*
```


## Migration vers un nouveau serveur
```bash
# Sur l'ancien serveur : sauvegarder la config et l'état
tar czf safran-backup.tar.gz .env resources/download_state.json

# Sur le nouveau serveur : suivre l'installation normale puis restaurer
tar xzf safran-backup.tar.gz
```
