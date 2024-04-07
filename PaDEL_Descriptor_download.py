import requests
import zipfile

# Download padel.zip
url_padel_zip = "https://github.com/dataprofessor/bioinformatics/raw/master/padel.zip"
response_padel_zip = requests.get(url_padel_zip)
with open("padel.zip", "wb") as f:
    f.write(response_padel_zip.content)

# Download padel.sh
url_padel_sh = "https://github.com/dataprofessor/bioinformatics/raw/master/padel.sh"
response_padel_sh = requests.get(url_padel_sh)
with open("padel.sh", "wb") as f:
    f.write(response_padel_sh.content)

# Specify the path to the ZIP file
zip_file = "padel.zip"

# Specify the directory where you want to extract the contents
extract_to = "./"

# Extract the contents of the ZIP file
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(extract_to)