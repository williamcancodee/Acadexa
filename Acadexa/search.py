import requests
from youtubesearchpython import VideosSearch

STEM_SUBJECTS = ['Math', 'Science', 'Computer Science', 'Physics', 'Chemistry', 'Biology', 'Engineering', 'Economics', 'Psychology', 'Sociology', 'Philosophy', 'Medicine', 'Law', 'Business']

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
