import os
import sys
import requests
from rich.progress import Progress

DOWNLOAD_DIR = "/mnt/Downloads"

def download_file(url, filename=None):
    filename = filename or os.path.basename(url)
    full_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            
            with Progress() as progress:
                task_id = progress.add_task("download", filename=filename, total=total_size_in_bytes)
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                with open(full_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        progress.update(task_id, advance=len(chunk))
                 
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        sys.exit(1)
    except Exception as err:
        print(f"An error occurred: {err}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py URL [FILENAME]")
        sys.exit(1)
    
    url = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_file(url, filename)
