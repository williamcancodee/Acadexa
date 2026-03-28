import requests
from youtubesearchpython import VideosSearch

STEM_SUBJECTS = ['Math', 'Science', 'Computer Science', 'Physics', 'Chemistry', 'Biology', 'Engineering', 'Economics', 'Psychology', 'Sociology', 'Philosophy', 'Medicine', 'Law', 'Business']


def merge_sources(*lists):
    merged = []
    seen = set()
    for items in lists:
        for item in items:
            key = (item.get('link') or item.get('title') or '').strip().lower()
            if not key or key in seen:
                continue
            merged.append(item)
            seen.add(key)
    return merged

def search_books(query, limit=10):
    """
    Search for books using Open Library API.

    Args:
        query (str): Search query for books.
        limit (int): Maximum number of results.

    Returns:
        list: List of dictionaries with book details.
    """
    url = f"https://openlibrary.org/search.json?q={query}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        books = []
        for doc in data.get('docs', []):
            title = doc.get('title', 'Unknown Title')
            author = ', '.join(doc.get('author_name', ['Unknown Author']))
            key = doc.get('key', '')
            link = f"https://openlibrary.org{key}" if key else "N/A"
            description = doc.get('first_sentence', ['No description'])[0] if doc.get('first_sentence') else 'No description'
            books.append({'title': title, 'author': author, 'link': link, 'description': description})
        return books
    except requests.RequestException as e:
        print(f"Error searching books: {e}")
        return []


def search_google_books(query, limit=10):
    """Search for books using Google Books API."""
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        books = []
        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})
            title = volume.get('title', 'Unknown Title')
            author = ', '.join(volume.get('authors', ['Unknown Author']))
            description = volume.get('description', 'No description')
            link = volume.get('infoLink', 'N/A')
            books.append({'title': title, 'author': author, 'link': link, 'description': description})
        return books
    except requests.RequestException as e:
        print(f"Error searching Google Books: {e}")
        return []


def search_gutenberg_links(query, limit=5):
    """Create Project Gutenberg catalog links as additional open-source book source."""
    items = []
    for idx in range(limit):
        items.append({
            'title': f"Project Gutenberg Catalog: {query} #{idx + 1}",
            'author': 'Various Authors',
            'description': 'Open classic literature and educational public-domain books.',
            'link': f"https://www.gutenberg.org/ebooks/search/?query={query.replace(' ', '+')}"
        })
    return items

def search_videos(query, limit=5):
    """
    Search for videos on YouTube.

    Args:
        query (str): Search query for videos.
        limit (int): Maximum number of results.

    Returns:
        list: List of dictionaries with video details.
    """
    try:
        videos_search = VideosSearch(query, limit=limit)
        results = videos_search.result()['result']
        videos = [{'title': r['title'], 'link': r['link']} for r in results]
        return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

def search_articles(query, limit=5):
    """
    Search for articles on Wikipedia.

    Args:
        query (str): Search query for articles.
        limit (int): Maximum number of results.

    Returns:
        list: List of dictionaries with article details.
    """
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&limit={limit}"
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = []
        for item in data.get('query', {}).get('search', []):
            title = item['title']
            link = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            summary = 'No summary available'
            try:
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
                summary_response = requests.get(summary_url, timeout=10)
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    summary = summary_data.get('extract', 'No summary available')
                    link = summary_data.get('content_urls', {}).get('desktop', {}).get('page', link)
            except requests.RequestException:
                pass  # Keep default summary and link
            articles.append({
                'title': title,
                'summary': summary,
                'link': link
            })
        return articles
    except requests.RequestException as e:
        print(f"Error searching articles: {e}")
        return []


def search_arxiv(query, limit=5):
    """Search arXiv feed for academic papers."""
    url = f"https://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&start=0&max_results={limit}"
    try:
        response = requests.get(url, timeout=12)
        response.raise_for_status()
        xml = response.text
        entries = xml.split('<entry>')[1:]
        papers = []
        for entry in entries:
            title = 'Unknown Title'
            summary = 'No summary available'
            link = 'https://arxiv.org'
            if '<title>' in entry:
                title = entry.split('<title>', 1)[1].split('</title>', 1)[0].strip().replace('\n', ' ')
            if '<summary>' in entry:
                summary = entry.split('<summary>', 1)[1].split('</summary>', 1)[0].strip().replace('\n', ' ')
            if '<id>' in entry:
                link = entry.split('<id>', 1)[1].split('</id>', 1)[0].strip()
            papers.append({'title': title, 'summary': summary, 'link': link})
        return papers
    except requests.RequestException as e:
        print(f"Error searching arXiv: {e}")
        return []


def search_openalex(query, limit=5):
    """Search OpenAlex for scholarly works."""
    url = f"https://api.openalex.org/works?search={query}&per-page={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        works = []
        for item in data.get('results', []):
            title = item.get('display_name', 'Unknown Title')
            summary = 'Scholarly article index from OpenAlex.'
            link = item.get('primary_location', {}).get('landing_page_url') or item.get('id', 'https://openalex.org')
            works.append({'title': title, 'summary': summary, 'link': link})
        return works
    except requests.RequestException as e:
        print(f"Error searching OpenAlex: {e}")
        return []

def search_libraries(query, limit=5):
    """
    Search for open source libraries on GitHub.

    Args:
        query (str): Search query for libraries.
        limit (int): Maximum number of results.

    Returns:
        list: List of dictionaries with library details.
    """
    url = f"https://api.github.com/search/repositories?q={query}+language:python&sort=stars&order=desc&per_page={limit}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        libraries = []
        for repo in data.get('items', []):
            title = repo.get('name', 'Unknown')
            description = repo.get('description', 'No description') or 'No description'
            link = repo.get('html_url', 'N/A')
            libraries.append({'title': title, 'description': description, 'link': link})
        return libraries
    except requests.RequestException as e:
        print(f"Error searching libraries: {e}")
        return []

def search_pdfs(query, limit=5):
    """
    Generate search links for academic PDFs on Ocean of PDF.

    Args:
        query (str): Search query for PDFs.
        limit (int): Number of links (currently returns one per call).

    Returns:
        list: List of dictionaries with PDF search links.
    """
    pdfs = []
    for i in range(limit):
        pdfs.append({'title': f"Academic PDF Search for {query}", 'link': f"https://oceanofpdf.com/search?q={query.replace(' ', '+')}"})
    return pdfs


def search_oer_commons_links(query, limit=5):
    """Generate OER Commons search links for open educational materials."""
    items = []
    for idx in range(limit):
        items.append({
            'title': f"OER Commons Materials for {query} #{idx + 1}",
            'description': 'Open educational resources, lesson plans, and course modules.',
            'link': f"https://www.oercommons.org/search?f.search={query.replace(' ', '+')}"
        })
    return items
