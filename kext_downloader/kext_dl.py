import urllib.request
import json
from zipfile import ZipFile
from pathlib import Path
import shutil
import requests
import zipfile
import os
from tqdm import tqdm

def fetch_latest_version(repo_name):
    api_url = f"https://api.github.com/repos/acidanthera/{repo_name}/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read())
        return data["tag_name"]
    except Exception as e:
        print(f"Error fetching latest {repo_name} version: {e}")
        return None

def download_file(url, output_path):
    urllib.request.urlretrieve(url, output_path)

def extract_kext(zip_path, extract_dir, kext_dir):
    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extract(f"{kext_dir}.kext/Contents/MacOS/{kext_dir}", extract_dir)
        zip_ref.extract(f"{kext_dir}.kext/Contents/Info.plist", extract_dir)

def extract_virtual_smc(zip_path, extract_dir):
    with ZipFile(zip_path, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            file_path = file_info.filename
            if "Kexts/VirtualSMC.kext" in file_path:
                zip_ref.extract(file_path)
                extracted_dir = Path(extract_dir) / "VirtualSMC.kext"
            if "Kexts/SMCProcessor.kext" in file_path:
                zip_ref.extract(file_path)
                extracted_dir = Path(extract_dir) / "SMCProcessor.kext"
            if "Kexts/SMCSuperIO.kext" in file_path:
                zip_ref.extract(file_path)
                extracted_dir = Path(extract_dir) / "SMCSuperIO.kext"

def main():
    kexts_dir = Path("Kexts")
    kexts_dir.mkdir(exist_ok=True)

    # Download other kexts directly without prompting for user input
    kexts = {
        "AppleALC": "AppleALC",
        "IntelMausi": "IntelMausi",
        "Lilu": "Lilu",
        "RestrictEvents": "RestrictEvents",
        "VirtualSMC": "VirtualSMC",
        "SMCProcessor": "SMCProcessor",
        "SMCSuperIO": "SMCSuperIO",
        "WhateverGreen": "WhateverGreen",
    }

    # Initialize tqdm manually
    progress_bar = tqdm(total=len(kexts), desc="Downloading and installing kexts")

    for kext_name, kext_dir in kexts.items():
        latest_version = fetch_latest_version(kext_name)
        if latest_version:
            kext_url = f"https://github.com/acidanthera/{kext_name}/releases/download/{latest_version}/{kext_name}-{latest_version}-RELEASE.zip"
            kext_download_path = kexts_dir / f"{kext_name}-{latest_version}-RELEASE.zip"

            try:
                download_file(kext_url, kext_download_path)

                if kext_name == "VirtualSMC":
                    extract_virtual_smc(kext_download_path, kexts_dir)
                else:
                    extract_kext(kext_download_path, kexts_dir, kext_dir)

                kext_download_path.unlink()  # Remove the downloaded zip file

                print(f"{kext_name}-{latest_version} has been downloaded and installed.")
            except Exception as e:
                print(f"Error downloading {kext_name}: {e}")

        # Update progress bar
        progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()

    # Download LucyRTL8125Ethernet
    kext_url = "https://github.com/Mieze/LucyRTL8125Ethernet/releases/download/1.1.0/LucyRTL8125Ethernet-V1.1.0.zip"
    kext_local_zip_name = "LucyRTL8125Ethernet-V1.1.0.zip"
    kext_extracted_kext_path = "LucyRTL8125Ethernet-V1.1.0/Release/LucyRTL8125Ethernet.kext"

    # Download the LucyRTL8125Ethernet file
    response = requests.get(kext_url)
    with open(kext_local_zip_name, 'wb') as file:
        file.write(response.content)

    # Extract the contents of the LucyRTL8125Ethernet zip file
    with zipfile.ZipFile(kext_local_zip_name, 'r') as zip_ref:
        zip_ref.extractall()

    # Move the LucyRTL8125Ethernet .kext file to the desired directory
    target_directory = "Kexts"  # Specify the target directory
    os.makedirs(target_directory, exist_ok=True)  # Create the directory if it doesn't exist
    os.rename(kext_extracted_kext_path, os.path.join(target_directory, os.path.basename(kext_extracted_kext_path)))
    print("LucyRTL8125Ethernet has been downloaded and installed.")

    # Clean up: remove the downloaded zip file and unrelated directories
    os.remove(kext_local_zip_name)
    current_directory = os.getcwd()

    for item in os.listdir(current_directory):
        if os.path.isdir(item) and item != target_directory:
            shutil.rmtree(item)

    print("Extraction complete.")

if __name__ == "__main__":
    main()
