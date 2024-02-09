import urllib.request
import json
from zipfile import ZipFile
from pathlib import Path
from rich.progress import Progress
import shutil

ACCESS_TOKEN = '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'

def fetch_latest_version(repo_name):
    api_url = f"https://api.github.com/repos/acidanthera/{repo_name}/releases/latest"
    try:
        request = urllib.request.Request(api_url, headers={'Authorization': f'token {ACCESS_TOKEN}'})
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read())
        return data["tag_name"]
    except Exception as e:
        print(f"Error fetching latest {repo_name} version: {e}")
        return None

def download_file(url, output_path):
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading", total=1, start=True)
        urllib.request.urlretrieve(url, output_path, reporthook=lambda b, bsize, tsize: progress.update(task, advance=bsize))

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

    kexts = {
        "AppleALC": "AppleALC",
        "IntelMausi": "IntelMausi",
        "Lilu": "Lilu",
        "RestrictEvents": "RestrictEvents",
        "VirtualSMC": "VirtualSMC",
        "VirtualSMC": "SMCProcessor",
        "VirtualSMC": "SMCSuperIO",
        "Whatevergreen": "WhateverGreen",
    }

    for kext_name, kext_dir in kexts.items():
        latest_version = fetch_latest_version(kext_name)
        if latest_version:
            print(f"Latest {kext_name} version available: {latest_version}")
            desired_version = input(f"Enter the desired {kext_name} version (or press Enter for latest): ")
            desired_version = desired_version.strip() or latest_version  # Use the latest if no input is given

            kext_url = f"https://github.com/acidanthera/{kext_name}/releases/download/{desired_version}/{kext_name}-{desired_version}-RELEASE.zip"
            kext_download_path = kexts_dir / f"{kext_name}-{desired_version}-RELEASE.zip"

            try:
                download_file(kext_url, kext_download_path)

                if kext_name == "VirtualSMC":
                    extract_virtual_smc(kext_download_path, kexts_dir)
                else:
                    extract_kext(kext_download_path, kexts_dir, kext_dir)

                kext_download_path.unlink()  # Remove the downloaded zip file

                print(f"{kext_name}-{desired_version} has been downloaded and installed.")
            except Exception as e:
                print(f"Error downloading {kext_name}: {e}")
            
if __name__ == "__main__":
    main()

