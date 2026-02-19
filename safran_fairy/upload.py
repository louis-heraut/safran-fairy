import os
import requests
import json
import time
from pathlib import Path


def upload(dataset_DOI: str,
           OUTPUT_DIR: str,
           file_paths: list = None,
           directory_labels: list = None,
           file_categories: list = None,
           RDG_BASE_URL: str = os.getenv("RDG_BASE_URL"),
           RDG_API_TOKEN: str = os.getenv("RDG_API_TOKEN"),
           verbose: bool = True):
    
    if file_paths is None:
        file_paths = list(Path(OUTPUT_DIR).glob("*.nc"))
    
    print("\nUPLOAD DATAVERSE")
    print(f"   Dataset: {dataset_DOI}")
    print(f"   Fichiers: {len(file_paths)}")
    
    url = f"{RDG_BASE_URL}/api/datasets/:persistentId/add?persistentId={dataset_DOI}"
    headers = {'X-Dataverse-key': RDG_API_TOKEN}
    not_uploaded = []
    
    for i, file_path in enumerate(file_paths):
        path_obj = Path(file_path)
        directory_label = directory_labels[i] if directory_labels else None
        categories = file_categories[i] if file_categories else None
        
        print(f"\n📤 [{i+1}/{len(file_paths)}] {path_obj.name}")
        if directory_label:
            print(f"   → Dossier: {directory_label}")
        if categories:
            print(f"   🏷️  Catégories: {', '.join(categories)}")
        
        json_data = {"description": "", "restrict": "false", "tabIngest": "true"}
        if directory_label:
            json_data["directoryLabel"] = directory_label
        if categories:
            json_data["categories"] = categories  # ajout direct dans jsonData
        
        try:
            start_time = time.time()
            with open(file_path, 'rb') as f:
                files = {
                    'file': (path_obj.name, f),
                    'jsonData': (None, json.dumps(json_data), 'application/json')
                }
                response = requests.post(url, headers=headers, files=files)
            
            elapsed_time = time.time() - start_time
            file_size = os.path.getsize(file_path) / (1024**2)
            upload_speed = file_size / elapsed_time
            
            if response.status_code != 200:
                not_uploaded.append(file_path)
                print(f"   ❌ Échec: {response.status_code} - {response.text}")
            else:
                print(f"   ✅ Upload: {round(file_size, 2)} MB en {round(elapsed_time, 2)}s @ {round(upload_speed, 2)} MB/s")
        
        except Exception as e:
            not_uploaded.append(file_path)
            print(f"   ❌ Erreur: {str(e)}")
    
    print("\nRÉSUMÉ")
    print(f"   - {len(file_paths) - len(not_uploaded)}/{len(file_paths)} fichier(s) uploadés")
    if not_uploaded:
        print(f"   - ⚠️  {len(not_uploaded)} échec(s)")
    
    return not_uploaded
