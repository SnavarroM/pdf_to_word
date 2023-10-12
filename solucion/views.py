import os
from PyPDF2 import PdfReader
from docx import Document
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.http import FileResponse

def pdf_to_word(file):
    pdf = PdfReader(file)
    doc = Document()
    for page in pdf.pages:
        page_content = page.extract_text()
        doc.add_paragraph(page_content)
    output_file_name = os.path.splitext(file.name)[0] + '.docx'
    output_file_path = os.path.join(settings.MEDIA_ROOT, output_file_name)
    doc.save(output_file_path)
    return output_file_path

def delete_docx_files():
    media_root = settings.MEDIA_ROOT
    for filename in os.listdir(media_root):
        if filename.endswith('.docx'):
            file_path = os.path.join(media_root, filename)
            try:
                os.remove(file_path)
            except OSError as e:
                # Manejar la excepción si no se puede eliminar el archivo
                print(f"No se pudo eliminar el archivo: {file_path}\n{e}")

def index(request):
    converted_file = None
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        converted_file = pdf_to_word(pdf_file)
        converted_file_name = os.path.basename(converted_file)
        cache.clear()
        response = FileResponse(open(converted_file, 'rb'), as_attachment=True, filename=converted_file_name)
        try:
            # Eliminar el archivo .docx después de enviarlo a la vista HTML
            os.remove(converted_file)
        except OSError as e:
            # Manejar la excepción si no se puede eliminar el archivo
            print(f"No se pudo eliminar el archivo: {converted_file}\n{e}")
        delete_docx_files()  # Llamar a la función para eliminar los archivos .docx
        return response
    return render(request, 'solucion/index.html', {'converted_file': converted_file})