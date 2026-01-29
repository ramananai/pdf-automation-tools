import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://boslive.icai.org/sm_chapter_details.php?p_id=142&m_id=181"

# Jupyter-safe download directory
DOWNLOAD_DIR = os.getcwd()

session = requests.Session()
response = session.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

pdf_links = soup.find_all("a", href=lambda x: x and x.lower().endswith(".pdf"))

print(f"Found {len(pdf_links)} PDF links")

for link in pdf_links:
    pdf_url = urljoin(URL, link["href"])
    link_text = link.get_text(strip=True)

    if not link_text:
        continue

    safe_name = re.sub(r'[\\/*?:"<>|]', "", link_text)
    file_name = safe_name + ".pdf"
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    print("Downloading:", file_name)

    pdf_response = session.get(pdf_url, stream=True)
    pdf_response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in pdf_response.iter_content(8192):
            if chunk:
                f.write(chunk)

print("✅ All PDFs downloaded to:", DOWNLOAD_DIR)
