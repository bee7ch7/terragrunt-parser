import os
import urllib.request
import zipfile

def download_and_unzip(version, download_path, extract_path):
    if "v" in version:
        url = f"https://github.com/gruntwork-io/terragrunt/releases/download/{version}/terragrunt_linux_amd64"
        print(f"Downloading Terragrunt {version}...")
    else:    
        url = f'https://releases.hashicorp.com/terraform/{version}/terraform_{version}_linux_amd64.zip'
        print(f"Downloading Terraform version {version}...")

    # Download the file
    urllib.request.urlretrieve(url, download_path)

    # Unzip the file
    if extract_path != False:
      with zipfile.ZipFile(download_path, 'r') as zip_ref:
          zip_ref.extractall(extract_path)
      # Clean up: remove the downloaded zip file
      os.remove(download_path)

    print("Setting permissions on binaries...")
    if "v" in version:
        os.chmod("/app/terragrunt", 0o755)
    else:
        os.chmod("/app/terraform", 0o755)
    print("Completed!")

    return True