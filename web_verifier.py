import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# Tavily API Key
TAVILY_API_KEY = "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"


def normalize_large_numbers(text):
    """
    Converts billion/million values into absolute numbers.
    """
    text = text.lower()
    values = []

    billion_match = re.findall(r'(\d+(?:\.\d+)?)\s*billion', text)
    million_match = re.findall(r'(\d+(?:\.\d+)?)\s*million', text)

    for num in billion_match:
        values.append(float(num) * 1_000_000_000)

    for num in million_match:
        values.append(float(num) * 1_000_000)

    return values


def classify_claim(claim, snippets):
    """
    Classifies claim dynamically based on retrieved evidence.
    """

    claim_lower = claim.lower()
    combined_text = " ".join(snippets).lower()

    contradiction_score = 0
    support_score = 0

    claim_years = re.findall(r'\b(?:19|20)\d{2}\b', claim)

    contradiction_phrases = [
        "false", "incorrect", "wrong", "myth",
        "debunked", "hoax", "not true",
        "did not", "was not", "never happened"
    ]

    support_phrases = [
        "founded", "launched", "confirmed",
        "official", "reported", "established",
        "according to", "verified"
    ]

    for phrase in contradiction_phrases:
        contradiction_score += combined_text.count(phrase)

    for phrase in support_phrases:
        support_score += combined_text.count(phrase)

    # Year mismatch
    for year in claim_years:
        if year not in combined_text:
            contradiction_score += 2

    # Statistical plausibility
    scaled_values = normalize_large_numbers(claim)

    if "subscribers" in claim_lower:
        for value in scaled_values:
            if value > 1_500_000_000:
                contradiction_score += 3

    if "electric vehicles" in claim_lower:
        for value in scaled_values:
            if value > 100_000_000:
                contradiction_score += 3

    if "meters tall" in claim_lower:
        numeric_values = [int(val) for val in re.findall(r'\d+', claim)]
        if any(val > 800 for val in numeric_values):
            contradiction_score += 3

    if contradiction_score >= support_score + 2:
        return (
            "False",
            "Source evidence strongly contradicts the claim."
        )

    elif support_score > contradiction_score:
        return (
            "Verified",
            "Source evidence generally supports the claim."
        )

    else:
        return (
            "Inaccurate",
            "Claim may be partially true, outdated, or insufficiently supported."
        )


def search_claim_online(claim):
    """
    Uses Tavily AI search for live fact-checking.
    """

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": claim,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 5
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            return {
                "claim": claim,
                "status": "Error",
                "evidence": f"Tavily search failed with status code {response.status_code}.",
                "sources": []
            }

        data = response.json()

        answer = data.get("answer", "")
        results = data.get("results", [])

        if not results:
            return {
                "claim": claim,
                "status": "Inaccurate",
                "evidence": "No reliable evidence found.",
                "sources": []
            }

        snippets = []
        sources = []

        # Add Tavily answer
        if answer:
            snippets.append(answer)

        for result in results:
            snippet = result.get("content", "")
            title = result.get("title", "Unknown Source")
            link = result.get("url", "")

            if snippet:
                snippets.append(snippet)

            sources.append({
                "title": title,
                "url": link,
                "content": snippet
            })

        status, evidence = classify_claim(claim, snippets)

        return {
            "claim": claim,
            "status": status,
            "evidence": evidence,
            "sources": sources
        }

    except Exception as e:
        return {
            "claim": claim,
            "status": "Error",
            "evidence": f"Verification failed: {str(e)}",
            "sources": []
        }