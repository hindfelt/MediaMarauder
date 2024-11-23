import requests
from bs4 import BeautifulSoup

# List to keep track of downloaded files
downloaded_files = []

def check_for_files(url):
    """
    Check the given URL for downloadable files and download them if not already downloaded.
    """
    print(f"Checking URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all file links (adjust selector based on the website structure)
        files = soup.find_all("a", href=True)
        for file in files:
            file_url = file["href"]
            
            # Check if it's a full URL or a relative path
            if not file_url.startswith("http"):
                file_url = f"{url.rstrip('/')}/{file_url.lstrip('/')}"
            
            # Skip already downloaded files
            if file_url not in downloaded_files:
                download_file(file_url)
    except Exception as e:
        print(f"Error checking files on {url}: {e}")

def downloaded_file(file_url):
    """
    Download a file from the given URL.
    """
    print(f"Downloading file: {file_url}")
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        
        # Get the file name from the URL
        file_name = file_url.split("/")[-1]
        
        # Save the file locally
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded: {file_name}")
        downloaded_files.append(file_url)
    except Exception as e:
        print(f"Error downloading {file_url}: {e}")
