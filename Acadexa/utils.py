def parse_grade(grade):
    """
    Parse grade to a level string.

    Args:
        grade (str): Grade string from form.

    Returns:
        str: Parsed level.
    """
    grade_parts = grade.split()
    level = grade_parts[0].lower()
    if level == 'elementary':
        level = 'elementary school'
    elif level == 'middle':
        level = 'middle school'
    elif level == 'high':
        level = 'high school'
    elif level == 'university':
        level = 'college'
    else:
        level = grade.lower()
    return level


LEVEL_PROFILES = {
    'elementary school': {
        'books_query': 'kids beginner workbook',
        'videos_query': 'for kids basics',
        'articles_query': 'simple introduction for kids',
        'libraries_query': 'beginner educational python',
        'include_keywords': ['kids', 'child', 'children', 'beginner', 'basics', 'simple', 'grade'],
        'exclude_keywords': ['advanced', 'research', 'graduate', 'theory', 'thesis', 'university'],
        'limits': {'books': 2, 'videos': 2, 'articles': 2, 'libraries': 1},
    },
    'middle school': {
        'books_query': 'middle school fundamentals practice',
        'videos_query': 'middle school tutorial fundamentals',
        'articles_query': 'middle school concept guide',
        'libraries_query': 'student friendly python project',
        'include_keywords': ['middle school', 'fundamentals', 'intro', 'concept'],
        'exclude_keywords': ['graduate', 'research paper', 'doctoral', 'thesis'],
        'limits': {'books': 2, 'videos': 2, 'articles': 2, 'libraries': 1},
    },
    'high school': {
        'books_query': 'high school exam prep textbook',
        'videos_query': 'high school lesson tutorial',
        'articles_query': 'high school overview',
        'libraries_query': 'intermediate python library examples',
        'include_keywords': ['high school', 'exam', 'introduction', 'intermediate'],
        'exclude_keywords': ['doctoral', 'graduate seminar'],
        'limits': {'books': 3, 'videos': 2, 'articles': 2, 'libraries': 2},
    },
    'college': {
        'books_query': 'university advanced textbook',
        'videos_query': 'university lecture advanced',
        'articles_query': 'research overview advanced',
        'libraries_query': 'professional python library research',
        'include_keywords': ['university', 'college', 'advanced', 'research', 'professional', 'theory'],
        'exclude_keywords': ['kids', 'for children', 'grade 1', 'grade 2', 'cartoon'],
        'limits': {'books': 3, 'videos': 3, 'articles': 3, 'libraries': 2},
    },
}


def _profile_for_level(level):
    return LEVEL_PROFILES.get(level, LEVEL_PROFILES['high school'])


def _item_text(item):
    return ' '.join([
        str(item.get('title', '')),
        str(item.get('description', '')),
        str(item.get('summary', '')),
        str(item.get('author', ''))
    ]).lower()


def _score_item(item, subject, profile, level):
    text = _item_text(item)
    score = 0

    if subject.lower() in text:
        score += 5
    if level.split()[0] in text:
        score += 3

    score += sum(2 for word in profile['include_keywords'] if word in text)
    score -= sum(3 for word in profile['exclude_keywords'] if word in text)

    return score


def _rank_and_filter(items, subject, profile, level, limit):
    scored = []
    for item in items:
        score = _score_item(item, subject, profile, level)
        if score > -2:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    ranked_items = [item for _, item in scored]
    return ranked_items[:limit]


def _dedupe_resources(items):
    deduped = []
    seen_links = set()
    seen_titles = set()

    for item in items:
        link = str(item.get('link', '')).strip().lower()
        title = str(item.get('title', '')).strip().lower()
        key = link or title
        if not key or key in seen_links or key in seen_titles:
            continue
        deduped.append(item)
        seen_links.add(link)
        seen_titles.add(title)

    return deduped

