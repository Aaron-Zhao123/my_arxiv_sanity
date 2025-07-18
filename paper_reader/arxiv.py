import requests
import feedparser
import time
from datetime import datetime, timedelta


def search_arxiv_abstract(
    paper_title, max_results=1, timeout=5, max_retries=3, retry_wait=2, return_all=False
):
    search_query = 'ti:"{}"'.format(paper_title)
    url = f"https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={max_results}"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            feed = feedparser.parse(response.text)

            if feed.entries:
                abstracts = [entry.summary for entry in feed.entries]
                if return_all:
                    return abstracts
                else:
                    return abstracts[0]
            else:
                return [] if return_all else None

        except (requests.exceptions.RequestException, Exception) as e:
            if attempt == max_retries:
                return [] if return_all else None
            time.sleep(retry_wait)


def search_arxiv_paper_info(
    paper_title, max_results=1, timeout=5, max_retries=3, retry_wait=2
):
    """Search for paper information including abstract and URL"""
    search_query = 'ti:"{}"'.format(paper_title)
    url = f"https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={max_results}"

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            feed = feedparser.parse(response.text)

            if feed.entries:
                entry = feed.entries[0]
                # Extract arxiv ID from the entry ID
                arxiv_id = entry.id.split('/')[-1]
                return {
                    "abstract": entry.summary,
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "arxiv_id": arxiv_id
                }
            else:
                return None

        except (requests.exceptions.RequestException, Exception) as e:
            if attempt == max_retries:
                return None
            time.sleep(retry_wait)
    
    return None


def get_recent_arxiv_papers(max_results=1000, days_ago=1):
    assert 0 < days_ago, "days_ago should be be greater than 0"
    # Compute date range in arXiv format: 20240614
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_ago)
    start_str = start_date.strftime("%Y%m%d%H%M")
    end_str = end_date.strftime("%Y%m%d%H%M")

    base_url = "https://export.arxiv.org/api/"
    # query focuses on machine learning, AI and hardware architecture categories
    # Change this to your desired categories, full list available at https://arxiv.org/category_taxonomy
    query = "cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.AR+"
    url = f"{base_url}query?search_query={query}"
    url += f"+AND+submittedDate:[{start_str}+TO+{end_str}]"
    url += f"&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)

    papers = []
    i = 0
    for entry in feed.entries:
        # Parse the published date
        papers.append(
            {
                "title": entry.title,
                "authors": [author.name for author in entry.authors],
                "published": entry.published,
                "id": entry.id,
                "summary": entry.summary,
            }
        )
        i += 1
        if i >= max_results:
            break
    return papers
