import pandas as pd


def generate_fact_check_report(verification_results):
    """
    Converts verification results into a structured DataFrame report.

    Args:
        verification_results (list): List of dictionaries returned by web_verifier.

    Returns:
        pd.DataFrame: Structured fact-check report.
    """

    report_data = []

    for result in verification_results:
        claim = result.get("claim", "N/A")
        status = result.get("status", "Unknown")
        evidence = result.get("evidence", "No evidence available")

        sources = result.get("sources", [])
        source_links = []

        for source in sources:
            title = source.get("title", "Unknown Source")
            url = source.get("url", "")
            source_links.append(f"{title}: {url}")

        report_data.append({
            "Claim": claim,
            "Status": status,
            "Evidence": evidence,
            "Sources": "\n".join(source_links) if source_links else "No sources available"
        })

    df = pd.DataFrame(report_data)

    return df


def export_report_to_csv(df, filename="fact_check_report.csv"):
    """
    Exports the DataFrame report to CSV.

    Args:
        df (pd.DataFrame): Fact-check report.
        filename (str): Output CSV filename.

    Returns:
        str: Saved file path.
    """

    df.to_csv(filename, index=False)
    r