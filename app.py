from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route("/check_requests")
def check_requests():
    try:
        import requests
        return "Requests module is installed and working!"
    except ImportError:
        return "Requests module is not installed."

@app.route('/search', methods=['POST'])
def search():
    word = request.form.get('word')
    google_search_url = f"https://www.google.com/search?q={word}"

    # Function to scrape Google search results
    def scrape_google_results(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Ensure we handle any HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error scraping Google search results: {e}")
            return [], [], [], None
        
        soup = BeautifulSoup(response.text, 'html.parser')

        snippets = []
        descriptions = []
        related_texts = []
        links = []

        # Scrape snippets (main result text)
        for div in soup.find_all("div", class_="BNeawe iBp4i AP7Wnd"):
            text = div.text.strip()
            if text and "Google" not in text:  # Filter out "Google" or irrelevant text
                snippets.append(text)

        # Scrape descriptions (secondary text under results)
        
        count = 0  # Counter to track results
        max_results = 2  # Desired number of results

        for div in soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd"):
            text = div.text.strip()
            if text and "Google" not in text:  # Filter out "Google" or irrelevant text
                descriptions.append(text)
                count += 1
                if count == max_results:  # Stop after collecting the first 2 results
                     break

        # Scrape related texts
        d_count = 0
        max_display = 7
        for div in soup.find_all("div", class_="kCrYT"):
            text = div.text.strip()
            if text and "Google" not in text:  # Filter out "Google" or irrelevant text
                related_texts.append(text)
                d_count += 1
                if d_count == max_display:  # Stop after collecting the first 7 results
                    break

        # Scrape URLs
        decode = []
        seventeenurl = []
        for a_tag in soup.find_all('a', href=True):  # Iterate over all <a> tags with href
            href = a_tag['href']
            if "/url?q=" in href:  # Check if the href contains "/url?q="
                clean_url = href.split("/url?q=")[1].split("&")[0]  # Extract the clean URL
                decoded_url = unquote(clean_url)  # Decode the URL
                decode.append(decoded_url)
            elif href.startswith('/'):  # Handle relative paths
                absolute_url = urljoin("https://www.google.com", href)  # Convert to absolute URL
                seventeenurl.append(absolute_url)  # Append the URL to the list
            links = links + decode + seventeenurl
                    


        # Find the "Next" button
        next_button = soup.find('a', {'aria-label': 'Next'})
        next_url = None
        if next_button and 'href' in next_button.attrs:
            next_url = urljoin("https://www.google.com", next_button['href'])

        return snippets, descriptions, related_texts, links, next_url

    # Initialize variables to store all results
    all_snippets = []
    all_descriptions = []
    all_related_texts = []
    all_links = []

    # Scrape the first page
    snippets, descriptions, related_texts, links, next_url = scrape_google_results(google_search_url)
    all_snippets.extend(snippets)
    all_descriptions.extend(descriptions)
    all_related_texts.extend(related_texts)
    all_links.extend(links)

    # Scrape subsequent pages using the "Next" button
    for _ in range(1, 5):  # Scraping next 4 pages (adjust as needed)
        if next_url:
            snippets, descriptions, related_texts, links, next_url = scrape_google_results(next_url)
            all_snippets.extend(snippets)
            all_descriptions.extend(descriptions)
            all_related_texts.extend(related_texts)
            all_links.extend(links)
        else:
            break

    # Render the results
    return render_template(
        'result.html',
        word=word,
        snippets=all_snippets,
        descriptions=all_descriptions,
        related_texts=all_related_texts,
        links=all_links
    )
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0')
