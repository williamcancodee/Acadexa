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
    from search import search_books, search_videos, search_articles, search_libraries, search_pdfs

    resources = {}
    for subject in subjects:
        if 'books' in resource_types:
            if 'books' not in resources:
                resources['books'] = []
            query = f"{subject} textbook"
            try:
                books = search_books(query, limit=5)
                relevant_books = [b for b in books if subject.lower() in b['title'].lower() or subject.lower() in b['description'].lower()]
                if not relevant_books:
                    relevant_books = books[:2]
                resources['books'].extend(relevant_books[:2])
            except Exception as e:
                print(f"Error searching books: {e}")
        if 'videos' in resource_types:
            if 'videos' not in resources:
                resources['videos'] = []
            query = f"{level} {subject} tutorial"
            try:
                videos = search_videos(query, limit=2)
                resources['videos'].extend(videos)
            except Exception as e:
                print(f"Error searching videos: {e}")
        if 'articles' in resource_types:
            if 'articles' not in resources:
                resources['articles'] = []
            query = f"{level} {subject}"
            try:
                articles = search_articles(query, limit=2)
                resources['articles'].extend(articles)
            except Exception as e:
                print(f"Error searching articles: {e}")
        if 'libraries' in resource_types:
            if 'libraries' not in resources:
                resources['libraries'] = []
            if subject in STEM_SUBJECTS:
                query = f"{subject} python library"
                try:
                    libraries = search_libraries(query, limit=5)
                    relevant_libraries = [l for l in libraries if subject.lower() in l['description'].lower()]
                    if not relevant_libraries:
                        relevant_libraries = libraries[:2]
                    resources['libraries'].extend(relevant_libraries[:2])
                except Exception as e:
                    print(f"Error searching libraries: {e}")
            else:
                query = f"{subject} academic pdf"
                try:
                    pdfs = search_pdfs(query, limit=2)
                    resources['libraries'].extend(pdfs)
                except Exception as e:
                    print(f"Error searching PDFs: {e}")
    return resources
