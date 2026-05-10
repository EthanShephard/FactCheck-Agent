import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Optional: Tavily Search API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_claim_online(claim):
    """
    Searches the web for evidence related to a factual claim.

    Args:
        claim (str): Claim extracted from PDF.

    Returns:
        dict: Search result summary.
    """

    if not TAVILY_API_KEY:
        return {
            "claim": claim,
            "status": "Error",
            "evidence": "Missing Tavily API key."
        }

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": claim,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 3
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        answer = data.get("answer", "")
        results = data.get("results", [])

        if not results:
            return {
                "claim": claim,
                "status": "False",
                "evidence": "No reliable evidence found online."
            }

        # Simple heuristic verification
        if answer:
            if any(word in answer.lower() for word in ["true", "correct", "confirmed", "reported"]):
                status = "Verified"
            elif any(word in answer.lower() for word in ["outdated", "changed", "revised"]):
                status = "Inaccurate"
            else:
                status = "Needs Review"
        else:
            status = "Needs Review"

        evidence_sources = []
        for result in results:
            evidence_sources.append({
                "title": result.get("title"),
                "url": result.get("url"),
                "content": result.get("content")
            })

        return {
            "claim": claim,
            "status": status,
            "evidence": answer,
            "sources": evidence_sources
        }

    except Exception as e:
        return {
            "claim": claim,
            "status": "Error",
            "evidence": f"Verification failed: {str(e)}"
        }