from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import mimetypes

proxyUrl = "http://localhost:5000/autoForward.html?url="

aub = ["http:", "https:", "ftp:", "ftps:", "sftp:"]

def get_content_type(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('Content-Type', '')
        
        if content_type:
            return content_type  # Return the content type from the header

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")

    # Fallback to extension-based type detection
    _, ext = os.path.splitext(url)
    return mimetypes.types_map.get(ext.lower(), 'application/octet-stream')

def webScrape(url):
    print("scraping...")
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        def modify_url(original_url):
            try:
                data = original_url.split("/")
                backDir = 0  # Initialize backDir if it's used

                if data[0] in aub:
                    return proxyUrl + original_url
                elif data[0] == "..":
                    for i in range(len(data)):
                        if data[i] == "..":
                            backDir += 1
                        else:
                            break
                        
                    newUrl = ""
                    newData = url.split("/")  # Ensure 'url' is defined in your scope

                    for i in range(len(newData) - backDir):
                        newUrl += newData[i] + "/"

                    if newUrl[-1] != "/":
                        newUrl += "/"

                    for j in range(len(data) - backDir):
                        newUrl += data[j + backDir] + "/"

                    return proxyUrl + newUrl
                else:
                    newData = url.split("/")
                    print(newData)
                    newUrl = newData[0] + "/" + newData[1] + "/" + newData[2]
            
                    if original_url[0] != "/":
                        newUrl = newUrl + original_url[1:]
                    else:
                        newUrl = newUrl + original_url
                    return proxyUrl + newUrl

            except Exception as e:
                print("Error:", e)
        
        for tag in soup.find_all(True):  # True finds all tags
            if 'href' in tag.attrs:
                original_href = tag['href']
                tag['href'] = modify_url(original_href)

            if 'src' in tag.attrs:
                original_src = tag['src']
                tag['src'] = modify_url(original_src)

        return soup.prettify()
    else:
        print('Failed to retrieve the webpage')
        return 'Error retrieving content'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the path to the front-end directory
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'front-end')

@app.route('/')
def home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>', methods=['GET'])
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json  # Get JSON data from the request
    url = data['data']
    response_content = webScrape(url)

    # Determine the content type to return based on the URL
    content_type = get_content_type(url)

    # Return a Flask Response object
    return Response(response_content, status=200, content_type=content_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)