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
