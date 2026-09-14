import os
import html
import re
from datetime import datetime


def generate_loan_summary_html(loan_data):
    client = loan_data.get("client") or {}
    installments = loan_data.get("installments") or []
    rows = "".join(
        f"<tr><td>{i.get('number', idx + 1)}</td><td>{html.escape(str(i.get('due_date','')))}</td>"
        f"<td>${float(i.get('amount',0)):,.2f}</td><td>{html.escape(str(i.get('status','pendiente')))}</td></tr>"
        for idx, i in enumerate(installments)
    )
    return f"""<!doctype html><html lang='es'><head><meta charset='utf-8'>
    <style>
    @page {{ size:A4; margin:18mm; }} body {{ font-family:Arial,sans-serif;color:#172033;font-size:11px; }}
    .header {{ background:#075985;color:#fff;padding:20px;border-radius:12px; }} h1 {{ margin:0 0 5px; }}
    .grid {{ display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0; }} .card {{ border:1px solid #dbe3ee;border-radius:10px;padding:12px; }}
    table {{ width:100%;border-collapse:collapse;margin-top:15px; }} th,td {{ border-bottom:1px solid #e5e7eb;padding:7px;text-align:left; }} th {{ background:#eff6ff; }}
    .total {{ font-size:18px;font-weight:700;color:#075985; }} .muted {{ color:#64748b; }}
    </style></head><body>
    <div class='header'><h1>Comprobante de préstamo #{loan_data.get('id','')}</h1><div>{html.escape(str(loan_data.get('company_name','Gestión Préstamos')))}</div></div>
    <div class='grid'>
      <div class='card'><b>Cliente</b><p>{html.escape(str(client.get('name',loan_data.get('client_name',''))))}</p><p class='muted'>CUIT/CUIL: {html.escape(str(client.get('cuit',loan_data.get('client_cuit','')) or 'No informado'))}</p><p class='muted'>Teléfono: {html.escape(str(client.get('whatsapp',loan_data.get('client_whatsapp','')) or 'No informado'))}</p></div>
      <div class='card'><b>Condiciones</b><p>Capital: <span class='total'>${float(loan_data.get('amount',0)):,.2f}</span></p><p>Tasa: {loan_data.get('interest_rate',0)}% · {html.escape(str(loan_data.get('rate_type','mensual')))}</p><p>Modalidad: {html.escape(str(loan_data.get('modality','mensual')))} · {loan_data.get('installments_count',1)} cuotas</p></div>
    </div>
    <p><b>Total a devolver:</b> ${float(loan_data.get('total_loan_amount',0)):,.2f} &nbsp; <b>Saldo:</b> ${float(loan_data.get('remaining_balance',0)):,.2f}</p>
    <table><thead><tr><th>#</th><th>Vencimiento</th><th>Importe</th><th>Estado</th></tr></thead><tbody>{rows}</tbody></table>
    <p class='muted'>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}.</p>
    </body></html>"""


def create_pdf(html_content, output_path):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    try:
        from weasyprint import HTML
        HTML(string=html_content, base_url=os.getcwd()).write_pdf(output_path)
        return output_path
    except Exception as exc:
        # ReportLab fallback keeps the feature usable on minimal installations.
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        y = height - 20 * mm
        c.setFont('Helvetica-Bold', 14)
        c.drawString(18 * mm, y, 'Comprobante de préstamo')
        y -= 10 * mm
        c.setFont('Helvetica', 8)
        for line in re.sub(r'<[^>]+>', ' ', html_content).splitlines():
            text = ' '.join(line.split())
            if not text: continue
            c.drawString(18 * mm, y, text[:120])
            y -= 5 * mm
            if y < 15 * mm:
                c.showPage(); y = height - 20 * mm
        c.save()
        return output_path


def send_whatsapp(message, phone_number):
    sid = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
    token = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
    sender = os.getenv('TWILIO_WHATSAPP_FROM', '').strip()
    if not sid or not token or not sender:
        raise RuntimeError('Credenciales de Twilio incompletas. Configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y TWILIO_WHATSAPP_FROM.')
    try:
        from twilio.rest import Client as TwilioClient
    except ImportError as exc:
        raise RuntimeError('La dependencia twilio no está instalada.') from exc
    to = str(phone_number or '').strip()
    if not to.startswith('whatsapp:'):
        to = f'whatsapp:{to}'
    client = TwilioClient(sid, token)
    msg = client.messages.create(body=message, from_=sender if sender.startswith('whatsapp:') else f'whatsapp:{sender}', to=to)
    return {'sid': msg.sid, 'status': getattr(msg, 'status', 'queued')}


def generate_loan_message(loan_data):
    client = loan_data.get('client') or {}
    name = client.get('name') or loan_data.get('client_name') or 'Cliente'
    total = float(loan_data.get('total_loan_amount') or 0)
    amount = float(loan_data.get('amount') or 0)
    rate = loan_data.get('interest_rate', 0)
    modality = loan_data.get('modality', 'mensual')
    count = loan_data.get('installments_count', 1)
    company = loan_data.get('company_name', 'Gestión Préstamos')
    fallback = (f"Hola {name}, te informamos que tu préstamo por ${amount:,.2f} fue otorgado. "
                f"La operación contempla {count} cuota(s), modalidad {modality}, tasa {rate}% y un total estimado a devolver de ${total:,.2f}. "
                f"Gracias por confiar en {company}.")
    api_key = os.getenv('GOOGLE_API_KEY', '').strip()
    if not api_key:
        return fallback
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(os.getenv('GOOGLE_GEMINI_MODEL', 'gemini-1.5-flash'))
        prompt = ("Redacta un mensaje breve, profesional y cordial para WhatsApp en español argentino. "
                  "No inventes datos. Usa exactamente estos datos del préstamo:\n" + str(loan_data) +
                  "\nNo agregues recomendaciones financieras ni información que no figure en los datos.")
        response = model.generate_content(prompt)
        text = getattr(response, 'text', '') or ''
        return text.strip() or fallback
    except Exception:
        return fallback
