import subprocess
from PIL import Image
from pdf2image import convert_from_bytes
from io import BytesIO
import tempfile
import streamlit as st
from PyPDF2 import PdfFileWriter


def deskew_with_unpaper(image_bytes):
    # Create a temporary input file for unpaper
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_input:
        temp_input.write(image_bytes)
        temp_input_path = temp_input.name

    # Generate a unique temporary output file name without pre-creating it
    temp_output_path = tempfile.mktemp(suffix=".png")

    # Run unpaper with the --overwrite flag to deskew the image
    subprocess.run(['unpaper', '--overwrite', '--no-noise-scan', temp_input_path, temp_output_path])

    # Read the processed (deskewed) image bytes
    with open(temp_output_path, 'rb') as f:
        deskewed_image_bytes = f.read()

    return deskewed_image_bytes


def process_pdf(input_pdf_bytes):
    # Convert the PDF to images
    images = convert_from_bytes(input_pdf_bytes)
    processed_images = []

    # Deskew each image using unpaper
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        processed_image_bytes = deskew_with_unpaper(image_bytes)
        processed_images.append(Image.open(BytesIO(processed_image_bytes)))

    # Convert processed images back to a PDF
    output_pdf = BytesIO()
    processed_images[0].save(output_pdf, format='PDF', save_all=True, append_images=processed_images[1:])
    return output_pdf.getvalue()


def main():
    st.title("PDF Deskewing Tool with unpaper")

    # File uploader for PDF
    uploaded_pdf = st.file_uploader("Upload your PDF file", type="pdf")

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.read()
        with st.spinner('Processing the PDF with unpaper...'):
            # Process the uploaded PDF
            processed_pdf_bytes = process_pdf(pdf_bytes)
        st.success('PDF processed successfully!')

        # Provide the download button for the deskewed PDF
        st.download_button(
            label="Download Deskewed PDF",
            data=processed_pdf_bytes,
            file_name=f'{str(uploaded_pdf.name).replace(".pdf", "")}_deskewed.pdf',
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()
