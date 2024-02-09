import requests
import zipfile
import os
import shutil
from rich.prompt import Confirm
from rich.progress import track

# Ask for confirmation to download LucyRTL8125Ethernet
confirmation = Confirm.ask("Accept to download LucyRTL8125Ethernet?")
if not confirmation:
    print("Download cancelled.")
    exit()

# Define the URL and local file name
url = "https://github.com/Mieze/LucyRTL8125Ethernet/releases/download/1.1.0/LucyRTL8125Ethernet-V1.1.0.zip"
local_zip_name = "LucyRTL8125Ethernet-V1.1.0.zip"

# Download the file with progress bar
response = requests.get(url, stream=True)
total_size = int(response.headers.get('content-length', 0))

with open(local_zip_name, 'wb') as file:
    for chunk in track(response.iter_content(chunk_size=1024), total=total_size // 1024, description="Downloading"):
        file.write(chunk)

# Extract the contents of the zip file
with zipfile.ZipFile(local_zip_name, 'r') as zip_ref:
    zip_ref.extractall()

# Move the .kext file to the desired directory
extracted_kext_path = "LucyRTL8125Ethernet-V1.1.0/Release/LucyRTL8125Ethernet.kext"
target_directory = "Kexts"  # Specify the target directory
os.makedirs(target_directory, exist_ok=True)  # Create the directory if it doesn't exist
os.rename(extracted_kext_path, os.path.join(target_directory, os.path.basename(extracted_kext_path)))

# Clean up: remove the downloaded zip file
os.remove(local_zip_name)

# Remove unrelated directories
current_directory = os.getcwd()
for item in os.listdir(current_directory):
    if os.path.isdir(item) and item != target_directory:
        shutil.rmtree(item)

print("Extraction complete.")
