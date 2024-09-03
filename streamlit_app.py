import streamlit as st
from deskew_logic import deskew_pdf, deskew_image

st.title("Deskew tool")

uploaded_pdf = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_pdf is not None:
    # Step 1: Get the uploaded file's bytes
    pdf_bytes = uploaded_pdf.read()

    # Step 2: Run the deskew function on the PDF
    deskewed_pdf_bytes = deskew_pdf(pdf_bytes)

    # Step 3: Set up the download button for the deskewed PDF
    st.download_button(
        label="Download Deskewed PDF",
        data=deskewed_pdf_bytes,  # Provide the deskewed PDF's bytes
        file_name=f'{str(uploaded_pdf.name).replace(".pdf","")}_deskewed.pdf',  # Specify the filename
        mime="application/pdf"  # Set the MIME type for PDF
    )
