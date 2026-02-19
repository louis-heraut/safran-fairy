import os
import re
import requests
from pathlib import Path
from datetime import datetime
from art import tprint


def clean_dataverse(dataset_DOI: str,
                    RDG_BASE_URL: str = os.getenv("RDG_BASE_URL"),
                    RDG_API_TOKEN: str = os.getenv("RDG_API_TOKEN"),
                    extensions=['.csv', '.csv.gz', '.parquet', '.nc'],
                    patterns = {
                        'latest': r'latest-(\d{8})-(\d{8})',
                        'previous': r'previous-(\d{4})-(\d{6})'
                    }):
    """
    Supprime les fichiers obsolètes d'un dataset Dataverse en ne gardant que le plus récent par type.
    """
    
    print("\nNETTOYAGE")
    print(f"   Dataset: {dataset_DOI}")
    
    # Récupérer la liste des fichiers du dataset
    url = f"{RDG_BASE_URL}/api/datasets/:persistentId/?persistentId={dataset_DOI}"
    headers = {'X-Dataverse-key': RDG_API_TOKEN}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"   ❌ Impossible de récupérer les fichiers: {response.text}")
        return
    
    files_data = response.json()['data']['latestVersion']['files']
    
    for file_type, pattern in patterns.items():
        print(f"\nRecherche de fichiers '{file_type}'...")
        
        # Filtrer les fichiers qui matchent le pattern ET l'extension
        matching_files = []
        for file_info in files_data:
            filename = file_info['dataFile']['filename']
            
            # Vérifier l'extension
            file_ext = ''.join(Path(filename).suffixes)
            if file_ext not in extensions:
                continue
            
            # Vérifier le pattern
            if re.search(pattern, filename):
                date = int(re.search(pattern, filename).group(2))
                matching_files.append({
                    'id': file_info['dataFile']['id'],
                    'filename': filename,
                    'date': date
                })
        
        if not matching_files:
            print(f"   - ℹ️ Aucun fichier trouvé")
            continue
        
        # Identifier les fichiers à supprimer (tous sauf le plus récent)
        max_date = max(f['date'] for f in matching_files)
        files_to_delete = [f for f in matching_files if f['date'] < max_date]
        
        # Supprimer les fichiers obsolètes
        deleted_count = 0
        for file in files_to_delete:
            delete_url = f"{RDG_BASE_URL}/api/files/{file['id']}"
            del_response = requests.delete(delete_url, headers=headers)
            if del_response.status_code in [200, 204]:  # <-- ajout du 200
                print(f"   - 🗑️ {file['filename']}")
                deleted_count += 1
            else:
                print(f"   - ❌ Échec suppression {file['filename']}: {del_response.text}")

        print(f"   - 📊 {deleted_count}/{len(files_to_delete)} fichier(s) supprimé(s)")


def clean_local(directory, extensions, patterns):
    """Version locale de ton code actuel"""
    directory = Path(directory)
    print("\nNETTOYAGE")
    
    for file_type, pattern in patterns.items():
        print(f"\nRecherche de fichiers '{file_type}'...")
        
        files = list(directory.glob(f"*{file_type}*"))
        files = [f for f in files if ''.join(f.suffixes) in extensions]
        files = [f for f in files if re.search(pattern, f.name)]
        
        if not files:
            print(f"   - ℹ️ Aucun fichier trouvé")
            continue
        
        dates = [int(re.search(pattern, f.name).group(2)) for f in files]
        max_date = max(dates)
        files_to_delete = [f for f, d in zip(files, dates) if d < max_date]
        for file in files_to_delete:
            print(f"   - 🗑️ {file.name}")
            file.unlink()
        
        print(f"   - 📊 {len(files_to_delete)} fichier(s) supprimé(s)")


def clean(directory=None,
          dataset_DOI=None,
          extensions=['.csv', '.csv.gz', '.parquet', '.nc'],
          patterns = {
            'latest': r'latest-(\d{8})-(\d{8})',
            'previous': r'previous-(\d{4})-(\d{6})'
          },
          RDG_BASE_URL: str = os.getenv("RDG_BASE_URL"),
          RDG_API_TOKEN: str = os.getenv("RDG_API_TOKEN")):
    """
    Nettoie un dossier local ET/OU un dataset Dataverse.
    """
    
    if directory:
        clean_local(directory=directory,
                    extensions=extensions,
                    patterns=patterns)
    
    if dataset_DOI:
        clean_dataverse(dataset_DOI=dataset_DOI,
                        extensions=extensions,
                        patterns=patterns,
                        RDG_BASE_URL=RDG_BASE_URL,
                        RDG_API_TOKEN=RDG_API_TOKEN)
