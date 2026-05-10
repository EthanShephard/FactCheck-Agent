import requests
from bs4 import BeautifulSoup


def search_claim_online(claim):
    """
    Free web verification using DuckDuckGo HTML search.
    """

    try:
        query = claim.replace(" ", "+")
        url = f"https://html.duckduckgo.com/html/?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {
                "claim": claim,
                "status": "Error",
                "evidence": "Search request failed."
            }

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", limit=3)

        if not results:
            return {
                "claim": claim,
                "status": "False",
                "evidence": "No evidence found."
            }

        evidence_sources = []

        for result in results:
            title = result.get_text()
            link = result.get("href")

            evidence_sources.append({
                "title": title,
                "url": link,
                "content": title
            })

        return {
            "claim": claim,
            "status": "Needs Review",
            "evidence": "Relevant sources found. Manual validation recommended.",
            "sources": evidence_sources
        }

    except Exception as e:
        return {
            "claim": claim,
            "status": "Error",
            "evidence": f"Verification failed: {str(e)}"
        }