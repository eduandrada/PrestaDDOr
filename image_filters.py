import io
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

def apply_document_clean_filter(img: Image.Image) -> Image.Image:
    """Filtro Aclarado Documental (CamScanner B&W Fotocopia Nítida).
    Convierte fotos oscuras o con sombras de pagarés/recibos a grises de alto contraste,
    blanqueando el fondo y oscureciendo el texto.
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    gray = img.convert('L')
    auto = ImageOps.autocontrast(gray, cutoff=2)
    high_contrast = ImageEnhance.Contrast(auto).enhance(2.2)
    brightener = ImageEnhance.Brightness(high_contrast).enhance(1.25)
    sharpened = brightener.filter(ImageFilter.SHARPEN)
    return sharpened.convert('RGB')


def apply_color_enhance_filter(img: Image.Image) -> Image.Image:
    """Filtro Color Realzado (Original Nítido).
    Realza los colores, el contraste y la nitidez manteniendo los colores originales de la imagen.
    """
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    auto = ImageOps.autocontrast(img, cutoff=1)
    color_boost = ImageEnhance.Color(auto).enhance(1.35)
    contrast_boost = ImageEnhance.Contrast(color_boost).enhance(1.2)
    sharpened = contrast_boost.filter(ImageFilter.SHARPEN)
    return sharpened


def compress_pdf_in_ram(pdf_bytes: bytes, target_max_bytes: int = 1024 * 1024) -> tuple:
    """Comprime un archivo PDF en RAM para reducir su peso a menos de 1 MB.
    Retorna (res_bytes, original_size, compressed_size).
    """
    original_size = len(pdf_bytes)
    if original_size <= target_max_bytes or original_size == 0:
        return pdf_bytes, original_size, original_size

    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        images = []
        
        for page in reader.pages:
            for img_obj in page.images:
                try:
                    img = Image.open(io.BytesIO(img_obj.data))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    max_dim = 1400
                    if img.width > max_dim or img.height > max_dim:
                        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                    images.append(img)
                except Exception:
                    pass

        if images:
            for q in [65, 50, 40, 30]:
                out_io = io.BytesIO()
                images[0].save(out_io, 'PDF', save_all=True, append_images=images[1:], quality=q, optimize=True)
                res_bytes = out_io.getvalue()
                if len(res_bytes) <= target_max_bytes or q == 30:
                    return res_bytes, original_size, len(res_bytes)

        # Fallback con pypdf compresion de flujos
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        out_io = io.BytesIO()
        writer.write(out_io)
        res_bytes = out_io.getvalue()
        return res_bytes, original_size, len(res_bytes)

    except Exception as e:
        print(f"Error comprimiendo PDF en RAM: {e}")
        return pdf_bytes, original_size, original_size
