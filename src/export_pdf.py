from weasyprint import HTML
from io import BytesIO

def html_to_pdf_bytes(html_string: str) -> bytes:
    # This renders the HTML exactly as a browser would
    # but without the asyncio conflict
    pdf_file = HTML(string=html_string).write_pdf()
    return pdf_file