import streamlit as st
from claim_extractor import extract_text_from_pdf, extract_claims
from web_verifier import search_claim_online
from report_generator import generate_fact_check_report, export_report_to_csv


st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🔎",
    layout="wide"
)

st.title("Fact-Check Agent")
st.subheader("Upload a PDF and verify factual claims against live web data")

uploaded_file = st.file_uploader(
    "Upload PDF Document",
    type=["pdf"]
)

if uploaded_file is not None:
    st.info("Extracting text from PDF...")

    pdf_text = extract_text_from_pdf(uploaded_file)

    if not pdf_text:
        st.error("Failed to extract text from PDF.")
    else:
        st.success("PDF text extracted successfully.")

        st.info("Extracting factual claims...")
        claims = extract_claims(pdf_text)

        if not claims:
            st.warning("No factual claims detected.")
        else:
            st.success(f"Detected {len(claims)} claims.")

            st.write("### Extracted Claims")
            for i, claim in enumerate(claims, start=1):
                st.write(f"{i}. {claim}")

            if st.button("Run Fact Check"):
                verification_results = []

                progress_bar = st.progress(0)

                for idx, claim in enumerate(claims):
                    result = search_claim_online(claim)
                    verification_results.append(result)

                    progress = (idx + 1) / len(claims)
                    progress_bar.progress(progress)

                st.success("Fact-checking complete.")

                report_df = generate_fact_check_report(verification_results)

                st.write("## Fact-Check Report")
                st.dataframe(report_df, use_container_width=True)

                csv_file = export_report_to_csv(report_df)

                with open(csv_file, "rb") as file:
                    st.download_button(
                        label="Download CSV Report",
                        data=file,
                        file_name="fact_check_report.csv",
                        mime="text/csv"
                    )