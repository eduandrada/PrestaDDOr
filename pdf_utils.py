from utils.notification import generate_loan_summary_html, create_pdf

def create_loan_pdf(loan):
    import tempfile, os
    data = loan.to_dict() if hasattr(loan, 'to_dict') else dict(loan)
    data['company_name'] = data.get('company_name', 'Gestión Préstamos')
    html = generate_loan_summary_html(data)
    fd, path = tempfile.mkstemp(suffix='.pdf'); os.close(fd)
    create_pdf(html, path)
    with open(path, 'rb') as f: content=f.read()
    os.unlink(path)
    return content

def create_custom_ai_report_pdf(title, text_body, company_name="Prestamos & Finanzas Familia Andrada", metadata=None):
    import tempfile, os
    from datetime import datetime
    
    meta_html = ""
    if metadata and isinstance(metadata, dict):
        meta_html = "<div style='margin-bottom: 15px; padding: 10px; background: #f1f5f9; border-radius: 8px; font-size: 12px;'>"
        for k, v in metadata.items():
            meta_html += f"<div><strong>{k}:</strong> {v}</div>"
        meta_html += "</div>"
        
    formatted_body = text_body.replace('\n', '<br>')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: Helvetica, Arial, sans-serif; margin: 30px; color: #1e293b; font-size: 13px; line-height: 1.6; }}
    .header {{ border-bottom: 2px solid #4f46e5; padding-bottom: 12px; margin-bottom: 20px; }}
    .title {{ font-size: 20px; font-weight: bold; color: #1e1b4b; margin: 0; }}
    .subtitle {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
    .content {{ background: #ffffff; padding: 15px 0; }}
    .footer {{ margin-top: 30px; border-top: 1px solid #e2e8f0; pt-8px; font-size: 10px; color: #94a3b8; text-align: center; }}
</style>
</head>
<body>
    <div class="header">
        <div class="title">📄 {title}</div>
        <div class="subtitle">{company_name} · Emisión Auditoría Contador Virtual IA ({datetime.now().strftime('%d/%m/%Y %H:%M')})</div>
    </div>
    {meta_html}
    <div class="content">
        {formatted_body}
    </div>
    <div class="footer">
        Este documento es un informe oficial emitido por el módulo de Auditoría Contable & Asesoría Financiera IA.
    </div>
</body>
</html>"""

    fd, path = tempfile.mkstemp(suffix='.pdf'); os.close(fd)
    create_pdf(html, path)
    with open(path, 'rb') as f: content=f.read()
    os.unlink(path)
    return content