def collect_resources(subjects, resource_types, level, STEM_SUBJECTS):
    """
    Collect resources for given subjects and types.

    Args:
        subjects (list): List of subjects.
        resource_types (list): List of resource types.
        level (str): Parsed grade level.
        STEM_SUBJECTS (list): List of STEM subjects.

    Returns:
        dict: Dictionary of resources by type.
    """
    from search import (
        merge_sources,
        search_arxiv,
        search_articles,
        search_books,
        search_google_books,
        search_gutenberg_links,
        search_libraries,
        search_oer_commons_links,
        search_openalex,
        search_pdfs,
        search_videos,
    )

    profile = _profile_for_level(level)
    resources = {}
    for subject in subjects:
        if 'books' in resource_types:
            if 'books' not in resources:
                resources['books'] = []
            query = f"{level} {subject} {profile['books_query']}"
            try:
                openlibrary_books = search_books(query, limit=5)
                google_books = search_google_books(query, limit=5)
                gutenberg_books = search_gutenberg_links(query, limit=2)
                books = merge_sources(openlibrary_books, google_books, gutenberg_books)
                relevant_books = _rank_and_filter(
                    books,
                    subject,
                    profile,
                    level,
                    profile['limits']['books']
                )
                if not relevant_books:
                    relevant_books = books[:2]
                resources['books'].extend(relevant_books)
            except Exception as e:
                print(f"Error searching books: {e}")
        if 'videos' in resource_types:
            if 'videos' not in resources:
                resources['videos'] = []
            query = f"{level} {subject} {profile['videos_query']}"
            try:
                videos = search_videos(query, limit=6)
                ranked_videos = _rank_and_filter(
                    videos,
                    subject,
                    profile,
                    level,
                    profile['limits']['videos']
                )
                resources['videos'].extend(ranked_videos)
            except Exception as e:
                print(f"Error searching videos: {e}")
        if 'articles' in resource_types:
            if 'articles' not in resources:
                resources['articles'] = []
            query = f"{level} {subject} {profile['articles_query']}"
            try:
                wikipedia_articles = search_articles(query, limit=5)
                arxiv_articles = search_arxiv(query, limit=4)
                openalex_articles = search_openalex(query, limit=4)
                articles = merge_sources(wikipedia_articles, arxiv_articles, openalex_articles)
                ranked_articles = _rank_and_filter(
                    articles,
                    subject,
                    profile,
                    level,
                    profile['limits']['articles']
                )
                resources['articles'].extend(ranked_articles)
            except Exception as e:
                print(f"Error searching articles: {e}")
        if 'libraries' in resource_types:
            if 'libraries' not in resources:
                resources['libraries'] = []
            if subject in STEM_SUBJECTS:
                query = f"{level} {subject} {profile['libraries_query']}"
                try:
                    github_libraries = search_libraries(query, limit=6)
                    oer_links = search_oer_commons_links(query, limit=2)
                    libraries = merge_sources(github_libraries, oer_links)
                    relevant_libraries = _rank_and_filter(
                        libraries,
                        subject,
                        profile,
                        level,
                        profile['limits']['libraries']
                    )
                    if not relevant_libraries:
                        relevant_libraries = libraries[:2]
                    resources['libraries'].extend(relevant_libraries)
                except Exception as e:
                    print(f"Error searching libraries: {e}")
            else:
                query = f"{level} {subject} {profile['articles_query']} academic pdf"
                try:
                    pdfs = search_pdfs(query, limit=profile['limits']['libraries'])
                    oer_links = search_oer_commons_links(query, limit=1)
                    pdfs = merge_sources(pdfs, oer_links)
                    ranked_pdfs = _rank_and_filter(
                        pdfs,
                        subject,
                        profile,
                        level,
                        profile['limits']['libraries']
                    )
                    resources['libraries'].extend(ranked_pdfs)
                except Exception as e:
                    print(f"Error searching PDFs: {e}")

    for key in resources:
        resources[key] = _dedupe_resources(resources[key])

    return resources
