import os
import json
import csv
import io
import uuid
import urllib.request
from datetime import datetime, date, timedelta
from flask import Flask, render_template, render_template_string, request, jsonify, send_file, Response, make_response
from models import db, Client, Loan, Installment, Payment, Expense, Setting, ClientDocument, PersonalBill, BiometricRequest, Raffle, ShoppingItem, NoticeBoardItem, HomeCalendarItem

app = Flask(__name__)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database.db')).replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'prestamos_secret_key_2026'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.context_processor
def inject_cache_buster():
    import time
    return dict(v=int(time.time()))

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

db.init_app(app)

# Helper for initial settings & seed data
def init_db_and_seeds():
    db.create_all()
    # Migration: Ensure new columns exist in personal_bills table
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE personal_bills ADD COLUMN owner VARCHAR(50) DEFAULT 'Compartido'"))
            conn.commit()
    except Exception:
        pass
    
    for col_def in [
        ("month", "INTEGER DEFAULT 9"),
        ("year", "INTEGER DEFAULT 2026"),
        ("installments_count", "INTEGER DEFAULT 1"),
        ("current_installment", "INTEGER DEFAULT 1"),
        ("is_recurring", "BOOLEAN DEFAULT 1")
    ]:
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text(f"ALTER TABLE personal_bills ADD COLUMN {col_def[0]} {col_def[1]}"))
                conn.commit()
        except Exception:
            pass


    # Default settings if empty or update default company name
    if not Setting.query.filter_by(key='company_name').first():
        Setting.set_val('company_name', 'Prestamos & Finanzas Familia Andrada')
    if not Setting.query.filter_by(key='alias_cbu').first():
        Setting.set_val('alias_cbu', 'FAMILIA.ANDRADA.MP')
    if not Setting.query.filter_by(key='qr_text').first():
        Setting.set_val('qr_text', 'CVU: 0000003100045678912345 | Alias: FAMILIA.ANDRADA.MP')
    if not Setting.query.filter_by(key='company_cuit').first():
        Setting.set_val('company_cuit', '20-33445566-9')
    if not Setting.query.filter_by(key='company_bank').first():
        Setting.set_val('company_bank', 'Mercado Pago / Banco Santander')
    if not Setting.query.filter_by(key='company_titular').first():
        Setting.set_val('company_titular', 'Eduardo Andrada')
    if not Setting.query.filter_by(key='company_phone').first():
        Setting.set_val('company_phone', '+54 9 11 3344-5566')
    if not Setting.query.filter_by(key='company_address').first():
        Setting.set_val('company_address', 'Av. Corrientes 1234, CABA')
    if not Setting.query.filter_by(key='default_grace_days').first():
        Setting.set_val('default_grace_days', '3')
    if not Setting.query.filter_by(key='default_late_fee').first():
        Setting.set_val('default_late_fee', '1.0')
    if not Setting.query.filter_by(key='ant_expense_threshold').first():
        Setting.set_val('ant_expense_threshold', '2500')
    if not Setting.query.filter_by(key='user_salary_eduardo').first():
        Setting.set_val('user_salary_eduardo', '550000')
    if not Setting.query.filter_by(key='user_salary_maira').first():
        Setting.set_val('user_salary_maira', '450000')

    # Seed sample personal bills if empty
    if PersonalBill.query.count() == 0:
        b1 = PersonalBill(name="Tarjeta Visa Santander", category="tarjeta", owner="Eduardo", amount=145000.0, due_day=10, status="pendiente", notes="Pago mínimo $35.000 - Eduardo")
        b2 = PersonalBill(name="Tarjeta Mastercard BBVA", category="tarjeta", owner="Maira", amount=88500.0, due_day=18, status="pendiente", notes="Cierre día 28 - Maira")
        b3 = PersonalBill(name="Servicio Luz Edesur", category="servicio", owner="Compartido", amount=24000.0, due_day=12, status="pendiente", notes="Factura Bimestral Compartida")
        b4 = PersonalBill(name="Internet & Cable Personal Flow", category="servicio", owner="Compartido", amount=19500.0, due_day=15, status="pagado", notes="Débito automático Compartido")
        b5 = PersonalBill(name="Telefonía Móvil Movistar", category="servicio", owner="Eduardo", amount=12800.0, due_day=22, status="pendiente", notes="Plan Eduardo")
        b6 = PersonalBill(name="Alquiler & Expensas Dpto", category="fijo", owner="Compartido", amount=230000.0, due_day=5, status="pagado", notes="Transferencia titular")
        db.session.add_all([b1, b2, b3, b4, b5, b6])
        db.session.commit()

    if Raffle.query.count() == 0:
        r1 = Raffle(
            title="Gran Rifa Aniversario Familia",
            motive="Fondo para Viaje de Fin de Año & Equipamiento",
            mode="numbers",
            number_min=1,
            number_max=100,
            ticket_price=1500.0,
            prizes_json=json.dumps([{"rank": 1, "name": "1° Premio: Asado Completo + Vino Reserva"}, {"rank": 2, "name": "2° Premio: Postre Helado + Sidra"}]),
            participants_json=json.dumps(["Juan Pérez", "María Gómez", "Roberto Fernández", "Eduardo Andrada", "Maira Fernández", "Carlos López", "Ana Martínez"]),
            status="activo",
            draw_date="2026-09-20"
        )
        db.session.add(r1)
        db.session.commit()

    if ShoppingItem.query.count() == 0:
        s1 = ShoppingItem(store_category="supermercado", item_name="Leche entera 1L", quantity="2 sachet", is_checked=False, added_by="Maira")
        s2 = ShoppingItem(store_category="supermercado", item_name="Detergente vajilla", quantity="1 botella", is_checked=True, added_by="Eduardo")
        s3 = ShoppingItem(store_category="verduleria", item_name="Tomates perita", quantity="1.5 kg", is_checked=False, added_by="Maira")
        s4 = ShoppingItem(store_category="ferreteria", item_name="Cinta aisladora negra", quantity="1 rollo", is_checked=False, added_by="Eduardo")
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

    if NoticeBoardItem.query.count() == 0:
        n1 = NoticeBoardItem(author="Eduardo", message="¡Hola! Hoy llego a casa a las 20:00 hs aprox.", is_pinned=True)
        n2 = NoticeBoardItem(author="Maira", message="Dejé comida en la heladera para calentar.", is_pinned=False)
        db.session.add_all([n1, n2])
        db.session.commit()

    if HomeCalendarItem.query.count() == 0:
        c1 = HomeCalendarItem(title="Turno Odontólogo Maira", category="medico", due_date=date.today().strftime("%Y-%m-%d"), due_time="17:00", notes="Dr. Rodríguez - Av. Mayo 450", is_completed=False)
        c2 = HomeCalendarItem(title="Vacuna Anual Mascota (Firulais)", category="mascota", due_date=(date.today() + timedelta(days=5)).strftime("%Y-%m-%d"), due_time="11:00", notes="Veterinaria San Bernardo", is_completed=False)
        c3 = HomeCalendarItem(title="Vencimiento Factura Edesur", category="servicio", due_date=(date.today() + timedelta(days=3)).strftime("%Y-%m-%d"), due_time="12:00", notes="Monto: $24.000", is_completed=False)
        db.session.add_all([c1, c2, c3])
        db.session.commit()
    # Seed initial demo clients if database is completely empty
    if Client.query.count() == 0:
        c1 = Client(name="Juan Carlos Pérez", whatsapp="5491155443322", email="juan.perez@email.com", address="Av. Corrientes 1234, CABA", notes="Cliente recurrente Familia Andrada, excelente puntualidad.")
        c2 = Client(name="María Elena Gómez", whatsapp="5491166778899", email="maria.gomez@email.com", address="Calle Florida 456, CABA", notes="Prefiere pago quincenal por transferencia.")
        c3 = Client(name="Roberto Fernández", whatsapp="5491133221100", email="roberto.f@email.com", address="Belgrano 789, CABA", notes="Suele pagar en el período de gracia.")
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Seed loans
        l1 = Loan(
            client_id=c1.id, amount=100000.0, interest_rate=15.0, rate_type='mensual',
            modality='mensual', installments_count=4, start_date=date.today() - timedelta(days=45),
            status='activo', grace_days=3, late_fee_type='porcentaje', late_fee_value=1.0, notes="Préstamo P2P - Personal"
        )
        l2 = Loan(
            client_id=c2.id, amount=50000.0, interest_rate=10.0, rate_type='mensual',
            modality='quincenal', installments_count=2, start_date=date.today() - timedelta(days=20),
            status='activo', grace_days=3, late_fee_type='monto_fijo', late_fee_value=500.0, notes="Capital de trabajo Social Lending"
        )
        db.session.add_all([l1, l2])
        db.session.commit()

        # Generate amortization schedules
        l1_insts = l1.generate_amortization_schedule()
        l2_insts = l2.generate_amortization_schedule()
        db.session.add_all(l1_insts + l2_insts)
        db.session.commit()

        # Mark first installment of L1 as paid
        l1_insts[0].paid_amount = l1_insts[0].amount
        l1_insts[0].status = 'pagado'
        l1_insts[0].paid_date = date.today() - timedelta(days=15)
        
        pay1 = Payment(
            installment_id=l1_insts[0].id, loan_id=l1.id, client_id=c1.id,
            amount=l1_insts[0].amount, payment_date=datetime.now() - timedelta(days=15),
            payment_method='Transferencia', notes='Cuota 1 saldada', receipt_number='REC-20260901-0001'
        )
        db.session.add(pay1)

        # Seed expenses
        e1 = Expense(category='Fijo', description='Suscripción software contable', amount=12000.0, date=date.today() - timedelta(days=10), is_ant_expense=False)
        e2 = Expense(category='Variable', description='Impresión de talonarios y papelería', amount=8500.0, date=date.today() - timedelta(days=8), is_ant_expense=False)
        e3 = Expense(category='Extraordinario', description='Café y refrigerios en reunión con clientes', amount=1800.0, date=date.today() - timedelta(days=5), is_ant_expense=True)
        e4 = Expense(category='Variable', description='Taxi/Comisión cobro a domicilio', amount=2200.0, date=date.today() - timedelta(days=2), is_ant_expense=True)
        db.session.add_all([e1, e2, e3, e4])
        db.session.commit()


_db_initialized = False

@app.before_request
def ensure_db_initialized():
    global _db_initialized
    if not _db_initialized:
        init_db_and_seeds()
        _db_initialized = True


@app.route('/')
def index():
    return render_template('index.html')


# Global in-memory cache for dollar rates
_dolar_cache = {
    'timestamp': None,
    'data': None
}

@app.route('/api/dolar-rates', methods=['GET'])
def get_dolar_rates():
    global _dolar_cache
    force = request.args.get('force', 'false').lower() == 'true'
    now = datetime.now()
    
    if not force and _dolar_cache['timestamp'] and (now - _dolar_cache['timestamp']).total_seconds() < 300:
        return jsonify(_dolar_cache['data'])
    
    rates = {}
    try:
        req = urllib.request.Request('https://dolarapi.com/v1/dolares', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for item in data:
                casa = item.get('casa', '').lower()
                compra = float(item.get('compra') or 0.0)
                venta = float(item.get('venta') or 0.0)
                promedio = round((compra + venta) / 2.0, 2) if (compra and venta) else (venta or compra)
                fecha = item.get('fechaActualizacion', '')
                
                if casa in ['oficial', 'blue', 'tarjeta', 'bolsa', 'contadoconliqui']:
                    rates[casa] = {
                        'nombre': item.get('nombre', casa.capitalize()),
                        'compra': compra,
                        'venta': venta,
                        'promedio': promedio,
                        'fecha': fecha
                    }
    except Exception as e:
        print(f"Error fetching from DolarApi: {e}")
    
    if 'oficial' not in rates or 'blue' not in rates:
        try:
            req = urllib.request.Request('https://api.bluelytics.com.ar/v2/latest', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                b_data = json.loads(resp.read().decode('utf-8'))
                if 'oficial' not in rates and 'oficial' in b_data:
                    c = float(b_data['oficial'].get('value_buy', 0))
                    v = float(b_data['oficial'].get('value_sell', 0))
                    rates['oficial'] = {'nombre': 'Dólar Oficial (BNA)', 'compra': c, 'venta': v, 'promedio': round((c+v)/2, 2), 'fecha': b_data.get('last_update', '')}
                if 'blue' not in rates and 'blue' in b_data:
                    c = float(b_data['blue'].get('value_buy', 0))
                    v = float(b_data['blue'].get('value_sell', 0))
                    rates['blue'] = {'nombre': 'Dólar Blue', 'compra': c, 'venta': v, 'promedio': round((c+v)/2, 2), 'fecha': b_data.get('last_update', '')}
        except Exception as e2:
            print(f"Error fetching from Bluelytics fallback: {e2}")

    if 'oficial' not in rates:
        rates['oficial'] = {'nombre': 'Dólar Oficial (BNA)', 'compra': 1380.0, 'venta': 1420.0, 'promedio': 1400.0, 'fecha': now.isoformat()}
    if 'blue' not in rates:
        rates['blue'] = {'nombre': 'Dólar Blue', 'compra': 1450.0, 'venta': 1470.0, 'promedio': 1460.0, 'fecha': now.isoformat()}
    if 'tarjeta' not in rates:
        of_v = rates['oficial']['venta']
        rates['tarjeta'] = {'nombre': 'Dólar Tarjeta (BNA + Imp.)', 'compra': round(of_v * 1.30, 2), 'venta': round(of_v * 1.60, 2), 'promedio': round(of_v * 1.45, 2), 'fecha': now.isoformat()}

    res_payload = {
        'success': True,
        'last_updated': now.strftime('%d/%m/%Y %H:%M:%S'),
        'rates': rates
    }
    _dolar_cache['timestamp'] = now
    _dolar_cache['data'] = res_payload
    return jsonify(res_payload)


# ----------------------------------------------------
# API DASHBOARD & METRICS
# ----------------------------------------------------
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    loans = Loan.query.all()
    installments = Installment.query.all()
    payments = Payment.query.all()
    expenses = Expense.query.all()

    active_loans = [l for l in loans if l.status == 'activo']
    
    # 3-BOX FINANCIAL SEGREGATION
    # 1. Capital en calle (Capital propio pendiente de recuperar en prestamos activos)
    capital_en_calle = sum(
        sum(max(0.0, inst.capital_portion - min(inst.capital_portion, inst.paid_amount)) for inst in l.installments if inst.status != 'pagado')
        for l in active_loans
    )
    # 2. Intereses / Ganancias a cobrar (Intereses proyectados no cobrados aun)
    intereses_a_cobrar = sum(
        sum(max(0.0, inst.interest_portion - max(0.0, inst.paid_amount - inst.capital_portion)) for inst in l.installments if inst.status != 'pagado')
        for l in active_loans
    )
    # 3. Ganancia líquida ya cobrada en el mes actual
    ganancia_liquida_mes = sum(
        (p.installment.interest_portion if p.installment else p.amount * 0.2) 
        for p in payments if p.payment_date.date() >= first_day_of_month
    )

    deployed_capital = sum(l.amount for l in active_loans)
    
    total_interest_collected = sum(
        (p.installment.interest_portion if p.installment else p.amount * 0.2) 
        for p in payments
    )
    total_capital_recovered = sum(
        (p.installment.capital_portion if p.installment else p.amount * 0.8) 
        for p in payments
    )

    total_expenses = sum(e.amount for e in expenses)
    fixed_expenses = sum(e.amount for e in expenses if e.category == 'Fijo')
    ant_expenses = sum(e.amount for e in expenses if e.is_ant_expense)

    net_yield = total_interest_collected - total_expenses
    roi = (net_yield / max(1.0, deployed_capital)) * 100.0 if deployed_capital > 0 else 0.0
    real_rate = ((total_interest_collected - fixed_expenses) / max(1.0, deployed_capital)) * 100.0 if deployed_capital > 0 else 0.0

    # Real-Time Mora Metrics
    total_inst_count = len(installments)
    overdue_inst_count = 0
    
    # Alerts calculation
    alerts = []
    for inst in installments:
        if inst.status != 'pagado':
            grace_days = inst.loan.grace_days or 0
            days_diff = (today - inst.due_date).days
            
            if days_diff > grace_days:
                overdue_inst_count += 1
                alerts.append({
                    "type": "overdue",
                    "badge": "En Mora Crítica",
                    "color": "rose",
                    "client": inst.loan.client.name,
                    "whatsapp": inst.loan.client.whatsapp,
                    "installment_id": inst.id,
                    "due_date": inst.due_date.strftime("%Y-%m-%d"),
                    "amount": inst.amount + inst.calculate_late_fee(),
                    "message": f"Cuota #{inst.number} vencida hace {days_diff} días con recargo acumulado."
                })
            elif days_diff == 0:
                alerts.append({
                    "type": "today",
                    "badge": "Vence Hoy",
                    "color": "amber",
                    "client": inst.loan.client.name,
                    "whatsapp": inst.loan.client.whatsapp,
                    "installment_id": inst.id,
                    "due_date": inst.due_date.strftime("%Y-%m-%d"),
                    "amount": inst.amount,
                    "message": f"La cuota #{inst.number} de ${inst.amount:,.2f} vence HOY."
                })
            elif days_diff == -2:
                alerts.append({
                    "type": "preventive",
                    "badge": "Requiere Aviso T-2",
                    "color": "blue",
                    "client": inst.loan.client.name,
                    "whatsapp": inst.loan.client.whatsapp,
                    "installment_id": inst.id,
                    "due_date": inst.due_date.strftime("%Y-%m-%d"),
                    "amount": inst.amount,
                    "message": f"Recordatorio preventivo: la cuota #{inst.number} vence en 2 días."
                })

    mora_percentage = round((overdue_inst_count / max(1, total_inst_count)) * 100.0, 1)

    # Expense breakdown by category for doughnut chart
    expenses_by_cat = {
        "Fijo": sum(e.amount for e in expenses if e.category == 'Fijo'),
        "Variable": sum(e.amount for e in expenses if e.category == 'Variable'),
        "Extraordinario": sum(e.amount for e in expenses if e.category == 'Extraordinario')
    }

    return jsonify({
        # 3-Box Financial Breakdown
        "capital_en_calle": round(capital_en_calle, 2),
        "intereses_a_cobrar": round(intereses_a_cobrar, 2),
        "ganancia_liquida_mes": round(ganancia_liquida_mes, 2),
        
        "deployed_capital": round(deployed_capital, 2),
        "total_interest_collected": round(total_interest_collected, 2),
        "total_capital_recovered": round(total_capital_recovered, 2),
        "total_expenses": round(total_expenses, 2),
        "fixed_expenses": round(fixed_expenses, 2),
        "ant_expenses": round(ant_expenses, 2),
        "ant_expenses_count": len([e for e in expenses if e.is_ant_expense]),
        "net_yield": round(net_yield, 2),
        "roi_percentage": round(roi, 2),
        "real_rate_percentage": round(real_rate, 2),
        "mora_percentage": mora_percentage,
        "overdue_inst_count": overdue_inst_count,
        "total_inst_count": total_inst_count,
        "alerts": alerts,
        "expenses_by_cat": expenses_by_cat,
        "clients_count": Client.query.count(),
        "active_loans_count": len(active_loans),
        "completed_loans_count": len([l for l in loans if l.status == 'completado'])
    })


# ----------------------------------------------------
# API CLIENTS
# ----------------------------------------------------
@app.route('/api/clients', methods=['GET', 'POST'])
def handle_clients():
    if request.method == 'POST':
        data = request.json
        client = Client(
            name=data['name'].strip(),
            whatsapp=data['whatsapp'].strip(),
            email=data.get('email', '').strip(),
            address=data.get('address', '').strip(),
            notes=data.get('notes', '').strip()
        )
        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201
    
    clients = Client.query.order_by(Client.name).all()
    return jsonify([c.to_dict() for c in clients])


@app.route('/api/clients/<int:client_id>', methods=['PUT', 'DELETE'])
def handle_single_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'DELETE':
        db.session.delete(client)
        db.session.commit()
        return jsonify({"success": True})
    
    data = request.json
    client.name = data.get('name', client.name).strip()
    client.whatsapp = data.get('whatsapp', client.whatsapp).strip()
    client.email = data.get('email', client.email).strip()
    client.address = data.get('address', client.address).strip()
    client.notes = data.get('notes', client.notes).strip()
    db.session.commit()
    return jsonify(client.to_dict())


@app.route('/api/clients/<int:client_id>/vcard', methods=['GET'])
def download_vcard(client_id):
    client = Client.query.get_or_404(client_id)
    vcard_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{client.name}
TEL;TYPE=CELL:+{client.whatsapp}
EMAIL:{client.email or ''}
ADR;TYPE=HOME:;;{client.address or ''};;;;
NOTE:Cliente Préstamos - {client.notes or ''}
END:VCARD"""
    
    response = make_response(vcard_content)
    response.headers["Content-Disposition"] = f"attachment; filename=Contacto_{client.name.replace(' ', '_')}.vcf"
    response.headers["Content-Type"] = "text/vcard; charset=utf-8"
    return response


@app.route('/api/clients/<int:client_id>/documents', methods=['GET', 'POST'])
def handle_client_documents(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        data = request.json
        doc = ClientDocument(
            client_id=client.id,
            loan_id=data.get('loan_id'),
            doc_type=data.get('doc_type', 'otro'),
            title=data.get('title', 'Documento').strip(),
            image_data=data['image_data']
        )
        db.session.add(doc)
        db.session.commit()
        return jsonify(doc.to_dict()), 201
    
    docs = ClientDocument.query.filter_by(client_id=client_id).order_by(ClientDocument.created_at.desc()).all()
    return jsonify([d.to_dict() for d in docs])


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    doc = ClientDocument.query.get_or_404(doc_id)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"success": True})



@app.route('/api/clients/<int:client_id>/history', methods=['GET'])
def get_client_history(client_id):
    client = Client.query.get_or_404(client_id)
    client_dict = client.to_dict()
    
    loans_history = [l.to_dict() for l in client.loans]
    total_borrowed = sum(l.amount for l in client.loans)
    total_paid = sum(l.to_dict()["total_paid"] for l in client.loans)
    total_interest_paid = sum(sum(i.interest_portion for i in l.installments if i.status == 'pagado') for l in client.loans)

    return jsonify({
        "client": client_dict,
        "loans": loans_history,
        "total_borrowed": round(total_borrowed, 2),
        "total_paid": round(total_paid, 2),
        "total_interest_paid": round(total_interest_paid, 2)
    })


# ----------------------------------------------------
# API LOANS
# ----------------------------------------------------
@app.route('/api/loans', methods=['GET', 'POST'])
def handle_loans():
    if request.method == 'POST':
        data = request.json
        start_d = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data and data['start_date'] else date.today()
        
        loan = Loan(
            client_id=int(data['client_id']),
            amount=float(data['amount']),
            interest_rate=float(data['interest_rate']),
            rate_type=data.get('rate_type', 'mensual'),
            modality=data.get('modality', 'mensual'),
            installments_count=int(data.get('installments_count', 1)),
            start_date=start_d,
            grace_days=int(data.get('grace_days', 3)),
            late_fee_type=data.get('late_fee_type', 'porcentaje'),
            late_fee_value=float(data.get('late_fee_value', 1.0)),
            notes=data.get('notes', '').strip(),
            signature_data=data.get('signature_data', '')
        )
        db.session.add(loan)
        db.session.commit()

        # Generate Amortization Schedule
        schedule = loan.generate_amortization_schedule()
        db.session.add_all(schedule)
        db.session.commit()

        # Si el préstamo fue otorgado/activo, eliminar solicitudes de QR Express del cliente
        if loan.status in ['activo', 'otorgado']:
            BiometricRequest.query.filter_by(client_id=loan.client_id).delete()
            db.session.commit()

        return jsonify(loan.to_dict()), 201

    loans = Loan.query.order_by(Loan.id.desc()).all()
    return jsonify([l.to_dict() for l in loans])


@app.route('/api/loans/<int:loan_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if request.method == 'DELETE':
        db.session.delete(loan)
        db.session.commit()
        return jsonify({"success": True})
    elif request.method == 'PUT':
        data = request.json or {}
        if 'notes' in data:
            loan.notes = data['notes'].strip()
        if 'grace_days' in data:
            loan.grace_days = int(data['grace_days'])
        if 'late_fee_type' in data:
            loan.late_fee_type = data['late_fee_type']
        if 'late_fee_value' in data:
            loan.late_fee_value = float(data['late_fee_value'])
        if 'status' in data:
            loan.status = data['status']
            if data['status'] in ['activo', 'otorgado']:
                # Otorgado -> Eliminar automáticamente el QR Express del cliente
                BiometricRequest.query.filter_by(client_id=loan.client_id).delete()
        db.session.commit()
        return jsonify(loan.to_dict())
    return jsonify(loan.to_dict())


@app.route('/api/loans/<int:loan_id>/pagare_pdf', methods=['GET'])
def generate_pagare_pdf(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    company = Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada')
    client = loan.client
    
    total_amount = sum(i.amount for i in loan.installments)
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contrato de Mutuo con Interés & Pagaré #{loan.id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; color: #1e293b; padding: 20px; margin: 0; }}
        .pagare-card {{ max-width: 800px; margin: 0 auto; background: #ffffff; border: 2px solid #0f172a; border-radius: 12px; padding: 35px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0; font-size: 24px; color: #0f172a; text-transform: uppercase; letter-spacing: 1px; }}
        .header p {{ margin: 5px 0 0 0; font-size: 14px; color: #64748b; font-weight: 600; }}
        .stamp {{ display: inline-block; background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-top: 10px; }}
        .legal-text {{ font-size: 15px; line-height: 1.7; text-align: justify; margin-bottom: 25px; color: #334155; }}
        .details-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; background: #f8fafc; padding: 18px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; }}
        .details-item {{ font-size: 14px; }}
        .details-item strong {{ color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
        th {{ background: #0f172a; color: #ffffff; text-transform: uppercase; font-size: 12px; }}
        .signatures {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 40px; padding-top: 20px; border-top: 1px dashed #cbd5e1; }}
        .sig-box {{ text-align: center; width: 45%; }}
        .sig-img {{ max-height: 90px; max-width: 100%; object-fit: contain; margin-bottom: 5px; }}
        .sig-line {{ border-top: 1px solid #0f172a; margin-top: 10px; padding-top: 5px; font-weight: bold; font-size: 13px; color: #0f172a; }}
        .footer-note {{ text-align: center; font-size: 11px; color: #94a3b8; margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 10px; }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .pagare-card {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 10px 24px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer;">🖨️ Imprimir / Guardar en PDF</button>
    </div>

    <div class="pagare-card">
        <div class="header">
            <h1>CONTRATO DE MUTUO CON INTERÉS & PAGARÉ DIGITAL</h1>
            <p>Mutuo con Interés</p>
            <span class="stamp">DOCUMENTO DIGITAL CON FIRMA BIOMÉTRICA</span>
        </div>

        <div class="legal-text">
            Por el presente <strong>CONTRATO DE MUTUO CON INTERÉS & PAGARÉ DIGITAL</strong>, el/la abajo firmante <strong>{client.name}</strong> (DNI/WhatsApp: +{client.whatsapp}), en adelante "EL DEUDOR / MUTUARIO", reconoce adeudar y se compromete incondicionalmente a pagar a la orden de <strong>Mutuo con Interés</strong>, en adelante "EL ACREEDOR / MUTUANTE", la suma total de <strong>${total_amount:,.2f} PESOS ARGENTINOS</strong>, correspondiente a la devolución del capital otorgado de ${loan.amount:,.2f} con una tasa de interés pactada de {loan.interest_rate}% ({loan.rate_type}), a ser abonado en <strong>{loan.installments_count} cuota(s) {loan.modality}s</strong> conforme al cronograma adjunto.
        </div>

        <div class="details-grid">
            <div class="details-item"><strong>N° Préstamo:</strong> P2P-{loan.id:05d}</div>
            <div class="details-item"><strong>Fecha Emisión:</strong> {loan.start_date.strftime("%d/%m/%Y")}</div>
            <div class="details-item"><strong>Monto Solicitado:</strong> ${loan.amount:,.2f}</div>
            <div class="details-item"><strong>Monto Total a Devolver:</strong> ${total_amount:,.2f}</div>
            <div class="details-item"><strong>Tasa de Interés:</strong> {loan.interest_rate}% ({loan.rate_type})</div>
            <div class="details-item"><strong>Recargo Mora:</strong> {loan.late_fee_value} ({loan.late_fee_type})</div>
        </div>

        <h3>CRONOGRAMA DE CUOTAS Y VENCIMIENTOS</h3>
        <table>
            <thead>
                <tr>
                    <th>N° Cuota</th>
                    <th>Vencimiento</th>
                    <th>Capital</th>
                    <th>Interés</th>
                    <th>Total Cuota</th>
                </tr>
            </thead>
            <tbody>"""
    
    for inst in loan.installments:
        html_content += f"""
                <tr>
                    <td>Cuota #{inst.number}</td>
                    <td>{inst.due_date.strftime("%d/%m/%Y")}</td>
                    <td>${inst.capital_portion:,.2f}</td>
                    <td>${inst.interest_portion:,.2f}</td>
                    <td><strong>${inst.amount:,.2f}</strong></td>
                </tr>"""

    sig_html = f'<img src="{loan.signature_data}" class="sig-img" alt="Firma Biometrica"/>' if loan.signature_data else '<div style="height: 60px; display:flex; align-items:center; justify-content:center; color:#94a3b8; font-style:italic;">Firma digital registrada electrónicamente</div>'

    html_content += f"""
            </tbody>
        </table>

        <div class="legal-text" style="font-size: 12px; color: #64748b; margin-top: 15px;">
            El mora de cualquiera de las cuotas dará derecho al Acreedor a exigir el pago total de la deuda pendiente más los punitorios configurados ({loan.late_fee_value} {loan.late_fee_type}). Ambas partes acuerdan la validez de las notificaciones digitales vía WhatsApp o medios electrónicos informados.
        </div>

        <div class="signatures">
            <div class="sig-box">
                <div style="height: 70px; display:flex; align-items:center; justify-content:center; font-weight:bold; color:#0f172a;">
                    Mutuo con Interés
                </div>
                <div class="sig-line">FIRMA ACREEDOR / MUTUANTE</div>
            </div>
            <div class="sig-box">
                {sig_html}
                <div class="sig-line">FIRMA BIOMÉTRICA DEUDOR ({client.name})</div>
            </div>
        </div>

        <div class="footer-note">
            Documento Privado P2P — Mutuo con Interés — {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
    </div>
</body>
</html>"""

    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.route('/api/quote/pdf', methods=['GET'])
def generate_quote_pdf():
    company = Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada')
    alias_cbu = Setting.get_val('alias_cbu', 'FAMILIA.ANDRADA.MP')
    cuit = Setting.get_val('company_cuit', '20-33445566-9')
    bank = Setting.get_val('company_bank', 'Mercado Pago / Banco Santander')
    titular = Setting.get_val('company_titular', 'Eduardo Andrada')
    phone = Setting.get_val('company_phone', '+54 9 11 3344-5566')
    address = Setting.get_val('company_address', 'Av. Corrientes 1234, CABA')
    
    client_name = request.args.get('client_name', 'Cliente Estimado/a').strip()
    whatsapp = request.args.get('whatsapp', '').strip()
    amount = float(request.args.get('amount', 50000))
    installments_count = int(request.args.get('installments', 4))
    interest_rate = float(request.args.get('interest_rate', 15))
    rate_type = request.args.get('rate_type', 'mensual')
    modality = request.args.get('modality', 'mensual')

    # Calculations
    months = installments_count
    if modality == 'semanal': months = installments_count / 4.0
    elif modality == 'quincenal': months = installments_count / 2.0
    elif modality == 'pago_unico': months = 1.0

    if rate_type == 'directo':
        total_interest = amount * (interest_rate / 100.0)
    else:
        total_interest = amount * (interest_rate / 100.0) * max(0.25, months)

    total_to_pay = amount + total_interest
    installment_value = round(total_to_pay / installments_count, 2)

    cur_d = date.today()
    schedule_rows = ""
    for i in range(1, installments_count + 1):
        if modality == 'semanal': cur_d += timedelta(days=7)
        elif modality == 'quincenal': cur_d += timedelta(days=15)
        else: cur_d += timedelta(days=30)
        
        schedule_rows += f"""
        <tr>
            <td>Cuota #{i}</td>
            <td>{cur_d.strftime("%d/%m/%Y")}</td>
            <td><strong>${installment_value:,.2f}</strong></td>
        </tr>"""

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={alias_cbu}"

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presupuesto de Mutuo - {company}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #0f172a; padding: 20px; margin: 0; }}
        .quote-card {{ max-width: 750px; margin: 0 auto; background: #ffffff; border: 2px solid #2563eb; border-radius: 16px; padding: 35px; box-shadow: 0 10px 30px rgba(37,99,235,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 25px; }}
        .header h1 {{ margin: 0; font-size: 22px; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; }}
        .header p {{ margin: 4px 0 0 0; font-size: 14px; color: #475569; font-weight: bold; }}
        .badge {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-top: 10px; }}
        .intro {{ font-size: 15px; line-height: 1.6; margin-bottom: 25px; color: #334155; }}
        .details-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; background: #eff6ff; padding: 20px; border-radius: 12px; border: 1px solid #bfdbfe; margin-bottom: 25px; }}
        .details-item {{ font-size: 14px; }}
        .details-item strong {{ color: #1e3a8a; }}
        .big-val {{ font-size: 26px; font-weight: 900; color: #16a34a; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 14px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 10px 14px; text-align: left; }}
        th {{ background: #1e40af; color: #ffffff; text-transform: uppercase; font-size: 12px; }}
        .payment-qr-box {{ display: flex; align-items: center; justify-content: space-between; background: #f1f5f9; border: 2px solid #cbd5e1; padding: 20px; border-radius: 12px; margin-top: 25px; }}
        .payment-info {{ font-size: 13px; line-height: 1.6; color: #334155; }}
        .payment-info strong {{ color: #0f172a; }}
        .qr-img {{ width: 120px; height: 120px; border-radius: 8px; border: 1px solid #cbd5e1; background: #fff; padding: 4px; }}
        .footer-info {{ text-align: center; margin-top: 20px; font-size: 11px; color: #64748b; }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .quote-card {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 12px 28px; font-size: 15px; font-weight: bold; border-radius: 10px; cursor: pointer; shadow: 0 4px 10px rgba(0,0,0,0.15);">🖨️ Imprimir Presupuesto Express / Guardar PDF</button>
    </div>

    <div class="quote-card">
        <div class="header">
            <h1>{company}</h1>
            <p>PRESUPUESTO EXPRESS DE MUTUO CON INTERÉS</p>
            <span class="badge">PROPUESTA OFICIAL DE FINANCIACIÓN 2026</span>
        </div>

        <div class="intro">
            Estimado/a <strong>{client_name}</strong> (Contacto: {whatsapp or 'No informado'}), a continuación le presentamos la propuesta detallada para su solicitud de mutuo con interés:
        </div>

        <div class="details-grid">
            <div class="details-item"><strong>Monto Solicitado:</strong> ${amount:,.2f}</div>
            <div class="details-item"><strong>Plan de Pago:</strong> {installments_count} cuota(s) {modality}s</div>
            <div class="details-item"><strong>Tasa de Interés:</strong> {interest_rate}% ({rate_type})</div>
            <div class="details-item"><strong>Monto Total a Devolver:</strong> ${total_to_pay:,.2f}</div>
            <div class="details-item" style="grid-column: span 2;">
                <strong>VALOR ESTIMADO POR CUOTA:</strong>
                <div class="big-val">${installment_value:,.2f}</div>
            </div>
        </div>

        <h3>PROYECCIÓN ESTIMADA DE CUOTAS</h3>
        <table>
            <thead>
                <tr>
                    <th>N° Cuota</th>
                    <th>Fecha Estimada</th>
                    <th>Valor de la Cuota</th>
                </tr>
            </thead>
            <tbody>
                {schedule_rows}
            </tbody>
        </table>

        <div class="payment-qr-box">
            <div class="payment-info">
                <h4 style="margin: 0 0 6px 0; color: #1e40af; font-size: 15px;">💳 DATOS PARA PAGO / TRANSFERENCIA DIRECTA</h4>
                <strong>Firma Comercial:</strong> {company}<br>
                <strong>Titular:</strong> {titular} (CUIT/CUIL: {cuit})<br>
                <strong>Entidad:</strong> {bank}<br>
                <strong>Alias / CBU / CVU:</strong> <span style="background: #e0e7ff; color: #3730a3; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{alias_cbu}</span><br>
                <strong>Contacto:</strong> {phone} | {address}
            </div>
            <div style="text-align: center;">
                <img src="{qr_url}" alt="Código QR de Pago" class="qr-img"><br>
                <span style="font-size: 10px; font-weight: bold; color: #475569;">Escanear para Pagar</span>
            </div>
        </div>

        <div class="footer-info">
            📌 Este presupuesto tiene una validez de 7 días. Sujeto a firma del contrato de mutuo o pagaré digital.<br>
            Emitido el {datetime.now().strftime("%d/%m/%Y %H:%M")} — <strong>{company}</strong>
        </div>
    </div>
</body>
</html>"""

    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


# ----------------------------------------------------
# API INSTALLMENTS & PAYMENTS (RECIBOS)
# ----------------------------------------------------
@app.route('/api/installments/<int:installment_id>/pay', methods=['POST'])
def pay_installment(installment_id):
    inst = Installment.query.get_or_404(installment_id)
    data = request.json
    pay_amount = float(data.get('amount', inst.amount - inst.paid_amount))
    method = data.get('payment_method', 'Transferencia')
    notes = data.get('notes', '').strip()

    receipt_num = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{inst.id}"

    # Waterfall Allocation: 1. Late Fee/Mora, 2. Interest, 3. Capital Principal
    late_fee = inst.calculate_late_fee()
    remaining_interest = max(0.0, inst.interest_portion - max(0.0, inst.paid_amount - inst.capital_portion))
    remaining_capital = max(0.0, inst.capital_portion - min(inst.capital_portion, inst.paid_amount))

    alloc_late_fee = min(pay_amount, late_fee)
    rem_after_fee = pay_amount - alloc_late_fee
    alloc_interest = min(rem_after_fee, remaining_interest)
    rem_after_interest = rem_after_fee - alloc_interest
    alloc_capital = min(rem_after_interest, remaining_capital)

    pay = Payment(
        installment_id=inst.id,
        loan_id=inst.loan_id,
        client_id=inst.loan.client_id,
        amount=pay_amount,
        payment_date=datetime.now(),
        payment_method=method,
        notes=notes,
        receipt_number=receipt_num
    )
    db.session.add(pay)

    inst.paid_amount += pay_amount
    inst.paid_date = date.today()

    if inst.paid_amount >= (inst.amount + late_fee) - 0.01:
        inst.status = 'pagado'
    else:
        inst.status = 'parcial'

    db.session.commit()

    # Settings for Receipt footer
    cbu = Setting.get_val('alias_cbu', '')
    company = Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada')

    return jsonify({
        "success": True,
        "payment": pay.to_dict(),
        "installment": inst.to_dict(),
        "loan": inst.loan.to_dict(),
        "receipt_details": {
            "receipt_number": receipt_num,
            "company_name": "Mutuo con Interés",
            "alias_cbu": cbu,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client_name": inst.loan.client.name,
            "client_whatsapp": inst.loan.client.whatsapp,
            "amount_paid": pay_amount,
            "allocated_late_fee": round(alloc_late_fee, 2),
            "allocated_interest": round(alloc_interest, 2),
            "allocated_capital": round(alloc_capital, 2),
            "installment_number": inst.number,
            "total_installments": inst.loan.installments_count,
            "remaining_installment_balance": max(0.0, round((inst.amount + late_fee) - inst.paid_amount, 2)),
            "remaining_loan_balance": inst.loan.to_dict()["remaining_balance"]
        }
    })


# ----------------------------------------------------
# API EXPENSES & GASTOS HORMIGA
# ----------------------------------------------------
@app.route('/api/expenses', methods=['GET', 'POST'])
def handle_expenses():
    threshold = float(Setting.get_val('ant_expense_threshold', '2500'))
    
    if request.method == 'POST':
        data = request.json
        amount = float(data['amount'])
        exp_date = datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data and data['date'] else date.today()
        is_ant = amount <= threshold or data.get('is_ant_expense', False)

        expense = Expense(
            category=data['category'],
            description=data['description'].strip(),
            amount=amount,
            date=exp_date,
            is_ant_expense=is_ant
        )
        db.session.add(expense)
        db.session.commit()
        return jsonify(expense.to_dict()), 201

    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return jsonify({
        "expenses": [e.to_dict() for e in expenses],
        "threshold": threshold
    })


@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    exp = Expense.query.get_or_404(expense_id)
    db.session.delete(exp)
    db.session.commit()
    return jsonify({"success": True})


# ----------------------------------------------------
# API SETTINGS
# ----------------------------------------------------
@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    if request.method == 'POST':
        data = request.json
        for key, val in data.items():
            Setting.set_val(key, val)
        return jsonify({"success": True})
    
    return jsonify({
        "company_name": Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada'),
        "alias_cbu": Setting.get_val('alias_cbu', 'FAMILIA.ANDRADA.MP'),
        "qr_text": Setting.get_val('qr_text', ''),
        "company_cuit": Setting.get_val('company_cuit', '20-33445566-9'),
        "company_bank": Setting.get_val('company_bank', 'Mercado Pago / Banco Santander'),
        "company_titular": Setting.get_val('company_titular', 'Eduardo Andrada'),
        "company_phone": Setting.get_val('company_phone', '+54 9 11 3344-5566'),
        "company_address": Setting.get_val('company_address', 'Av. Corrientes 1234, CABA'),
        "default_grace_days": Setting.get_val('default_grace_days', '3'),
        "default_late_fee": Setting.get_val('default_late_fee', '1.0'),
        "ant_expense_threshold": Setting.get_val('ant_expense_threshold', '2500')
    })


# ----------------------------------------------------
# API PERSONAL ACCOUNTS, SALARY & AI CASHFLOW ANALYSIS
# ----------------------------------------------------
@app.route('/api/personal_accounts', methods=['GET', 'POST'])
def handle_personal_accounts():
    if request.method == 'POST':
        data = request.json or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({"error": "El nombre es obligatorio"}), 400
        category = data.get('category', 'servicio')
        owner = data.get('owner', 'Compartido')
        try:
            amount = float(data.get('amount', 0.0) or 0.0)
        except (ValueError, TypeError):
            amount = 0.0
        try:
            due_day = int(data.get('due_day', 10) or 10)
        except (ValueError, TypeError):
            due_day = 10
        status = data.get('status', 'pendiente')
        notes = data.get('notes', '').strip()
        try:
            start_month = int(data.get('month', date.today().month) or date.today().month)
        except (ValueError, TypeError):
            start_month = date.today().month
        try:
            start_year = int(data.get('year', date.today().year) or date.today().year)
        except (ValueError, TypeError):
            start_year = date.today().year
        try:
            installments_count = int(data.get('installments_count', 1) or 1)
        except (ValueError, TypeError):
            installments_count = 1
        is_recurring = bool(data.get('is_recurring', True))

        created_bills = []
        if installments_count > 1:
            cur_m = start_month
            cur_y = start_year
            for i in range(1, installments_count + 1):
                inst_notes = f"{notes} (Cuota {i}/{installments_count})".strip()
                bill = PersonalBill(
                    name=name,
                    category=category,
                    owner=owner,
                    amount=amount,
                    due_day=due_day,
                    status=status if i == 1 else 'pendiente',
                    notes=inst_notes,
                    month=cur_m,
                    year=cur_y,
                    installments_count=installments_count,
                    current_installment=i,
                    is_recurring=False
                )
                db.session.add(bill)
                created_bills.append(bill)
                cur_m += 1
                if cur_m > 12:
                    cur_m = 1
                    cur_y += 1
        else:
            bill = PersonalBill(
                name=name,
                category=category,
                owner=owner,
                amount=amount,
                due_day=due_day,
                status=status,
                notes=notes,
                month=start_month,
                year=start_year,
                installments_count=1,
                current_installment=1,
                is_recurring=is_recurring
            )
            db.session.add(bill)
            created_bills.append(bill)

        db.session.commit()
        return jsonify([b.to_dict() for b in created_bills]), 201
    
    # GET method
    try:
        req_month = int(request.args.get('month', date.today().month))
    except (ValueError, TypeError):
        req_month = date.today().month
    try:
        req_year = int(request.args.get('year', date.today().year))
    except (ValueError, TypeError):
        req_year = date.today().year

    # Auto carry-forward recurring bills from EARLIER months if they don't exist for req_month/req_year
    existing_in_req = PersonalBill.query.filter_by(month=req_month, year=req_year).all()
    existing_names_req = {b.name.strip().lower() for b in existing_in_req}

    earlier_recurring = PersonalBill.query.filter(
        PersonalBill.is_recurring == True,
        (PersonalBill.year < req_year) | ((PersonalBill.year == req_year) & (PersonalBill.month < req_month))
    ).all()

    seen_recurring_names = set()
    for rec in earlier_recurring:
        rec_name_key = rec.name.strip().lower()
        if rec_name_key not in existing_names_req and rec_name_key not in seen_recurring_names:
            new_clone = PersonalBill(
                name=rec.name,
                category=rec.category,
                owner=rec.owner,
                amount=rec.amount,
                due_day=rec.due_day,
                status='pendiente',
                notes=rec.notes,
                month=req_month,
                year=req_year,
                installments_count=1,
                current_installment=1,
                is_recurring=True
            )
            db.session.add(new_clone)
            seen_recurring_names.add(rec_name_key)

    if seen_recurring_names:
        db.session.commit()

    bills = PersonalBill.query.filter_by(month=req_month, year=req_year).order_by(PersonalBill.due_day.asc()).all()
    salary_eduardo = float(Setting.get_val('user_salary_eduardo', '550000'))
    salary_maira = float(Setting.get_val('user_salary_maira', '450000'))
    household_salary = salary_eduardo + salary_maira
    
    total_bills_amount = sum(b.amount for b in bills)
    total_pending = sum(b.amount for b in bills if b.status == 'pendiente')
    total_paid = sum(b.amount for b in bills if b.status == 'pagado')
    
    cards_total = sum(b.amount for b in bills if b.category == 'tarjeta')
    services_total = sum(b.amount for b in bills if b.category in ['servicio', 'fijo'])

    bills_eduardo = sum(b.amount for b in bills if b.owner == 'Eduardo') + (sum(b.amount for b in bills if b.owner == 'Compartido') * 0.5)
    bills_maira = sum(b.amount for b in bills if b.owner == 'Maira') + (sum(b.amount for b in bills if b.owner == 'Compartido') * 0.5)

    free_flow = household_salary - total_bills_amount
    debt_ratio = round((total_bills_amount / max(1.0, household_salary)) * 100.0, 1)
    
    free_flow_eduardo = salary_eduardo - bills_eduardo
    debt_ratio_eduardo = round((bills_eduardo / max(1.0, salary_eduardo)) * 100.0, 1)

    free_flow_maira = salary_maira - bills_maira
    debt_ratio_maira = round((bills_maira / max(1.0, salary_maira)) * 100.0, 1)

    if debt_ratio < 40.0:
        health_status = "Excelente"
        badge_color = "emerald"
    elif debt_ratio < 60.0:
        health_status = "Saludable"
        badge_color = "blue"
    elif debt_ratio < 80.0:
        health_status = "Atención Rechazo"
        badge_color = "amber"
    else:
        health_status = "Alerta Sobreendeudamiento"
        badge_color = "rose"

    return jsonify({
        "req_month": req_month,
        "req_year": req_year,
        "salary_eduardo": salary_eduardo,
        "salary_maira": salary_maira,
        "household_salary": household_salary,
        "bills": [b.to_dict() for b in bills],
        "metrics": {
            "total_bills_amount": round(total_bills_amount, 2),
            "total_pending": round(total_pending, 2),
            "total_paid": round(total_paid, 2),
            "cards_total": round(cards_total, 2),
            "services_total": round(services_total, 2),
            "free_flow": round(free_flow, 2),
            "debt_ratio": debt_ratio,
            "health_status": health_status,
            "badge_color": badge_color,
            "eduardo": {
                "salary": salary_eduardo,
                "bills_total": round(bills_eduardo, 2),
                "free_flow": round(free_flow_eduardo, 2),
                "debt_ratio": debt_ratio_eduardo
            },
            "maira": {
                "salary": salary_maira,
                "bills_total": round(bills_maira, 2),
                "free_flow": round(free_flow_maira, 2),
                "debt_ratio": debt_ratio_maira
            }
        }
    })


@app.route('/api/personal_accounts/<int:bill_id>', methods=['PUT', 'DELETE'])
def handle_single_personal_bill(bill_id):
    bill = PersonalBill.query.get_or_404(bill_id)
    if request.method == 'DELETE':
        delete_all = request.args.get('delete_all', 'false').lower() == 'true' or request.args.get('scope') == 'all'
        if delete_all:
            PersonalBill.query.filter(
                db.func.lower(PersonalBill.name) == bill.name.strip().lower()
            ).delete(synchronize_session=False)
        else:
            db.session.delete(bill)
        db.session.commit()
        return jsonify({"success": True})
    
    data = request.json or {}
    update_all = data.get('update_all', False) or request.args.get('update_all', 'false').lower() == 'true'
    
    old_name_key = bill.name.strip().lower()
    
    new_name = data.get('name', bill.name).strip() if data.get('name') else bill.name
    new_category = data.get('category', bill.category)
    new_owner = data.get('owner', bill.owner)
    
    try:
        new_amount = float(data['amount']) if 'amount' in data and data['amount'] is not None and data['amount'] != '' else bill.amount
    except (ValueError, TypeError):
        new_amount = bill.amount
        
    try:
        new_due_day = int(data['due_day']) if 'due_day' in data and data['due_day'] is not None and data['due_day'] != '' else bill.due_day
    except (ValueError, TypeError):
        new_due_day = bill.due_day
        
    new_status = data.get('status', bill.status)
    new_notes = data.get('notes', bill.notes).strip() if data.get('notes') is not None else bill.notes

    if update_all:
        matching = PersonalBill.query.filter(
            db.func.lower(PersonalBill.name) == old_name_key
        ).all()
        for b in matching:
            b.name = new_name
            b.category = new_category
            b.owner = new_owner
            b.amount = new_amount
            b.due_day = new_due_day
            b.notes = new_notes
            if 'is_recurring' in data: b.is_recurring = bool(data['is_recurring'])
    else:
        bill.name = new_name
        bill.category = new_category
        bill.owner = new_owner
        bill.amount = new_amount
        bill.due_day = new_due_day
        bill.status = new_status
        bill.notes = new_notes
        if 'month' in data and data['month']:
            try: bill.month = int(data['month'])
            except (ValueError, TypeError): pass
        if 'year' in data and data['year']:
            try: bill.year = int(data['year'])
            except (ValueError, TypeError): pass
        if 'is_recurring' in data: bill.is_recurring = bool(data['is_recurring'])
    
    db.session.commit()
    return jsonify(bill.to_dict())


@app.route('/api/personal_accounts/<int:bill_id>/toggle_paid', methods=['POST'])
def toggle_personal_bill_paid(bill_id):
    bill = PersonalBill.query.get_or_404(bill_id)
    bill.status = 'pagado' if bill.status == 'pendiente' else 'pendiente'
    db.session.commit()
    return jsonify(bill.to_dict())


@app.route('/api/personal_accounts/salaries', methods=['POST'])
def update_couple_salaries():
    data = request.json or {}
    sal_edu = float(data.get('salary_eduardo', 550000.0))
    sal_mai = float(data.get('salary_maira', 450000.0))
    Setting.set_val('user_salary_eduardo', str(sal_edu))
    Setting.set_val('user_salary_maira', str(sal_mai))
    return jsonify({"success": True, "salary_eduardo": sal_edu, "salary_maira": sal_mai})


@app.route('/api/personal_accounts/ai_analysis', methods=['GET'])
def get_ai_cashflow_tips():
    req_month = int(request.args.get('month', date.today().month))
    req_year = int(request.args.get('year', date.today().year))
    
    salary_eduardo = float(Setting.get_val('user_salary_eduardo', '550000'))
    salary_maira = float(Setting.get_val('user_salary_maira', '450000'))
    salary = salary_eduardo + salary_maira
    
    bills = PersonalBill.query.filter_by(month=req_month, year=req_year).all()
    total_bills = sum(b.amount for b in bills)
    cards_total = sum(b.amount for b in bills if b.category == 'tarjeta')
    pending_count = len([b for b in bills if b.status == 'pendiente'])
    free_flow = salary - total_bills
    debt_ratio = (total_bills / max(1.0, salary)) * 100.0

    month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    m_name = month_names[req_month] if 1 <= req_month <= 12 else str(req_month)

    tips = []
    
    if debt_ratio > 65.0:
        tips.append({
            "title": f"🚨 Alerta de Endeudamiento en {m_name}",
            "category": "Estrategia Urgente",
            "icon": "⚠️",
            "color": "rose",
            "text": f"En {m_name} tus compromisos (${total_bills:,.2f}) consumen el {debt_ratio:.1f}% del ingreso del hogar (${salary:,.2f}). Se recomienda recortar gastos prescindibles y pagar el total de tarjetas para evitar recargos."
        })
    elif debt_ratio > 40.0:
        tips.append({
            "title": f"⚖️ Balance de Cuentas para {m_name}",
            "category": "Optimización",
            "icon": "📈",
            "color": "amber",
            "text": f"En {m_name} estás destinando el {debt_ratio:.1f}% de los ingresos a cuentas y tarjetas. Se recomienda aplicar la regla 50/30/20 manteniendo libre al menos un 20% (${salary*0.20:,.2f})."
        })
    else:
        tips.append({
            "title": f"✨ Excelente Superávit en {m_name}",
            "category": "Crecimiento & Inversión",
            "icon": "🛡️",
            "color": "emerald",
            "text": f"¡Excelente! En {m_name} tus gastos representan solo el {debt_ratio:.1f}% de tus ingresos. Dispones de ${free_flow:,.2f} libres para ahorro o inversión."
        })

    if cards_total > (salary * 0.3):
        tips.append({
            "title": f"💳 Control de Tarjetas de Crédito ({m_name})",
            "category": "Estrategia Tarjetas",
            "icon": "💳",
            "color": "indigo",
            "text": f"Tus tarjetas suman ${cards_total:,.2f} en {m_name}. Procura no refinanciar resúmenes y liquida primero las tarjetas con mayor tasa de interés."
        })

    target_savings = round(salary * 0.20, 2)
    tips.append({
        "title": "💡 Regla de Ahorro 50/30/20 del Hogar",
        "category": "Regla Financiera IA",
        "icon": "🎯",
        "color": "blue",
        "text": f"Con el ingreso familiar de ${salary:,.2f}, la meta de reserva para el hogar es de ${target_savings:,.2f}. Separa este monto ni bien cobren sus sueldos."
    })

    if pending_count > 0:
        tips.append({
            "title": f"🗓️ Cuentas Pendientes de {m_name} ({pending_count})",
            "category": "Flujo de Caja",
            "icon": "🔔",
            "color": "amber",
            "text": f"Tienes {pending_count} cuenta(s) pendiente(s) de pago este mes. Revisa las fechas de vencimiento para evitar moras o interrupciones de servicio."
        })
    else:
        tips.append({
            "title": f"🎉 ¡Todas las cuentas de {m_name} al día!",
            "category": "Estado Óptimo",
            "icon": "✅",
            "color": "emerald",
            "text": f"Has pagado la totalidad de las cuentas de {m_name} {req_year}. Tu flujo líquido está libre de deudas este mes."
        })

    tips.append({
        "title": "🧠 Asesor IA: Planificación a Futuro",
        "category": "Tips Calendario",
        "icon": "📆",
        "color": "purple",
        "text": "Planifica los meses venideros cargando los vencimientos de tus tarjetas de crédito en cuotas para anticiparte a los meses de mayor gasto."
    })

    return jsonify({
        "tips": tips,
        "count": len(tips)
    })


@app.route('/api/personal_accounts/ai_advisor_chat', methods=['POST'])
def ai_advisor_chat():
    data = request.json or {}
    user_query = data.get('query', '').strip()
    req_month = int(data.get('month', date.today().month))
    req_year = int(data.get('year', date.today().year))

    salary_eduardo = float(Setting.get_val('user_salary_eduardo', '550000'))
    salary_maira = float(Setting.get_val('user_salary_maira', '450000'))
    household_salary = salary_eduardo + salary_maira
    
    bills = PersonalBill.query.filter_by(month=req_month, year=req_year).all()
    total_bills = sum(b.amount for b in bills)
    cards_total = sum(b.amount for b in bills if b.category == 'tarjeta')
    free_flow = household_salary - total_bills
    debt_ratio = (total_bills / max(1.0, household_salary)) * 100.0

    month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    m_name = month_names[req_month] if 1 <= req_month <= 12 else str(req_month)

    query_lower = user_query.lower()
    
    if "tarjeta" in query_lower or "cuota" in query_lower or "credito" in query_lower:
        reply = (f"En {m_name} {req_year}, el gasto en tarjetas de crédito asciende a ${cards_total:,.2f} "
                 f"({(cards_total/max(1.0, household_salary))*100:.1f}% de tus ingresos). "
                 f"Para reducir intereses: 1) Cancela el saldo total antes de la fecha de vencimiento; "
                 f"2) Evita realizar compras en más de 3 cuotas en bienes de consumo rápido; "
                 f"3) Si tienes cuotas fijas futuras, revisa la sección del Calendario para anticipar tu carga mensual.")
    elif "ahorro" in query_lower or "guardar" in query_lower or "inversion" in query_lower:
        rec_saving = household_salary * 0.20
        reply = (f"Actualmente dispones de un flujo libre estimado de ${free_flow:,.2f} en {m_name}. "
                 f"Tu meta de ahorro recomendada bajo la regla 50/30/20 es de ${rec_saving:,.2f}. "
                 f"Te aconsejo transferir este monto a una cuenta remunerada o fondo común de inversión de bajo riesgo "
                 f"apenas cobres tu sueldo para evitar gastarlo impulsivamente.")
    elif "reducir" in query_lower or "gasto" in query_lower or "recortar" in query_lower:
        reply = (f"Para optimizar tus cuentas en {m_name}: tus gastos fijos y servicios representan ${total_bills:,.2f}. "
                 f"Revisa suscripciones de streaming, contrata planes de telefonía familiar agrupados, "
                 f"y programa débitos automáticos para evitar recargos por mora en servicios esenciales.")
    elif "salud" in query_lower or "ratio" in query_lower or "diagnostico" in query_lower:
        status = "saludable" if debt_ratio <= 50 else ("moderado" if debt_ratio <= 75 else "crítico")
        reply = (f"Tu diagnóstico financiero para {m_name} es **{status.upper()}**. "
                 f"El ratio de endeudamiento es del {debt_ratio:.1f}%. "
                 f"Se considera ideal que no supere el 50%. Tienes ${free_flow:,.2f} disponible de liquidez neta.")
    else:
        reply = (f"Hola, soy tu Asesor Financiero IA para la Familia Andrada. En {m_name} {req_year}: "
                 f"Ingresos totales del hogar: ${household_salary:,.2f} | Cuentas totales: ${total_bills:,.2f} | "
                 f"Flujo libre: ${free_flow:,.2f} (Ratio de endeudamiento: {debt_ratio:.1f}%). "
                 f"¿En qué área te gustaría enfocar el plan de mejora? (Ej: Tarjetas, Ahorro, Reducción de Gastos, Diagnóstico).")

    return jsonify({
        "query": user_query,
        "reply": reply,
        "metrics_context": {
            "month": req_month,
            "year": req_year,
            "debt_ratio": debt_ratio,
            "free_flow": free_flow
        }
    })


@app.route('/api/personal_accounts/history_summary', methods=['GET'])
def get_history_summary():
    # Fetch distinct month/year pairs in personal_bills
    all_bills = PersonalBill.query.all()
    months_dict = {}
    month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    for b in all_bills:
        m = b.month or 9
        y = b.year or 2026
        key = f"{y}-{m:02d}"
        if key not in months_dict:
            months_dict[key] = {
                "year": y,
                "month": m,
                "month_name": month_names[m] if 1 <= m <= 12 else str(m),
                "total_bills": 0.0,
                "total_paid": 0.0,
                "total_pending": 0.0,
                "bills_count": 0,
                "pending_count": 0
            }
        months_dict[key]["total_bills"] += b.amount
        if b.status == 'pagado':
            months_dict[key]["total_paid"] += b.amount
        else:
            months_dict[key]["total_pending"] += b.amount
            months_dict[key]["pending_count"] += 1
        months_dict[key]["bills_count"] += 1

    history_list = sorted(months_dict.values(), key=lambda x: (x["year"], x["month"]), reverse=True)
    return jsonify({"history": history_list})


@app.route('/api/personal_accounts/clear_history', methods=['POST'])
def clear_past_history():
    data = request.json or {}
    curr_m = int(data.get('month', date.today().month))
    curr_y = int(data.get('year', date.today().year))

    # Delete bills before curr_y, curr_m
    bills_to_delete = PersonalBill.query.filter(
        (PersonalBill.year < curr_y) | ((PersonalBill.year == curr_y) & (PersonalBill.month < curr_m))
    ).all()

    count = len(bills_to_delete)
    for b in bills_to_delete:
        db.session.delete(b)
    
    db.session.commit()
    return jsonify({"success": True, "deleted_count": count, "message": f"Se eliminaron {count} cuentas de meses pasados."})



# ----------------------------------------------------
# CALENDAR ICS & 1-CLICK BACKUP & CSV REPORTS
# ----------------------------------------------------
@app.route('/api/calendar/ics', methods=['GET'])
def export_ics_calendar():
    installments = Installment.query.filter(Installment.status != 'pagado').all()
    
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Gestión Préstamos//Cobranzas//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    for inst in installments:
        date_str = inst.due_date.strftime("%Y%m%d")
        summary = f"Cobro Cuota #{inst.number} - {inst.loan.client.name} (${inst.amount:,.2f})"
        desc = f"Cliente: {inst.loan.client.name}\\nTel: +{inst.loan.client.whatsapp}\\nMonto: ${inst.amount:,.2f}"
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:inst-{inst.id}-{date_str}@prestamos.app",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"DTEND;VALUE=DATE:{date_str}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])
        
    ics_lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(ics_lines)
    
    response = make_response(ics_content)
    response.headers["Content-Disposition"] = "attachment; filename=Cobranzas_Mes.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response


@app.route('/api/backup/download', methods=['GET'])
def download_backup():
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clients": [c.to_dict() for c in Client.query.all()],
        "loans": [l.to_dict() for l in Loan.query.all()],
        "payments": [p.to_dict() for p in Payment.query.all()],
        "expenses": [e.to_dict() for e in Expense.query.all()],
        "settings": {s.key: s.value for s in Setting.query.all()}
    }
    
    response = make_response(json.dumps(data, indent=2, ensure_ascii=False))
    response.headers["Content-Disposition"] = f"attachment; filename=Backup_Prestamos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.route('/api/backup/restore', methods=['POST'])
def restore_backup():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if not file or not file.filename:
                return jsonify({"success": False, "error": "No se seleccionó ningún archivo de respaldo"}), 400
            content = file.read().decode('utf-8')
            backup_data = json.loads(content)
        elif request.is_json:
            backup_data = request.json
        else:
            return jsonify({"success": False, "error": "Formato inválido. Se espera JSON o archivo multipart."}), 400

        if not isinstance(backup_data, dict):
            return jsonify({"success": False, "error": "Estructura de respaldo inválida."}), 400

        clients_data = backup_data.get('clients', [])
        loans_data = backup_data.get('loans', [])
        payments_data = backup_data.get('payments', [])
        expenses_data = backup_data.get('expenses', [])
        settings_data = backup_data.get('settings', {})

        # Clear existing tables safely
        Payment.query.delete()
        Installment.query.delete()
        ClientDocument.query.delete()
        Loan.query.delete()
        Client.query.delete()
        Expense.query.delete()
        db.session.flush()

        # Restore Clients & Documents
        client_id_map = {}
        for c_raw in clients_data:
            old_id = c_raw.get('id')
            created_at = datetime.utcnow()
            if 'created_at' in c_raw and c_raw['created_at']:
                try:
                    created_at = datetime.strptime(c_raw['created_at'], "%Y-%m-%d %H:%M")
                except Exception:
                    pass
            new_c = Client(
                id=old_id,
                name=c_raw.get('name', '').strip(),
                whatsapp=c_raw.get('whatsapp', '').strip(),
                email=c_raw.get('email', '').strip(),
                address=c_raw.get('address', '').strip(),
                notes=c_raw.get('notes', '').strip(),
                created_at=created_at
            )
            db.session.add(new_c)
            db.session.flush()
            if old_id:
                client_id_map[old_id] = new_c.id

            for doc_raw in c_raw.get('documents', []):
                new_doc = ClientDocument(
                    client_id=new_c.id,
                    loan_id=doc_raw.get('loan_id'),
                    doc_type=doc_raw.get('doc_type', 'otro'),
                    title=doc_raw.get('title', 'Documento').strip(),
                    image_data=doc_raw.get('image_data', '')
                )
                db.session.add(new_doc)

        # Restore Loans & Installments
        loan_id_map = {}
        installment_id_map = {}
        for l_raw in loans_data:
            old_loan_id = l_raw.get('id')
            old_client_id = l_raw.get('client_id')
            target_client_id = client_id_map.get(old_client_id, old_client_id)

            start_d = date.today()
            if 'start_date' in l_raw and l_raw['start_date']:
                try:
                    start_d = datetime.strptime(l_raw['start_date'], '%Y-%m-%d').date()
                except Exception:
                    pass

            new_loan = Loan(
                id=old_loan_id,
                client_id=target_client_id,
                amount=float(l_raw.get('amount', 0)),
                interest_rate=float(l_raw.get('interest_rate', 0)),
                rate_type=l_raw.get('rate_type', 'mensual'),
                modality=l_raw.get('modality', 'mensual'),
                installments_count=int(l_raw.get('installments_count', 1)),
                start_date=start_d,
                status=l_raw.get('status', 'activo'),
                grace_days=int(l_raw.get('grace_days', 3)),
                late_fee_type=l_raw.get('late_fee_type', 'porcentaje'),
                late_fee_value=float(l_raw.get('late_fee_value', 1.0)),
                notes=l_raw.get('notes', ''),
                signature_data=l_raw.get('signature_data', '')
            )
            db.session.add(new_loan)
            db.session.flush()
            if old_loan_id:
                loan_id_map[old_loan_id] = new_loan.id

            inst_list = l_raw.get('installments', [])
            if inst_list:
                for inst_raw in inst_list:
                    old_inst_id = inst_raw.get('id')
                    due_d = date.today()
                    if 'due_date' in inst_raw and inst_raw['due_date']:
                        try:
                            due_d = datetime.strptime(inst_raw['due_date'], '%Y-%m-%d').date()
                        except Exception:
                            pass
                    paid_d = None
                    if inst_raw.get('paid_date'):
                        try:
                            paid_d = datetime.strptime(inst_raw['paid_date'], '%Y-%m-%d').date()
                        except Exception:
                            pass
                    new_inst = Installment(
                        id=old_inst_id,
                        loan_id=new_loan.id,
                        number=int(inst_raw.get('number', 1)),
                        due_date=due_d,
                        amount=float(inst_raw.get('amount', 0)),
                        capital_portion=float(inst_raw.get('capital_portion', 0)),
                        interest_portion=float(inst_raw.get('interest_portion', 0)),
                        paid_amount=float(inst_raw.get('paid_amount', 0)),
                        status=inst_raw.get('status', 'pendiente'),
                        paid_date=paid_d
                    )
                    db.session.add(new_inst)
                    db.session.flush()
                    if old_inst_id:
                        installment_id_map[old_inst_id] = new_inst.id
            else:
                schedule = new_loan.generate_amortization_schedule()
                db.session.add_all(schedule)
                db.session.flush()

        # Restore Payments
        for p_raw in payments_data:
            p_date = datetime.utcnow()
            if 'payment_date' in p_raw and p_raw['payment_date']:
                try:
                    p_date = datetime.strptime(p_raw['payment_date'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            old_inst_id = p_raw.get('installment_id')
            target_inst_id = installment_id_map.get(old_inst_id, old_inst_id)
            target_loan_id = loan_id_map.get(p_raw.get('loan_id'), p_raw.get('loan_id'))
            target_client_id = client_id_map.get(p_raw.get('client_id'), p_raw.get('client_id'))

            new_p = Payment(
                id=p_raw.get('id'),
                installment_id=target_inst_id,
                loan_id=target_loan_id,
                client_id=target_client_id,
                amount=float(p_raw.get('amount', 0)),
                payment_date=p_date,
                payment_method=p_raw.get('payment_method', 'Transferencia'),
                notes=p_raw.get('notes', ''),
                receipt_number=p_raw.get('receipt_number', f"REC-{p_raw.get('id', 1)}")
            )
            db.session.add(new_p)

        # Restore Expenses
        for e_raw in expenses_data:
            e_date = date.today()
            if 'date' in e_raw and e_raw['date']:
                try:
                    e_date = datetime.strptime(e_raw['date'], '%Y-%m-%d').date()
                except Exception:
                    pass
            new_e = Expense(
                id=e_raw.get('id'),
                category=e_raw.get('category', 'Variable'),
                description=e_raw.get('description', ''),
                amount=float(e_raw.get('amount', 0)),
                date=e_date,
                is_ant_expense=bool(e_raw.get('is_ant_expense', False))
            )
            db.session.add(new_e)

        # Restore Settings
        if isinstance(settings_data, dict):
            for k, v in settings_data.items():
                Setting.set_val(k, v)

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Copia de seguridad restaurada correctamente.",
            "restored": {
                "clients": len(clients_data),
                "loans": len(loans_data),
                "payments": len(payments_data),
                "expenses": len(expenses_data)
            }
        })
    except Exception as err:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Error al restaurar respaldo: {str(err)}"}), 500


@app.route('/api/reports/csv', methods=['GET'])
def export_csv_report():
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["REPORTE DE COBRANZAS Y GASTOS", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    
    writer.writerow(["--- HISTORIAL DE PAGOS / COBROS ---"])
    writer.writerow(["ID Recibo", "Fecha", "Cliente", "N° Cuota", "Monto Cobrado", "Método", "Notas"])
    for p in Payment.query.order_by(Payment.payment_date.desc()).all():
        writer.writerow([
            p.receipt_number,
            p.payment_date.strftime("%Y-%m-%d %H:%M"),
            p.client.name if p.client else "",
            p.installment.number if p.installment else 1,
            f"{p.amount:.2f}",
            p.payment_method,
            p.notes or ""
        ])
        
    writer.writerow([])
    writer.writerow(["--- REGISTRO DE EGRESOS / GASTOS ---"])
    writer.writerow(["ID", "Fecha", "Categoría", "Descripción", "Monto", "Es Gasto Hormiga"])
    for e in Expense.query.order_by(Expense.date.desc()).all():
        writer.writerow([
            e.id,
            e.date.strftime("%Y-%m-%d"),
            e.category,
            e.description,
            f"{e.amount:.2f}",
            "SI" if e.is_ant_expense else "NO"
        ])
        
    response = make_response(output.getvalue().encode('utf-8-sig'))
    response.headers["Content-Disposition"] = f"attachment; filename=Reporte_Contable_{datetime.now().strftime('%Y%m%d')}.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


# ----------------------------------------------------
# API CAJAS DETAILS & PDF REPORTS (CAJAS 1, 2, 3)
# ----------------------------------------------------
@app.route('/api/cajas/detail/<int:caja_id>', methods=['GET'])
def get_caja_detail(caja_id):
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    loans = Loan.query.all()
    active_loans = [l for l in loans if l.status == 'activo']
    payments = Payment.query.all()
    expenses = Expense.query.all()
    
    if caja_id == 1:
        # Caja 1: Capital en Calle
        items = []
        total_capital = 0.0
        for l in active_loans:
            pending_cap = sum(max(0.0, inst.capital_portion - min(inst.capital_portion, inst.paid_amount)) for inst in l.installments if inst.status != 'pagado')
            if pending_cap > 0:
                total_capital += pending_cap
                items.append({
                    "loan_id": l.id,
                    "client_name": l.client.name if l.client else "Desconocido",
                    "client_whatsapp": l.client.whatsapp if l.client else "",
                    "original_amount": l.amount,
                    "pending_capital": round(pending_cap, 2),
                    "start_date": l.start_date.strftime("%Y-%m-%d"),
                    "modality": l.modality,
                    "installments_count": l.installments_count,
                    "status": l.to_dict()["status"]
                })
        return jsonify({
            "caja_id": 1,
            "title": "Caja 1: Capital en Calle (Préstamos Activos)",
            "description": "Capital propio desplegado pendiente de recuperar en préstamos activos.",
            "total": round(total_capital, 2),
            "count": len(items),
            "items": items
        })
        
    elif caja_id == 2:
        # Caja 2: Intereses y Ganancias Proyectadas
        items = []
        total_interest_pending = 0.0
        total_interest_collected = sum((p.installment.interest_portion if p.installment else p.amount * 0.2) for p in payments)
        
        for l in active_loans:
            pending_int = sum(max(0.0, inst.interest_portion - max(0.0, inst.paid_amount - inst.capital_portion)) for inst in l.installments if inst.status != 'pagado')
            if pending_int > 0:
                total_interest_pending += pending_int
                items.append({
                    "loan_id": l.id,
                    "client_name": l.client.name if l.client else "Desconocido",
                    "client_whatsapp": l.client.whatsapp if l.client else "",
                    "interest_rate": l.interest_rate,
                    "pending_interest": round(pending_int, 2),
                    "total_interest": round(sum(i.interest_portion for i in l.installments), 2),
                    "start_date": l.start_date.strftime("%Y-%m-%d"),
                    "modality": l.modality
                })
        return jsonify({
            "caja_id": 2,
            "title": "Caja 2: Intereses & Ganancias Proyectadas",
            "description": "Desglose de intereses generados, cobrados y pendientes a cobrar.",
            "total_pending": round(total_interest_pending, 2),
            "total_collected": round(total_interest_collected, 2),
            "count": len(items),
            "items": items
        })
        
    elif caja_id == 3:
        # Caja 3: Ganancia Líquida del Mes & Balance Neto
        payments_this_month = [p for p in payments if p.payment_date.date() >= first_day_of_month]
        expenses_this_month = [e for e in expenses if e.date >= first_day_of_month]
        
        income_this_month = sum(p.amount for p in payments_this_month)
        interest_this_month = sum((p.installment.interest_portion if p.installment else p.amount * 0.2) for p in payments_this_month)
        expenses_amount = sum(e.amount for e in expenses_this_month)
        net_liquid_profit = interest_this_month - expenses_amount
        
        items_payments = [p.to_dict() for p in payments_this_month]
        items_expenses = [e.to_dict() for e in expenses_this_month]
        
        return jsonify({
            "caja_id": 3,
            "title": "Caja 3: Ganancia Líquida & Balance Neto del Mes",
            "description": "Intereses cobrados en el mes actual menos los gastos operativos acumulados.",
            "month_income_total": round(income_this_month, 2),
            "month_interest_collected": round(interest_this_month, 2),
            "month_expenses_total": round(expenses_amount, 2),
            "net_liquid_profit": round(net_liquid_profit, 2),
            "payments_count": len(payments_this_month),
            "expenses_count": len(expenses_this_month),
            "payments": items_payments,
            "expenses": items_expenses
        })
        
    return jsonify({"error": "Caja no válida"}), 400


@app.route('/api/cajas/pdf/<int:caja_id>', methods=['GET'])
def generate_caja_pdf(caja_id):
    company = Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada')
    detail_res = get_caja_detail(caja_id)
    data = detail_res.get_json()
    
    today_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if caja_id == 1:
        title = "REPORTE DETALLADO - CAJA 1: CAPITAL EN CALLE"
        total_label = f"Total Capital Pendiente: ${data['total']:,.2f}"
        rows_html = "".join([
            f"<tr><td>P2P-{item['loan_id']:05d}</td><td>{item['client_name']}</td><td>+{item['client_whatsapp']}</td><td>${item['original_amount']:,.2f}</td><td><strong>${item['pending_capital']:,.2f}</strong></td><td>{item['start_date']}</td><td><span style='color:green;'>{item['status'].upper()}</span></td></tr>"
            for item in data['items']
        ])
        headers_html = "<th>ID</th><th>Cliente</th><th>WhatsApp</th><th>Monto Original</th><th>Capital en Calle</th><th>Inicio</th><th>Estado</th>"
        
    elif caja_id == 2:
        title = "REPORTE DETALLADO - CAJA 2: INTERESES & GANANCIAS"
        total_label = f"Interés Cobrado: ${data['total_collected']:,.2f} | Interés a Cobrar: ${data['total_pending']:,.2f}"
        rows_html = "".join([
            f"<tr><td>P2P-{item['loan_id']:05d}</td><td>{item['client_name']}</td><td>+{item['client_whatsapp']}</td><td>{item['interest_rate']}%</td><td>${item['total_interest']:,.2f}</td><td><strong>${item['pending_interest']:,.2f}</strong></td><td>{item['modality']}</td></tr>"
            for item in data['items']
        ])
        headers_html = "<th>ID</th><th>Cliente</th><th>WhatsApp</th><th>Tasa</th><th>Interés Total</th><th>Interés Pendiente</th><th>Modalidad</th>"
        
    else:
        title = "REPORTE DETALLADO - CAJA 3: GANANCIA LÍQUIDA Y BALANCE NETO DEL MES"
        total_label = f"Intereses del Mes: ${data['month_interest_collected']:,.2f} - Gastos: ${data['month_expenses_total']:,.2f} = GANANCIA NETA: ${data['net_liquid_profit']:,.2f}"
        
        rows_payments = "".join([
            f"<tr><td>Cobro REC-{p['id']}</td><td>{p['payment_date']}</td><td>{p['client_name']}</td><td>{p['payment_method']}</td><td><strong>${p['amount']:,.2f}</strong></td></tr>"
            for p in data['payments']
        ])
        rows_expenses = "".join([
            f"<tr><td>Gasto #{e['id']}</td><td>{e['date']}</td><td>{e['category']} - {e['description']}</td><td>{'SÍ' if e['is_ant_expense'] else 'NO'}</td><td><strong style='color:red;'>${e['amount']:,.2f}</strong></td></tr>"
            for e in data['expenses']
        ])
        
        rows_html = f"<tr><td colspan='5' style='background:#f1f5f9; font-weight:bold;'>--- INGRESOS / COBROS DEL MES ({data['payments_count']}) ---</td></tr>" + rows_payments + f"<tr><td colspan='5' style='background:#fee2e2; font-weight:bold;'>--- GASTOS DEL MES ({data['expenses_count']}) ---</td></tr>" + rows_expenses
        headers_html = "<th>Tipo / ID</th><th>Fecha</th><th>Cliente / Detalle</th><th>Categoría / Método</th><th>Monto</th>"

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8fafc; color: #0f172a; padding: 20px; margin: 0; }}
        .card {{ max-width: 900px; margin: 0 auto; background: #ffffff; border: 2px solid #0f172a; border-radius: 12px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #cbd5e1; padding-bottom: 15px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; font-size: 20px; color: #0f172a; text-transform: uppercase; }}
        .header p {{ margin: 5px 0 0 0; font-size: 13px; color: #64748b; font-weight: bold; }}
        .total-box {{ background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
        th {{ background: #0f172a; color: #ffffff; text-transform: uppercase; font-size: 11px; }}
        .footer {{ text-align: center; font-size: 11px; color: #94a3b8; margin-top: 25px; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .card {{ border: none; box-shadow: none; padding: 0; max-width: 100%; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 10px 24px; font-size: 14px; font-weight: bold; border-radius: 8px; cursor: pointer;">🖨️ Imprimir / Guardar PDF</button>
    </div>

    <div class="card">
        <div class="header">
            <h1>{title}</h1>
            <p>{company} — Emitido el {today_str}</p>
        </div>

        <div class="total-box">
            {total_label}
        </div>

        <table>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div class="footer">
            Reporte generado automáticamente — {company} — Sistema de Control Financiero
        </div>
    </div>
</body>
</html>"""

    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


# ----------------------------------------------------
# API CASH FLOW & GENERAL HISTORY & BULK DELETE
# ----------------------------------------------------
@app.route('/api/cashflow/detail', methods=['GET'])
def get_cashflow_detail():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    query = Payment.query
    if year:
        query = query.filter(db.extract('year', Payment.payment_date) == year)
    if month:
        query = query.filter(db.extract('month', Payment.payment_date) == month)
        
    payments = query.order_by(Payment.payment_date.desc()).all()
    
    total_received = sum(p.amount for p in payments)
    total_capital = sum((p.installment.capital_portion if p.installment else p.amount * 0.8) for p in payments)
    total_interest = sum((p.installment.interest_portion if p.installment else p.amount * 0.2) for p in payments)
    
    by_method = {}
    for p in payments:
        method = p.payment_method or 'Transferencia'
        by_method[method] = round(by_method.get(method, 0.0) + p.amount, 2)
        
    return jsonify({
        "total_received": round(total_received, 2),
        "total_capital": round(total_capital, 2),
        "total_interest": round(total_interest, 2),
        "payments_count": len(payments),
        "by_method": by_method,
        "payments": [p.to_dict() for p in payments]
    })


@app.route('/api/history/general', methods=['GET'])
def get_general_history():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    item_type = request.args.get('type', 'todos')
    
    history_items = []
    
    # 1. Loans
    if item_type in ['todos', 'loans', 'prestamos']:
        loans_q = Loan.query
        if year:
            loans_q = loans_q.filter(db.extract('year', Loan.created_at) == year)
        if month:
            loans_q = loans_q.filter(db.extract('month', Loan.created_at) == month)
        for l in loans_q.all():
            history_items.append({
                "unique_key": f"loan_{l.id}",
                "type": "prestamo",
                "raw_type": "Loan",
                "id": l.id,
                "date": l.created_at.strftime("%Y-%m-%d %H:%M"),
                "title": f"Préstamo a {l.client.name if l.client else 'Cliente'}",
                "subtitle": f"Monto: ${l.amount:,.2f} | {l.installments_count} cuotas | Tasa: {l.interest_rate}%",
                "amount": l.amount,
                "status": l.to_dict()["status"],
                "client_name": l.client.name if l.client else ""
            })

    # 2. Payments
    if item_type in ['todos', 'payments', 'cobros']:
        pay_q = Payment.query
        if year:
            pay_q = pay_q.filter(db.extract('year', Payment.payment_date) == year)
        if month:
            pay_q = pay_q.filter(db.extract('month', Payment.payment_date) == month)
        for p in pay_q.all():
            history_items.append({
                "unique_key": f"payment_{p.id}",
                "type": "cobro",
                "raw_type": "Payment",
                "id": p.id,
                "date": p.payment_date.strftime("%Y-%m-%d %H:%M"),
                "title": f"Cobro REC-{p.id} ({p.client.name if p.client else 'Cliente'})",
                "subtitle": f"Cuota #{p.installment.number if p.installment else 1} | Método: {p.payment_method}",
                "amount": p.amount,
                "status": "completado",
                "client_name": p.client.name if p.client else ""
            })

    # 3. Expenses
    if item_type in ['todos', 'expenses', 'gastos']:
        exp_q = Expense.query
        if year:
            exp_q = exp_q.filter(db.extract('year', Expense.date) == year)
        if month:
            exp_q = exp_q.filter(db.extract('month', Expense.date) == month)
        for e in exp_q.all():
            history_items.append({
                "unique_key": f"expense_{e.id}",
                "type": "gasto",
                "raw_type": "Expense",
                "id": e.id,
                "date": e.date.strftime("%Y-%m-%d"),
                "title": f"Gasto: {e.description}",
                "subtitle": f"Categoría: {e.category} | {'Hormiga' if e.is_ant_expense else 'Ordinario'}",
                "amount": -e.amount,
                "status": "registrado",
                "client_name": ""
            })

    # Sort descending by date
    history_items.sort(key=lambda x: x["date"], reverse=True)
    return jsonify(history_items)


@app.route('/api/history/bulk_delete', methods=['POST'])
def bulk_delete_history():
    data = request.json or {}
    items = data.get('items', [])
    
    deleted_count = 0
    for item in items:
        raw_type = item.get('raw_type')
        item_id = item.get('id')
        
        if raw_type == 'Loan':
            obj = Loan.query.get(item_id)
            if obj:
                db.session.delete(obj)
                deleted_count += 1
        elif raw_type == 'Payment':
            obj = Payment.query.get(item_id)
            if obj:
                if obj.installment:
                    obj.installment.paid_amount = max(0.0, obj.installment.paid_amount - obj.amount)
                    if obj.installment.paid_amount == 0:
                        obj.installment.status = 'pendiente'
                    else:
                        obj.installment.status = 'parcial'
                db.session.delete(obj)
                deleted_count += 1
        elif raw_type == 'Expense':
            obj = Expense.query.get(item_id)
            if obj:
                db.session.delete(obj)
                deleted_count += 1
        elif raw_type == 'Client':
            obj = Client.query.get(item_id)
            if obj:
                db.session.delete(obj)
                deleted_count += 1
                
    db.session.commit()
    return jsonify({"success": True, "deleted_count": deleted_count})


# ----------------------------------------------------
# API SMART AI FINANCIAL ADVISOR BOT
# ----------------------------------------------------
@app.route('/api/ai_financial_advisor', methods=['GET'])
def get_ai_financial_advisor():
    today = date.today()
    first_day = date(today.year, today.month, 1)
    
    loans = Loan.query.all()
    active_loans = [l for l in loans if l.status == 'activo']
    payments = Payment.query.all()
    expenses = Expense.query.all()
    
    payments_month = [p for p in payments if p.payment_date.date() >= first_day]
    expenses_month = [e for e in expenses if e.date >= first_day]
    
    capital_en_calle = sum(
        sum(max(0.0, inst.capital_portion - min(inst.capital_portion, inst.paid_amount)) for inst in l.installments if inst.status != 'pagado')
        for l in active_loans
    )
    
    interest_month = sum((p.installment.interest_portion if p.installment else p.amount * 0.2) for p in payments_month)
    expenses_month_total = sum(e.amount for e in expenses_month)
    ant_expenses_month = sum(e.amount for e in expenses_month if e.is_ant_expense)
    net_liquid = interest_month - expenses_month_total
    
    # Overdue stats
    installments = Installment.query.all()
    overdue_count = sum(1 for inst in installments if inst.status != 'pagado' and (today - inst.due_date).days > (inst.loan.grace_days or 0))
    total_inst = len(installments)
    mora_pct = (overdue_count / max(1, total_inst)) * 100.0
    
    # AI Rules & Calculations:
    reserve_fund = capital_en_calle * 0.10
    capital_inviolable = capital_en_calle + reserve_fund
    
    reinvestment_portion = max(0.0, net_liquid * 0.30)
    safe_withdrawable_amount = max(0.0, net_liquid - reinvestment_portion)
    
    alerts = []
    if ant_expenses_month > 0:
        ant_pct = (ant_expenses_month / max(1.0, expenses_month_total)) * 100.0
        if ant_pct > 15.0:
            alerts.append({
                "level": "warning",
                "title": "🚨 Fuga de Dinero Detectada (Gastos Hormiga Altos)",
                "message": f"Los gastos hormiga representan el {ant_pct:.1f}% (${ant_expenses_month:,.2f}) de tus gastos del mes. Se recomienda auditarlos inmediatamente."
            })
            
    if mora_pct > 10.0:
        alerts.append({
            "level": "danger",
            "title": "⚠️ Tasa de Mora Elevada",
            "message": f"Tu índice de mora actual es de {mora_pct:.1f}%. Te sugiero reducir el otorgamiento de nuevos créditos y enfocar el 80% de tu tiempo en gestión de cobro de cuotas vencidas."
        })
    else:
        alerts.append({
            "level": "success",
            "title": "🛡️ Excelente Salud de Cartera",
            "message": f"Tu tasa de mora es baja ({mora_pct:.1f}%). Puedes reinvertir de forma segura en nuevos préstamos a clientes con Scoring de 4 o 5 estrellas."
        })
        
    recommendations = [
        f"💡 **Fondo Inviolable**: Mantén en caja o cuenta productiva ${capital_inviolable:,.2f} para respaldar la continuidad de los préstamos activos.",
        f"💰 **Retiro Sugerido**: De la ganancia neta de este mes (${net_liquid:,.2f}), puedes retirar hasta **${safe_withdrawable_amount:,.2f}** y destinar **${reinvestment_portion:,.2f}** (30%) a aumentar tu fondo prestable.",
        "📊 **Regla de Oro**: Nunca financies gastos fijos o personales utilizando el capital cobrado de las amortizaciones de capital principal. Solo debes tocar las ganancias netas de intereses."
    ]
    
    return jsonify({
        "status": "active",
        "capital_inviolable": round(capital_inviolable, 2),
        "safe_withdrawable_amount": round(safe_withdrawable_amount, 2),
        "reinvestment_portion": round(reinvestment_portion, 2),
        "net_liquid_profit": round(net_liquid, 2),
        "ant_expenses_month": round(ant_expenses_month, 2),
        "mora_percentage": round(mora_pct, 1),
        "alerts": alerts,
        "recommendations": recommendations
    })


# ----------------------------------------------------
# API BIOMETRIC EXPRESS PAGARÉ & SIGNATURE SYSTEM
# ----------------------------------------------------

def cleanup_biometric_requests():
    """
    Limpieza automática de solicitudes de Pagaré Express QR:
    1. Elimina solicitudes emitidas hace más de 30 minutos (expiradas).
    2. Elimina solicitudes cuyo estado sea 'otorgado' o cuyo préstamo fue otorgado/activado.
    """
    try:
        now = datetime.utcnow()
        thirty_mins_ago = now - timedelta(minutes=30)
        
        expired = BiometricRequest.query.filter(BiometricRequest.created_at < thirty_mins_ago).all()
        granted = BiometricRequest.query.filter(BiometricRequest.status.in_(['otorgado', 'cancelado'])).all()
        
        to_delete = set(expired + granted)
        if to_delete:
            for req in to_delete:
                db.session.delete(req)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error en cleanup_biometric_requests: {e}")


@app.route('/api/biometric_requests', methods=['GET', 'POST'])
@app.route('/api/biometric/request/create', methods=['POST'])
def handle_biometric_requests():
    cleanup_biometric_requests()
    if request.method == 'GET':
        client_id = request.args.get('client_id')
        query = BiometricRequest.query
        if client_id:
            query = query.filter_by(client_id=int(client_id))
        requests_list = query.order_by(BiometricRequest.id.desc()).all()
        return jsonify([r.to_dict() for r in requests_list])

    data = request.json or {}
    client_id = int(data.get('client_id', 0))
    if not client_id:
        return jsonify({"error": "client_id es requerido", "status": "error"}), 400

    client = Client.query.get_or_404(client_id)
    
    # Eliminar solicitudes anteriores no completadas para este cliente
    old_reqs = BiometricRequest.query.filter_by(client_id=client_id).all()
    for old in old_reqs:
        db.session.delete(old)
    db.session.commit()
    
    token = uuid.uuid4().hex[:12]
    amount = float(data.get('amount', 50000))
    installments_count = int(data.get('installments_count', 4))
    interest_rate = float(data.get('interest_rate', 15.0))
    rate_type = data.get('rate_type', 'mensual')
    modality = data.get('modality', 'mensual')
    notes = data.get('notes', 'Pagaré Virtual Express con firma biométrica y selfie').strip()
    
    bio_req = BiometricRequest(
        token=token,
        client_id=client_id,
        amount=amount,
        installments_count=installments_count,
        interest_rate=interest_rate,
        rate_type=rate_type,
        modality=modality,
        notes=notes,
        status='pendiente'
    )
    db.session.add(bio_req)
    db.session.commit()
    
    host_url = request.host_url.rstrip('/')
    sign_url = f"{host_url}/firmar/{token}"
    qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(sign_url)}"
    
    company_name = Setting.get_val('company_name', 'Prestamos & Finanzas')
    wa_msg = f"Hola {client.name}, por favor ingresa al enlace para firmar tu Pagaré Digital Express por ${amount:,.2f} y completar tu validación biométrica con selfie (Válido por 30 minutos):\n{sign_url}"
    clean_phone = client.whatsapp.replace('+', '').replace(' ', '').replace('-', '')
    wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}"
    
    return jsonify({
        "success": True,
        "status": "success",
        "token": token,
        "sign_url": sign_url,
        "qr_img_url": qr_img_url,
        "wa_url": wa_url,
        "client_name": client.name,
        "biometric_request": bio_req.to_dict()
    })


@app.route('/api/biometric_requests/<token>', methods=['GET', 'DELETE'])
def single_biometric_request(token):
    cleanup_biometric_requests()
    bio_req = BiometricRequest.query.filter_by(token=token).first()
    if request.method == 'DELETE':
        if bio_req:
            db.session.delete(bio_req)
            db.session.commit()
        return jsonify({"success": True, "message": "Pagaré Express QR eliminado correctamente."})
        
    if not bio_req or bio_req.is_expired or bio_req.status == 'otorgado':
        if bio_req:
            db.session.delete(bio_req)
            db.session.commit()
        return jsonify({"error": "Pagaré Express QR expirado o eliminado por otorgamiento."}), 404
        
    return jsonify(bio_req.to_dict())


@app.route('/firmar/<token>', methods=['GET'])
def render_biometric_sign_page(token):
    cleanup_biometric_requests()
    bio_req = BiometricRequest.query.filter_by(token=token).first()
    
    # 1. Si la solicitud no existe o fue eliminada por estar otorgada/expirada (>30 min)
    if not bio_req:
        return render_template_string("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Express Expirado o No Disponible</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; }</style>
</head>
<body class="min-h-screen p-6 flex items-center justify-center">
    <div class="max-w-md w-full bg-slate-900/95 border border-slate-800 p-6 rounded-3xl text-center space-y-4 shadow-2xl">
        <div class="w-16 h-16 rounded-2xl bg-amber-500/20 text-amber-400 mx-auto flex items-center justify-center text-3xl border border-amber-500/30">
            ⏰
        </div>
        <h1 class="text-xl font-black text-white">QR Express Expirado o No Disponible</h1>
        <p class="text-xs text-slate-300 leading-relaxed">
            Este código QR o enlace ha <strong>expirado</strong> (superó el límite de 30 minutos desde su emisión) o ya fue <strong>eliminado automáticamente</strong> porque el préstamo fue otorgado.
        </p>
        <div class="p-3 bg-slate-800/80 rounded-2xl text-[11px] text-slate-400 border border-slate-700">
            Por favor, solicita al administrador un nuevo código QR Express para formalizar la firma biométrica.
        </div>
    </div>
</body>
</html>"""), 410

    # 2. Si expiró en el momento exacto
    if bio_req.is_expired:
        db.session.delete(bio_req)
        db.session.commit()
        return render_template_string("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Express Expirado</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; }</style>
</head>
<body class="min-h-screen p-6 flex items-center justify-center">
    <div class="max-w-md w-full bg-slate-900/95 border border-slate-800 p-6 rounded-3xl text-center space-y-4 shadow-2xl">
        <div class="w-16 h-16 rounded-2xl bg-amber-500/20 text-amber-400 mx-auto flex items-center justify-center text-3xl border border-amber-500/30">
            ⏱️
        </div>
        <h1 class="text-xl font-black text-white">Tiempo de QR Expirado (30 min)</h1>
        <p class="text-xs text-slate-300 leading-relaxed">
            El tiempo límite de 30 minutos ha finalizado. El código QR ha sido eliminado por seguridad.
        </p>
    </div>
</body>
</html>"""), 410

    client = bio_req.client
    company = Setting.get_val('company_name', 'Prestamos & Finanzas Familia Andrada')
    
    months = bio_req.installments_count
    if bio_req.modality == 'semanal': months = bio_req.installments_count / 4.0
    elif bio_req.modality == 'quincenal': months = bio_req.installments_count / 2.0
    elif bio_req.modality == 'pago_unico': months = 1.0

    if bio_req.rate_type == 'directo':
        total_interest = bio_req.amount * (bio_req.interest_rate / 100.0)
    else:
        total_interest = bio_req.amount * (bio_req.interest_rate / 100.0) * max(0.25, months)

    total_to_pay = bio_req.amount + total_interest
    installment_value = round(total_to_pay / bio_req.installments_count, 2)
    rem_seconds = bio_req.remaining_seconds

    html_page = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Pagaré Digital Express - Firma Biométrica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }}
        .glass-card {{ background: rgba(30, 41, 59, 0.90); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        canvas {{ touch-action: none; }}
    </style>
</head>
<body class="min-h-screen p-3 sm:p-6 flex flex-col justify-center items-center">
    <div class="w-full max-w-lg space-y-4">
        
        <!-- Header -->
        <div class="text-center space-y-1">
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/30">
                <span>🔐 Firma Digital Biométrica 2026</span>
            </div>
            <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">{company}</h1>
            <p class="text-xs text-slate-400">Pagaré Virtual Express con Verificación de Identidad</p>
        </div>

        <!-- 30 MINUTE COUNTDOWN BANNER -->
        <div class="glass-card p-3 rounded-2xl flex items-center justify-between border-amber-500/40 bg-amber-950/20 text-amber-300 shadow-lg">
            <div class="flex items-center space-x-2 text-xs font-bold">
                <span class="animate-pulse text-base">⏱️</span>
                <span>Vencimiento del QR Express:</span>
            </div>
            <div class="font-mono text-sm font-black px-2.5 py-1 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-200">
                <span id="timerCountdown">--:--</span>
            </div>
        </div>

        <!-- Promissory Note Summary Card -->
        <div id="signCard" class="glass-card p-4 sm:p-5 rounded-2xl space-y-3 shadow-2xl">
            <div class="flex justify-between items-center border-b border-slate-700 pb-2">
                <span class="text-xs font-bold text-slate-400 uppercase">Solicitante / Deudor</span>
                <span class="text-xs font-black text-emerald-400 uppercase">Verificado</span>
            </div>
            <div class="text-sm font-bold text-white">
                👤 {client.name} <span class="text-xs text-slate-400 font-normal">({client.whatsapp})</span>
            </div>

            <div class="grid grid-cols-2 gap-2.5 pt-2 text-xs border-t border-slate-700/60">
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-700/50">
                    <span class="text-slate-400 block text-[10px] uppercase font-bold">Monto Solicitado</span>
                    <span class="text-emerald-400 font-black text-base">${bio_req.amount:,.2f}</span>
                </div>
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-700/50">
                    <span class="text-slate-400 block text-[10px] uppercase font-bold">Plan de Pago</span>
                    <span class="text-white font-bold">{bio_req.installments_count} cuota(s) ({bio_req.modality})</span>
                </div>
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-700/50">
                    <span class="text-slate-400 block text-[10px] uppercase font-bold">Tasa de Interés</span>
                    <span class="text-amber-300 font-bold">{bio_req.interest_rate}% ({bio_req.rate_type})</span>
                </div>
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-700/50">
                    <span class="text-slate-400 block text-[10px] uppercase font-bold">Valor por Cuota</span>
                    <span class="text-white font-black text-sm">${installment_value:,.2f}</span>
                </div>
            </div>

            <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-[11px] text-slate-300 space-y-1.5 leading-relaxed">
                <p class="font-bold text-amber-300">📄 Declaración Jurada de Pagaré Digital:</p>
                <p>Por medio del presente reconozco adeudar incondicionalmente a <strong>{company}</strong> la suma total de <strong>${total_to_pay:,.2f}</strong> a ser pagada en {bio_req.installments_count} cuota(s). Declaro bajo fe de juramento la validez de mi firma digital y fotografía biométrica.</p>
            </div>

            <!-- STEP 1: DIGITAL SIGNATURE CANVAS -->
            <div class="space-y-2 pt-2 border-t border-slate-700">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-bold text-white flex items-center gap-1.5">
                        <span>✍️ Paso 1: Firma Digital del Deudor</span>
                    </span>
                    <button type="button" onclick="clearSignature()" class="text-[11px] text-rose-400 font-bold hover:underline">Limpiar Firma</button>
                </div>
                <div class="relative bg-slate-950 rounded-xl border border-slate-700 overflow-hidden touch-none">
                    <canvas id="signatureCanvas" class="w-full h-36 cursor-crosshair"></canvas>
                    <div id="sigPlaceholder" class="absolute inset-0 flex items-center justify-center pointer-events-none text-slate-600 text-xs font-bold uppercase tracking-wider">
                        Dibuja tu firma aquí con el dedo o mouse
                    </div>
                </div>
            </div>

            <!-- STEP 2: CAMERA SELFIE BIOMETRIC & FILE FALLBACK -->
            <div class="space-y-2 pt-2 border-t border-slate-700">
                <span class="text-xs font-bold text-white block">📸 Paso 2: Selfie de Verificación Biométrica</span>
                <div class="bg-slate-950 rounded-xl border border-slate-700 p-3 text-center space-y-3">
                    <div class="relative w-full max-w-[240px] h-[180px] mx-auto bg-black rounded-lg overflow-hidden flex items-center justify-center">
                        <video id="videoElement" autoplay playsinline class="w-full h-full object-cover hidden"></video>
                        <img id="selfiePreview" class="w-full h-full object-cover hidden" alt="Selfie Preview"/>
                        <canvas id="selfieCanvas" class="hidden"></canvas>
                    </div>

                    <!-- Hidden File Input for Mobile/PC Backup -->
                    <input type="file" id="fileSelfieInput" accept="image/*" capture="user" class="hidden" onchange="handleFileSelect(event)">

                    <div class="flex flex-wrap justify-center gap-2">
                        <button type="button" id="startCamBtn" onclick="startCamera()" class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition flex items-center gap-1">
                            📷 Cámara en Vivo
                        </button>
                        <button type="button" onclick="document.getElementById('fileSelfieInput').click()" class="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition flex items-center gap-1">
                            📁 Tomar / Subir Foto
                        </button>
                        <button type="button" id="snapBtn" onclick="takeSnap()" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition hidden">
                            📸 Capturar
                        </button>
                        <button type="button" id="retakeBtn" onclick="retakeSnap()" class="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold transition hidden">
                            🔄 Repetir
                        </button>
                    </div>
                    <p id="cameraStatus" class="text-[10px] text-slate-400">Presiona 'Cámara en Vivo' o 'Tomar / Subir Foto' para validar tu identidad</p>
                </div>
            </div>

            <!-- STEP 3: ACCEPT CHECKBOX & SUBMIT -->
            <div class="pt-2 space-y-3">
                <label class="flex items-start space-x-2 cursor-pointer select-none">
                    <input type="checkbox" id="acceptCheck" class="mt-0.5 rounded border-slate-700 bg-slate-900 text-brand-600 focus:ring-brand-500">
                    <span class="text-[11px] text-slate-300">Acepto los términos del Pagaré Digital, autorizo mi firma digital y selfie como constancia válida de obligación de pago.</span>
                </label>

                <button type="button" id="submitBtn" onclick="submitBiometricSignature('{token}')" class="w-full py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-extrabold text-sm shadow-lg shadow-emerald-500/20 transition active:scale-[0.99]">
                    ✍️ Aceptar & Firmar Pagaré Digital
                </button>
            </div>
        </div>

        <!-- EXPIRED / SUCCESS BOXES -->
        <div id="expiredBox" class="glass-card p-6 rounded-2xl text-center space-y-3 hidden border-amber-500/40">
            <div class="w-14 h-14 rounded-full bg-amber-500/20 text-amber-400 mx-auto flex items-center justify-center text-3xl">⏰</div>
            <h2 class="text-xl font-black text-white">QR Expirado (30 Minutos)</h2>
            <p class="text-xs text-slate-300">El tiempo de validez para firmar este pagaré ha finalizado. Por favor solicita un nuevo código QR al emisor.</p>
        </div>

        <div id="successBox" class="glass-card p-6 rounded-2xl text-center space-y-3 hidden border-emerald-500/40">
            <div class="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center text-2xl">✅</div>
            <h2 class="text-xl font-black text-white">¡Pagaré Firmado Exitosamente!</h2>
            <p class="text-xs text-slate-300">Tu firma digital y selfie biométrica han sido registradas de forma segura. Tu solicitud pasará a revisión para el otorgamiento del préstamo.</p>
        </div>

    </div>

    <script>
        // 30 MINUTE COUNTDOWN TIMER
        let secondsLeft = {rem_seconds};
        function updateTimer() {{
            if (secondsLeft <= 0) {{
                document.getElementById('signCard').style.display = 'none';
                document.getElementById('expiredBox').classList.remove('hidden');
                document.getElementById('timerCountdown').innerText = '00:00 EXPIRED';
                return;
            }}
            let mins = Math.floor(secondsLeft / 60);
            let secs = secondsLeft % 60;
            document.getElementById('timerCountdown').innerText = 
                (mins < 10 ? '0' : '') + mins + ':' + (secs < 10 ? '0' : '') + secs;
            secondsLeft--;
        }}
        setInterval(updateTimer, 1000);
        updateTimer();

        // SIGNATURE CANVAS LOGIC (COMPATIBLE MOBILE & PC)
        const canvas = document.getElementById('signatureCanvas');
        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        let hasSignature = false;

        function resizeCanvas() {{
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
        }}
        window.addEventListener('resize', resizeCanvas);
        setTimeout(resizeCanvas, 150);

        function getPos(e) {{
            const rect = canvas.getBoundingClientRect();
            let clientX, clientY;
            if (e.touches && e.touches.length > 0) {{
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            }} else if (e.changedTouches && e.changedTouches.length > 0) {{
                clientX = e.changedTouches[0].clientX;
                clientY = e.changedTouches[0].clientY;
            }} else {{
                clientX = e.clientX;
                clientY = e.clientY;
            }}
            return {{
                x: (clientX - rect.left) * (canvas.width / rect.width),
                y: (clientY - rect.top) * (canvas.height / rect.height)
            }};
        }}

        function startDrawing(e) {{
            isDrawing = true;
            hasSignature = true;
            document.getElementById('sigPlaceholder').style.display = 'none';
            const pos = getPos(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        }}

        function draw(e) {{
            if (!isDrawing) return;
            if (e.cancelable) e.preventDefault();
            const pos = getPos(e);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        }}

        function stopDrawing() {{ isDrawing = false; }}

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mouseleave', stopDrawing);

        canvas.addEventListener('touchstart', (e) => {{ if (e.cancelable) e.preventDefault(); startDrawing(e); }}, {{ passive: false }});
        canvas.addEventListener('touchmove', (e) => {{ if (e.cancelable) e.preventDefault(); draw(e); }}, {{ passive: false }});
        canvas.addEventListener('touchend', stopDrawing);

        function clearSignature() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            hasSignature = false;
            document.getElementById('sigPlaceholder').style.display = 'flex';
        }}

        // CAMERA SELFIE LOGIC (MULTI-PLATFORM MOBILE & PC)
        let videoStream = null;
        let selfieDataUrl = '';

        async function startCamera() {{
            try {{
                // Try facingMode user first
                try {{
                    videoStream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'user' }} }});
                }} catch(e1) {{
                    // Fallback to basic video true for desktop webcams
                    videoStream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                }}
                const video = document.getElementById('videoElement');
                video.srcObject = videoStream;
                video.classList.remove('hidden');
                document.getElementById('selfiePreview').classList.add('hidden');
                document.getElementById('startCamBtn').classList.add('hidden');
                document.getElementById('snapBtn').classList.remove('hidden');
                document.getElementById('retakeBtn').classList.add('hidden');
                document.getElementById('cameraStatus').innerText = 'Cámara Activa. Ubica tu rostro y captura.';
            }} catch(err) {{
                alert('No se pudo abrir la cámara en vivo. Puedes usar la opción "Tomar / Subir Foto" para seleccionar o tomar una foto.');
            }}
        }}

        function takeSnap() {{
            const video = document.getElementById('videoElement');
            const canvasSnap = document.getElementById('selfieCanvas');
            canvasSnap.width = video.videoWidth || 320;
            canvasSnap.height = video.videoHeight || 240;
            const snapCtx = canvasSnap.getContext('2d');
            snapCtx.drawImage(video, 0, 0, canvasSnap.width, canvasSnap.height);
            selfieDataUrl = canvasSnap.toDataURL('image/jpeg', 0.85);

            document.getElementById('selfiePreview').src = selfieDataUrl;
            document.getElementById('selfiePreview').classList.remove('hidden');
            video.classList.add('hidden');
            document.getElementById('snapBtn').classList.add('hidden');
            document.getElementById('retakeBtn').classList.remove('hidden');
            document.getElementById('cameraStatus').innerText = 'Foto Capturada Correctamente';

            if (videoStream) {{
                videoStream.getTracks().forEach(t => t.stop());
            }}
        }}

        function handleFileSelect(e) {{
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(evt) {{
                selfieDataUrl = evt.target.result;
                document.getElementById('selfiePreview').src = selfieDataUrl;
                document.getElementById('selfiePreview').classList.remove('hidden');
                document.getElementById('videoElement').classList.add('hidden');
                document.getElementById('startCamBtn').classList.add('hidden');
                document.getElementById('snapBtn').classList.add('hidden');
                document.getElementById('retakeBtn').classList.remove('hidden');
                document.getElementById('cameraStatus').innerText = 'Foto Cargada Exitosamente';
            }};
            reader.readAsDataURL(file);
        }}

        function retakeSnap() {{
            selfieDataUrl = '';
            document.getElementById('selfiePreview').classList.add('hidden');
            document.getElementById('videoElement').classList.add('hidden');
            document.getElementById('startCamBtn').classList.remove('hidden');
            document.getElementById('snapBtn').classList.add('hidden');
            document.getElementById('retakeBtn').classList.add('hidden');
            document.getElementById('cameraStatus').innerText = 'Presiona "Cámara en Vivo" o "Tomar / Subir Foto"';
            if (videoStream) {{
                videoStream.getTracks().forEach(t => t.stop());
            }}
        }}

        async function submitBiometricSignature(token) {{
            const check = document.getElementById('acceptCheck').checked;
            if (!hasSignature) return alert('Por favor realiza tu firma digital en el recuadro.');
            if (!selfieDataUrl) return alert('Por favor tómate la selfie o sube tu foto de validación.');
            if (!check) return alert('Debes aceptar la declaración jurada del pagaré.');

            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.innerText = 'Enviando Firma...';

            try {{
                const res = await fetch(`/api/biometric_requests/${{token}}/sign`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ signature_data: canvas.toDataURL('image/png'), selfie_data: selfieDataUrl }})
                }});
                const result = await res.json();
                if (result.success) {{
                    document.getElementById('signCard').style.display = 'none';
                    document.getElementById('successBox').classList.remove('hidden');
                }} else {{
                    alert(result.error || 'Error al guardar la firma');
                    btn.disabled = false;
                    btn.innerText = '✍️ Aceptar & Firmar Pagaré Digital';
                }}
            }} catch(err) {{
                alert('Error de conexión al guardar firma');
                btn.disabled = false;
                btn.innerText = '✍️ Aceptar & Firmar Pagaré Digital';
            }}
        }}
    </script>
</body>
</html>"""
    return render_template_string(html_page)


@app.route('/api/biometric_requests/<token>/sign', methods=['POST'])
def sign_biometric_request(token):
    cleanup_biometric_requests()
    bio_req = BiometricRequest.query.filter_by(token=token).first()
    if not bio_req or bio_req.is_expired:
        if bio_req:
            db.session.delete(bio_req)
            db.session.commit()
        return jsonify({"error": "⏰ El código QR o enlace ha expirado (límite de 30 minutos). Genera una nueva solicitud."}), 400

    if bio_req.status == 'otorgado':
        db.session.delete(bio_req)
        db.session.commit()
        return jsonify({"error": "❌ Este QR ya no está disponible porque el préstamo ya ha sido otorgado."}), 400

    if bio_req.status == 'firmado':
        return jsonify({"success": True, "message": "Esta solicitud ya fue firmada previamente."})
        
    data = request.json or {}
    signature_data = data.get('signature_data', '').strip()
    selfie_data = data.get('selfie_data', '').strip()
    
    if not signature_data or not selfie_data:
        return jsonify({"error": "La firma y la selfie son obligatorias"}), 400
        
    bio_req.signature_data = signature_data
    bio_req.selfie_data = selfie_data
    bio_req.status = 'firmado'
    bio_req.signed_at = datetime.utcnow()
    
    doc_sig = ClientDocument(
        client_id=bio_req.client_id,
        doc_type='firma_digital',
        title=f'Firma Digital Pagaré Express (${bio_req.amount:,.2f})',
        image_data=signature_data
    )
    doc_selfie = ClientDocument(
        client_id=bio_req.client_id,
        doc_type='selfie_deudor',
        title=f'Selfie Biométrica Deudor (${bio_req.amount:,.2f})',
        image_data=selfie_data
    )
    db.session.add_all([doc_sig, doc_selfie])
    
    new_loan = Loan(
        client_id=bio_req.client_id,
        amount=bio_req.amount,
        interest_rate=bio_req.interest_rate,
        rate_type=bio_req.rate_type,
        modality=bio_req.modality,
        installments_count=bio_req.installments_count,
        start_date=date.today(),
        status='pendiente_otorgamiento',
        notes=f"Pagaré Virtual Express firmado el {datetime.now().strftime('%d/%m/%Y %H:%M')}. Selfie y firma registradas.",
        signature_data=signature_data
    )
    db.session.add(new_loan)
    db.session.commit()
    
    schedule = new_loan.generate_amortization_schedule()
    db.session.add_all(schedule)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Firma biométrica y selfie registradas exitosamente. Préstamo pendiente de otorgamiento.",
        "loan_id": new_loan.id
    })


# ----------------------------------------------------
# API SORTEOS & RIFAS EXPRESS
# ----------------------------------------------------
@app.route('/api/sorteos', methods=['GET', 'POST'])
@app.route('/api/raffles', methods=['GET', 'POST'])
def api_raffles():
    if request.method == 'GET':
        raffles = Raffle.query.order_by(Raffle.created_at.desc()).all()
        return jsonify({"success": True, "status": "success", "raffles": [r.to_dict() for r in raffles]})
    
    data = request.get_json() or {}
    title = data.get('title') or 'Sorteo Express'
    motive = data.get('motive') or data.get('description') or ''
    mode = data.get('mode') or 'numbers'
    number_min = int(data.get('number_min') or data.get('range_min') or 1)
    number_max = int(data.get('number_max') or data.get('range_max') or 100)
    ticket_price = float(data.get('ticket_price') or 0.0)
    prizes = data.get('prizes') or []
    participants = data.get('participants') or []
    if not participants and data.get('names_list'):
        participants = [n.strip() for n in str(data.get('names_list')).split('\n') if n.strip()]

    draw_date = data.get('draw_date') or date.today().strftime('%Y-%m-%d')

    raffle = Raffle(
        title=title,
        motive=motive,
        mode=mode,
        number_min=number_min,
        number_max=number_max,
        ticket_price=ticket_price,
        prizes_json=json.dumps(prizes),
        participants_json=json.dumps(participants),
        status='activo',
        draw_date=draw_date
    )
    db.session.add(raffle)
    db.session.commit()
    return jsonify({"success": True, "status": "success", "raffle": raffle.to_dict()}), 201

@app.route('/api/raffles/<int:raffle_id>', methods=['DELETE'])
def delete_raffle(raffle_id):
    r = Raffle.query.get_or_404(raffle_id)
    db.session.delete(r)
    db.session.commit()
    return jsonify({"success": True, "status": "success"})

@app.route('/api/raffles/<int:raffle_id>/draw', methods=['POST'])
def draw_raffle_winners(raffle_id):
    import random
    import hashlib
    r = Raffle.query.get_or_404(raffle_id)
    prizes = json.loads(r.prizes_json) if r.prizes_json else [{"rank": 1, "title": "1° Premio"}]
    participants = json.loads(r.participants_json) if r.participants_json else []
    
    if r.mode == 'numbers':
        pool = [f"Número #{num:02d}" for num in range(r.number_min, r.number_max + 1)]
    else:
        pool = participants if participants else ["Participante Demo 1", "Participante Demo 2"]

    available = list(pool)
    random.shuffle(available)

    winners = []
    for idx, prize in enumerate(prizes):
        winner_name = available.pop(0) if available else f"Ganador #{idx+1}"
        prize_name = prize.get('title') or prize.get('name') if isinstance(prize, dict) else str(prize)
        
        raw_hash_str = f"{r.id}-{winner_name}-{prize_name}-{datetime.utcnow().isoformat()}"
        ticket_hash = hashlib.sha256(raw_hash_str.encode('utf-8')).hexdigest()[:16].upper()
        
        winners.append({
            "rank": idx + 1,
            "prize": prize_name,
            "prize_title": prize_name,
            "winner": winner_name,
            "winner_name": winner_name,
            "ticket_code": f"TICKET-{r.id:03d}-{ticket_hash}",
            "hash": ticket_hash,
            "verification_hash": ticket_hash,
            "draw_timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    r.winners_json = json.dumps(winners)
    r.status = 'completado'
    db.session.commit()
    return jsonify({"success": True, "status": "success", "winners": winners, "raffle": r.to_dict()})

@app.route('/api/generar-flyer', methods=['GET', 'POST'])
def generar_flyer():
    from PIL import Image, ImageDraw, ImageFont
    import io
    import urllib.request
    import urllib.parse
    import random
    
    if request.method == 'POST':
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()
    
    raffle_id = payload.get('raffle_id')
    r_obj = None
    if raffle_id:
        try:
            r_obj = Raffle.query.get(int(raffle_id))
        except Exception:
            pass

    if r_obj:
        title = payload.get('title') or r_obj.title
        motive = payload.get('motive') or r_obj.motive or "Gran Sorteo & Rifa Express"
        draw_date = payload.get('draw_date') or r_obj.draw_date or "Fecha a Confirmar"
        price = float(payload.get('ticket_price') or r_obj.ticket_price or 0.0)
        number_min = int(payload.get('number_min') or r_obj.number_min or 1)
        number_max = int(payload.get('number_max') or r_obj.number_max or 100)
        prizes_str = payload.get('prizes') or (json.loads(r_obj.prizes_json) if r_obj.prizes_json else "1° Premio")
    else:
        title = payload.get('title') or "GRAN SORTEO Y RIFA FAMILIAR"
        motive = payload.get('motive') or "Beneficio Fondo de la Casa & Actividades"
        draw_date = payload.get('draw_date') or "Próximo Sábado 20:00 hs"
        price = float(payload.get('ticket_price') or 1500.0)
        number_min = int(payload.get('number_min') or 1)
        number_max = int(payload.get('number_max') or 100)
        prizes_str = payload.get('prizes') or "1° Premio: Asado Completo + Vino\n2° Premio: Postre Familiar + Sidra"

    use_ai = str(payload.get('use_ai') or payload.get('ai') or '0').lower() in ['1', 'true', 'yes']
    W, H = 1080, 1350
    ai_img = None

    if use_ai:
        try:
            prompt_str = f"vibrant gold luxury raffle trophy background {title} {motive} dark glassmorphism 2026 aesthetics"
            encoded_prompt = urllib.parse.quote(prompt_str[:120])
            ai_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&nologo=true&seed={random.randint(100, 99999)}"
            req = urllib.request.Request(ai_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                ai_data = resp.read()
                ai_img = Image.open(io.BytesIO(ai_data)).convert('RGB')
                ai_img = ai_img.resize((W, H))
        except Exception as err:
            print(f"[AI Flyer Image Generator Fallback]: {err}")
            ai_img = None

    if ai_img:
        overlay = Image.new('RGBA', (W, H), (15, 23, 42, 170))
        img = Image.alpha_composite(ai_img.convert('RGBA'), overlay).convert('RGB')
    else:
        img = Image.new('RGB', (W, H), color='#0f172a')
        draw_bg = ImageDraw.Draw(img)
        for y in range(260):
            r_c = int(15 + (y / 260) * 20)
            g_c = int(23 + (y / 260) * 100)
            b_c = int(42 + (y / 260) * 160)
            draw_bg.line([(0, y), (W, y)], fill=(r_c, g_c, b_c))

    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_sub = ImageFont.truetype("arial.ttf", 30)
        font_body = ImageFont.truetype("arial.ttf", 26)
        font_num = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font_title = font_sub = font_body = font_num = ImageFont.load_default()

    draw.rounded_rectangle([60, 35, W - 60, 110], radius=20, fill='#0284c7', outline='#38bdf8', width=2)
    draw.text((W // 2, 72), "🎲 SORTEO EXPRESS & RIFA IA 🎲", fill="#ffffff", font=font_sub, anchor="mm")

    draw.text((W // 2, 170), title.upper(), fill="#ffffff", font=font_title, anchor="mm")
    draw.text((W // 2, 225), f"📌 {motive}", fill="#38bdf8", font=font_sub, anchor="mm")

    draw.rounded_rectangle([60, 270, W - 60, 420], radius=20, fill='#1e293b', outline='#6366f1', width=3)
    draw.text((80, 295), "🏆 PREMIOS DESTACADOS:", fill="#f59e0b", font=font_sub)
    
    if isinstance(prizes_str, list):
        prize_lines = [p.get('name', str(p)) if isinstance(p, dict) else str(p) for p in prizes_str]
    else:
        prize_lines = str(prizes_str).split('\n')
        
    y_p = 340
    for line in prize_lines[:3]:
        draw.text((90, y_p), f"✨ {line.strip()}", fill="#ffffff", font=font_body)
        y_p += 35

    draw.text((W // 2, 455), f"SELECCIONÁ TU NÚMERO ({number_min:02d} al {number_max:02d})", fill="#e2e8f0", font=font_sub, anchor="mm")

    total_nums = min(100, number_max - number_min + 1)
    cols = 10
    rows = (total_nums + cols - 1) // cols
    grid_top = 490
    grid_left = 60
    cell_w = (W - 120) // cols
    cell_h = min(48, 680 // max(1, rows))

    for idx in range(total_nums):
        num = number_min + idx
        r_i = idx // cols
        c_i = idx % cols
        x1 = grid_left + c_i * cell_w + 3
        y1 = grid_top + r_i * cell_h + 3
        x2 = x1 + cell_w - 6
        y2 = y1 + cell_h - 6
        
        draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill='#090d16', outline='#334155', width=1)
        draw.text(((x1 + x2) // 2, (y1 + y2) // 2), f"{num:02d}", fill="#94a3b8", font=font_num, anchor="mm")

    footer_top = H - 170
    draw.rounded_rectangle([60, footer_top, W - 60, H - 40], radius=25, fill='#0284c7', outline='#38bdf8', width=3)
    draw.text((100, footer_top + 40), f"💵 VALOR DEL NÚMERO: ${price:,.2f}", fill="#ffffff", font=font_sub)
    draw.text((100, footer_top + 85), f"📅 FECHA DE SORTEO: {draw_date}", fill="#e0f2fe", font=font_body)
    draw.text((W - 90, footer_top + 60), "VERIFICADO ✓", fill="#fef08a", font=font_sub, anchor="rm")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=False, download_name='flyer_sorteo_ia.png')


@app.route('/api/generar-cartones-bingo', methods=['GET', 'POST'])
def generar_cartones_bingo():
    from PIL import Image, ImageDraw, ImageFont
    import random
    import io
    
    if request.method == 'POST':
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()

    raffle_title = payload.get('title') or "GRAN BINGO FAMILIAR 2026"
    mode = str(payload.get('mode') or '75')
    cards_count = min(10, max(1, int(payload.get('count') or payload.get('quantity') or 2)))

    W, H = 1200, 1600
    img = Image.new('RGB', (W, H), color='#090d16')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 45)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_num = ImageFont.truetype("arial.ttf", 32)
        font_header = ImageFont.truetype("arial.ttf", 34)
    except Exception:
        font_title = font_sub = font_num = font_header = ImageFont.load_default()

    draw.rounded_rectangle([40, 30, W - 40, 120], radius=20, fill='#1e1b4b', outline='#6366f1', width=3)
    draw.text((W // 2, 75), f"🎱 {raffle_title.upper()} 🎱", fill="#ffffff", font=font_title, anchor="mm")
    draw.text((W // 2, 145), f"CARTONES OFICIALES DE BINGO (MODO {mode} BOLILLAS) • GENERADO CON IA", fill="#a5b4fc", font=font_sub, anchor="mm")

    cards_per_page = min(2, cards_count)
    card_w = W - 120
    card_h = 640
    
    for c_idx in range(cards_per_page):
        top_y = 190 + c_idx * 680
        
        draw.rounded_rectangle([60, top_y, 60 + card_w, top_y + card_h], radius=25, fill='#0f172a', outline='#f59e0b', width=3)
        
        draw.rounded_rectangle([75, top_y + 15, 60 + card_w - 15, top_y + 75], radius=15, fill='#d97706', outline='#fbbf24', width=2)
        card_id_str = f"CARTÓN N° #{c_idx + 1:03d} • HASH: BINGO-{random.randint(1000, 9999)}"
        draw.text((W // 2, top_y + 45), card_id_str, fill="#ffffff", font=font_header, anchor="mm")

        if mode == '75':
            headers = ["B", "I", "N", "G", "O"]
            cols = 5
            rows = 5
            col_w = (card_w - 40) // cols
            row_h = (card_h - 120) // (rows + 1)
            grid_left = 80
            grid_top = top_y + 90
            
            for ci, h_letter in enumerate(headers):
                cx1 = grid_left + ci * col_w
                cy1 = grid_top
                cx2 = cx1 + col_w - 6
                cy2 = cy1 + row_h - 6
                draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=10, fill='#4338ca', outline='#818cf8', width=2)
                draw.text(((cx1 + cx2) // 2, (cy1 + cy2) // 2), h_letter, fill="#ffffff", font=font_header, anchor="mm")

            col_ranges = [(1,15), (16,30), (31,45), (46,60), (61,75)]
            card_grid = []
            for col_i in range(5):
                nums = random.sample(range(col_ranges[col_i][0], col_ranges[col_i][1] + 1), 5)
                card_grid.append(nums)

            for ri in range(5):
                for ci in range(5):
                    cx1 = grid_left + ci * col_w
                    cy1 = grid_top + (ri + 1) * row_h
                    cx2 = cx1 + col_w - 6
                    cy2 = cy1 + row_h - 6
                    
                    if ri == 2 and ci == 2:
                        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=12, fill='#b45309', outline='#f59e0b', width=2)
                        draw.text(((cx1 + cx2) // 2, (cy1 + cy2) // 2), "⭐ LIBRE ⭐", fill="#fef08a", font=font_sub, anchor="mm")
                    else:
                        num_val = card_grid[ci][ri]
                        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=12, fill='#1e293b', outline='#334155', width=1)
                        draw.text(((cx1 + cx2) // 2, (cy1 + cy2) // 2), f"{num_val:02d}", fill="#ffffff", font=font_num, anchor="mm")

        else: # 90 balls
            cols = 9
            rows = 3
            col_w = (card_w - 40) // cols
            row_h = (card_h - 110) // rows
            grid_left = 80
            grid_top = top_y + 90
            
            for ri in range(3):
                row_nums = random.sample(range(1, 91), 5)
                row_nums.sort()
                positions = sorted(random.sample(range(9), 5))
                pos_idx = 0
                
                for ci in range(9):
                    cx1 = grid_left + ci * col_w
                    cy1 = grid_top + ri * row_h
                    cx2 = cx1 + col_w - 4
                    cy2 = cy1 + row_h - 4
                    
                    if ci in positions:
                        num_val = row_nums[pos_idx]
                        pos_idx += 1
                        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=10, fill='#1e293b', outline='#475569', width=1)
                        draw.text(((cx1 + cx2) // 2, (cy1 + cy2) // 2), f"{num_val:02d}", fill="#ffffff", font=font_num, anchor="mm")
                    else:
                        draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=10, fill='#090d16', outline='#1e293b', width=1)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=False, download_name='cartones_bingo.png')


# ----------------------------------------------------
# API GESTIÓN DE COMPRAS, PIZARRA & CALENDARIO
# ----------------------------------------------------
@app.route('/api/shopping', methods=['GET', 'POST'])
def api_shopping():
    if request.method == 'GET':
        items = ShoppingItem.query.order_by(ShoppingItem.is_checked.asc(), ShoppingItem.id.desc()).all()
        return jsonify({"success": True, "items": [i.to_dict() for i in items]})
    
    data = request.get_json() or {}
    item = ShoppingItem(
        store_category=data.get('store_category') or 'supermercado',
        item_name=data.get('item_name') or 'Producto',
        quantity=data.get('quantity') or '1',
        is_checked=bool(data.get('is_checked', False)),
        added_by=data.get('added_by') or 'Familia'
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"success": True, "item": item.to_dict()})

@app.route('/api/shopping/<int:item_id>/toggle', methods=['POST'])
def toggle_shopping_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    item.is_checked = not item.is_checked
    db.session.commit()
    return jsonify({"success": True, "item": item.to_dict()})

@app.route('/api/shopping/<int:item_id>', methods=['DELETE'])
def delete_shopping_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/noticeboard', methods=['GET', 'POST'])
def api_noticeboard():
    if request.method == 'GET':
        items = NoticeBoardItem.query.order_by(NoticeBoardItem.is_pinned.desc(), NoticeBoardItem.created_at.desc()).all()
        return jsonify({"success": True, "notices": [i.to_dict() for i in items]})
    
    data = request.get_json() or {}
    item = NoticeBoardItem(
        author=data.get('author') or 'Familia',
        message=data.get('message') or '',
        is_pinned=bool(data.get('is_pinned', False))
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"success": True, "notice": item.to_dict()})

@app.route('/api/noticeboard/<int:notice_id>', methods=['DELETE'])
def delete_noticeboard(notice_id):
    item = NoticeBoardItem.query.get_or_404(notice_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/home-calendar', methods=['GET', 'POST'])
def api_home_calendar():
    if request.method == 'GET':
        items = HomeCalendarItem.query.order_by(HomeCalendarItem.due_date.asc()).all()
        return jsonify({"success": True, "events": [i.to_dict() for i in items]})
    
    data = request.get_json() or {}
    item = HomeCalendarItem(
        title=data.get('title') or 'Evento / Turno',
        category=data.get('category') or 'servicio',
        due_date=data.get('due_date') or date.today().strftime('%Y-%m-%d'),
        due_time=data.get('due_time') or '',
        notes=data.get('notes') or '',
        is_completed=bool(data.get('is_completed', False))
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"success": True, "event": item.to_dict()})

@app.route('/api/home-calendar/<int:event_id>', methods=['DELETE'])
def delete_home_calendar(event_id):
    item = HomeCalendarItem.query.get_or_404(event_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"success": True})

# ----------------------------------------------------
# ZERO-UI VOICE/TEXT AUDIO PARSER & WHATSAPP WEBHOOK
# ----------------------------------------------------
def process_zero_ui_text(raw_text, source="Voz/Zero-UI"):
    raw_text = (raw_text or '').strip()
    if not raw_text:
        return {"success": False, "status": "error", "error": "No se recibió texto o audio para procesar."}

    created_items = {"shopping": [], "calendar": [], "notices": []}

    shopping_keywords = ["comprar", "compras", "detergente", "leche", "tomates", "pan", "carne", "clavos", "supermercado", "verdulería", "ferretería", "aceite", "jabón", "fideos", "harina"]
    calendar_keywords = ["turno", "dentista", "médico", "vacuna", "examen", "colegio", "vencimiento", "factura", "jueves", "martes", "miércoles", "viernes", "sábado", "domingo", "lunes"]

    sentences = [s.strip() for s in raw_text.replace('\n', '.').split('.') if s.strip()]
    if not sentences:
        sentences = [raw_text]

    for sentence in sentences:
        s_lower = sentence.lower()
        
        if any(k in s_lower for k in shopping_keywords) or "anotát" in s_lower or "comprar" in s_lower or "compras" in s_lower:
            cat = 'supermercado'
            if any(k in s_lower for k in ['tomate', 'verdura', 'fruta', 'papa', 'cebolla']):
                cat = 'verduleria'
            elif any(k in s_lower for k in ['clavo', 'cinta', 'tornillo', 'cable', 'pintura']):
                cat = 'ferreteria'
            elif any(k in s_lower for k in ['remedio', 'remédio', 'remedios', 'aspirina', 'farmacia']):
                cat = 'farmacia'

            item = ShoppingItem(store_category=cat, item_name=sentence.capitalize(), quantity="1", added_by=source)
            db.session.add(item)
            db.session.commit()
            created_items["shopping"].append(item.to_dict())

        elif any(k in s_lower for k in calendar_keywords):
            cat = 'servicio'
            if any(k in s_lower for k in ['médico', 'dentista', 'doctor', 'salud', 'clinica']):
                cat = 'medico'
            elif any(k in s_lower for k in ['vacuna', 'perro', 'gato', 'mascota', 'veterinaria']):
                cat = 'mascota'
            elif any(k in s_lower for k in ['examen', 'prueba', 'colegio', 'escuela']):
                cat = 'examen'

            ev = HomeCalendarItem(title=sentence.capitalize(), category=cat, due_date=(date.today() + timedelta(days=2)).strftime('%Y-%m-%d'), due_time="17:00", notes=f"Registrado desde {source}")
            db.session.add(ev)
            db.session.commit()
            created_items["calendar"].append(ev.to_dict())

        else:
            n = NoticeBoardItem(author=source, message=sentence.capitalize(), is_pinned=False)
            db.session.add(n)
            db.session.commit()
            created_items["notices"].append(n.to_dict())

    return {
        "status": "success",
        "success": True,
        "raw_text": raw_text,
        "summary": f"Se procesó la nota: {len(created_items['shopping'])} compras, {len(created_items['calendar'])} turnos y {len(created_items['notices'])} avisos.",
        "created_items": created_items,
        "result": {
            "shopping": [i["name"] for i in created_items["shopping"]],
            "calendar": [i["title"] for i in created_items["calendar"]],
            "notices": [i["content"] for i in created_items["notices"]]
        }
    }


@app.route('/api/hogar/parse-audio', methods=['POST'])
def parse_audio_note():
    data = request.get_json() or {}
    raw_text = (data.get('audio_text') or data.get('raw_text') or data.get('text') or data.get('transcript') or '').strip()
    
    if not raw_text:
        return jsonify({"success": False, "status": "error", "error": "No se recibió texto o audio para procesar."}), 400

    result = process_zero_ui_text(raw_text, source="Voz/Zero-UI")
    return jsonify(result)


@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token') or request.args.get('token')
        challenge = request.args.get('hub.challenge')
        if challenge:
            return str(challenge), 200
        return jsonify({"status": "active", "service": "WhatsApp Webhook Listener", "endpoint": "/api/whatsapp/webhook"}), 200

    payload = request.get_json(silent=True) or {}
    form_data = request.form.to_dict() or {}
    
    raw_text = (
        form_data.get('Body') or 
        form_data.get('message') or 
        payload.get('audio_text') or 
        payload.get('text') or 
        payload.get('transcript') or 
        payload.get('message') or ''
    ).strip()

    if not raw_text and 'entry' in payload:
        try:
            entry = payload['entry'][0]
            changes = entry['changes'][0]
            msg = changes['value']['messages'][0]
            if msg.get('type') == 'text':
                raw_text = msg['text']['body']
            elif msg.get('type') == 'audio':
                raw_text = payload.get('transcript') or "Nota de voz recibida por WhatsApp"
        except Exception:
            pass

    if not raw_text:
        return jsonify({"status": "ignored", "reason": "No text content found in request."}), 200

    result = process_zero_ui_text(raw_text, source="WhatsApp Voz")
    
    sh_cnt = len(result.get("created_items", {}).get("shopping", []))
    cal_cnt = len(result.get("created_items", {}).get("calendar", []))
    not_cnt = len(result.get("created_items", {}).get("notices", []))
    
    reply_msg = f"📱 *¡Agendado Exitosamente en tu App de Préstamos & Hogar!*\n\n" \
                f"📝 *Texto*: \"{raw_text}\"\n" \
                f"🛒 *Compras*: {sh_cnt}\n" \
                f"📅 *Turnos*: {cal_cnt}\n" \
                f"📌 *Pizarra*: {not_cnt}\n\n" \
                f"✨ _Auto-agendado desde tu móvil 2026_"

    if 'Body' in form_data:
        twiml_xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{reply_msg}</Message></Response>"
        return Response(twiml_xml, mimetype='application/xml')

    return jsonify({
        "status": "success",
        "success": True,
        "reply_text": reply_msg,
        "result": result
    }), 200



@app.route('/api/comidas/calculate', methods=['POST'])
@app.route('/api/asado/calculate', methods=['POST'])
def calculate_comidas():
    import math
    data = request.get_json() or {}
    
    event_type = (data.get('event_type') or data.get('menu_type') or 'asado').lower() # asado, pizza, tacos, disco, hamburguesas, custom
    people = max(1, int(data.get('people') or data.get('diners_count') or data.get('adults') or 10))
    adults = max(0, int(data.get('adults') or people))
    children = max(0, int(data.get('children') or 0))
    vegetarians = max(0, int(data.get('vegetarians') or 0))
    ticket_price = float(data.get('ticket_price') or 0.0)
    bought_items = data.get('bought_items') or data.get('items') or []

    ingredients_list = []
    
    if event_type == 'pizza':
        pizzas_count = math.ceil((adults * 0.5) + (children * 0.25))
        cheese_kg = round(pizzas_count * 0.25, 2)
        flour_kg = round(pizzas_count * 0.2, 2)
        sauce_lts = round(pizzas_count * 0.1, 2)
        soda_liters = round((adults + children) * 1.0, 1)
        beer_bottles = math.ceil(adults * 0.8)

        ingredients_list = [
            {"item": "Pizzas Estimadas", "qty": f"{pizzas_count} unidades"},
            {"item": "Queso Muzzarella", "qty": f"{cheese_kg} kg"},
            {"item": "Harina 0000", "qty": f"{flour_kg} kg"},
            {"item": "Salsa de Tomate", "qty": f"{sauce_lts} Lts"},
            {"item": "Gaseosas", "qty": f"{soda_liters} Lts"},
            {"item": "Cerveza / Bebidas", "qty": f"{beer_bottles} botellas/latas"}
        ]
        menu_name = "Noche de Pizzas Caseras 🍕"

    elif event_type == 'tacos':
        tacos_count = (adults * 4) + (children * 2)
        meat_kg = round((adults + children) * 0.2, 2)
        tortillas_packs = math.ceil(tacos_count / 12.0)
        guacamole_kg = round(people * 0.08, 2)
        cheese_kg = round(people * 0.08, 2)
        soda_liters = round(people * 1.0, 1)

        ingredients_list = [
            {"item": "Tacos Estimados", "qty": f"{tacos_count} tacos"},
            {"item": "Carne Picada / Pollo", "qty": f"{meat_kg} kg"},
            {"item": "Paquetes de Tortillas (x12)", "qty": f"{tortillas_packs} paquetes"},
            {"item": "Guacamole / Palta", "qty": f"{guacamole_kg} kg"},
            {"item": "Queso Rallado / Cheddar", "qty": f"{cheese_kg} kg"},
            {"item": "Gaseosas / Bebidas", "qty": f"{soda_liters} Lts"}
        ]
        menu_name = "Taquiza & Noche de Tacos 🌮"

    elif event_type == 'disco':
        chicken_kg = round(people * 0.4, 2)
        potatoes_kg = round(people * 0.25, 2)
        peppers_kg = round(people * 0.1, 2)
        wine_white_bottles = math.ceil(people / 6.0)
        bread_kg = round(people * 0.15, 2)

        ingredients_list = [
            {"item": "Pollo Trozado", "qty": f"{chicken_kg} kg"},
            {"item": "Papas / Cebollas", "qty": f"{potatoes_kg} kg"},
            {"item": "Morrones / Pimientos", "qty": f"{peppers_kg} kg"},
            {"item": "Vino Blanco para Cocinar", "qty": f"{wine_white_bottles} botellas"},
            {"item": "Pan para Acompañar", "qty": f"{bread_kg} kg"}
        ]
        menu_name = "Pollo al Disco & Cazuela 🥘"

    elif event_type == 'hamburguesas':
        burgers_count = (adults * 2) + children
        meat_kg = round(burgers_count * 0.15, 2)
        buns_packs = math.ceil(burgers_count / 4.0)
        cheddar_slices = burgers_count
        french_fries_kg = round(people * 0.2, 2)

        ingredients_list = [
            {"item": "Medallones de Hamburguesa", "qty": f"{burgers_count} unidades ({meat_kg} kg)"},
            {"item": "Panes de Hamburguesa", "qty": f"{burgers_count} panes ({buns_packs} paq.)"},
            {"item": "Fetas de Queso Cheddar", "qty": f"{cheddar_slices} fetas"},
            {"item": "Papas Fritas", "qty": f"{french_fries_kg} kg"}
        ]
        menu_name = "Hamburguesada Familiar 🍔"

    elif event_type == 'custom':
        ingredients_list = [
            {"item": "Insumos Personalizados", "qty": f"{people} comensales"}
        ]
        menu_name = "Menú Personalizado & Juntada Libre 🎨"

    else: # Asado Tradicional (Default)
        eaters_meat = max(0, adults - vegetarians)
        meat_kg = round(eaters_meat * 0.5 + children * 0.25, 2)
        veggie_kg = round(vegetarians * 0.4, 2)
        bread_kg = round(people * 0.15, 2)
        coal_bags = math.ceil(max(1.0, (meat_kg + veggie_kg) / 5.0))
        soda_liters = round(people * 1.0, 1)
        wine_bottles = math.ceil(adults * 0.75)

        ingredients_list = [
            {"item": "Carne (Asado/Vacío/Chorizos)", "qty": f"{meat_kg} kg"},
            {"item": "Verduras / Ensaladas", "qty": f"{veggie_kg} kg"},
            {"item": "Pan Francés", "qty": f"{bread_kg} kg"},
            {"item": "Bolsas de Carbón", "qty": f"{coal_bags} bolsa(s)"},
            {"item": "Gaseosas", "qty": f"{soda_liters} Lts"},
            {"item": "Vino / Cerveza", "qty": f"{wine_bottles} botellas"}
        ]
        menu_name = "Asado Tradicional 🥩"

    parsed_items = []
    total_cost = 0.0
    category_labels = {
        'alimentos': '🥩 Alimentos',
        'bebidas': '🍷 Bebidas',
        'postres': '🍰 Postres',
        'varios': '📦 Artículos Varios'
    }
    
    for item in bought_items:
        if isinstance(item, dict):
            name = (item.get('name') or item.get('item') or '').strip()
            cost = float(item.get('cost') or item.get('price') or 0.0)
            cat = item.get('category') or 'alimentos'
        else:
            name = str(item).strip()
            cost = 0.0
            cat = 'alimentos'
        if name:
            cat_lbl = category_labels.get(cat, '🥩 Alimentos')
            parsed_items.append({"name": name, "cost": cost, "price": cost, "category": cat, "category_label": cat_lbl})
            total_cost += cost

    if total_cost == 0.0 and ticket_price > 0:
        total_cost = ticket_price * people

    per_person_cost = round(total_cost / max(1, people), 2)

    wa_summary = f"""🍽️ *REPORTE IA: {menu_name.upper()}* 🍽️
👥 *Comensales*: {people} personas ({adults} Adultos, {children} Niños)

📌 *INSUMOS SUGERIDOS DE REFERENCIA*:
"""
    for ing in ingredients_list:
        wa_summary += f"• *{ing['item']}*: {ing['qty']}\n"

    if parsed_items:
        wa_summary += f"\n💰 *DESGLOSE DE COMPRAS REGISTRADAS POR CATEGORÍA*:\n"
        grouped_items = {}
        for p in parsed_items:
            cat_lbl = p['category_label']
            if cat_lbl not in grouped_items:
                grouped_items[cat_lbl] = []
            grouped_items[cat_lbl].append(p)
            
        for cat_lbl, cat_list in grouped_items.items():
            wa_summary += f"\n*{cat_lbl}*:\n"
            for p in cat_list:
                wa_summary += f"  • {p['name']}: ${p['cost']:,.2f}\n"

    wa_summary += f"\n💵 *PRORRATEO FINAL*:\n" \
                  f"• 💰 *Gasto Total*: ${total_cost:,.2f}\n" \
                  f"• 👤 *Monto por Persona*: ${per_person_cost:,.2f}\n\n" \
                  f"_Generado automáticamente por Sistema de Gestión de Préstamos & Hogar 2026_"

    result_dict = {
        "menu_name": menu_name,
        "event_type": event_type,
        "people": people,
        "adults": adults,
        "children": children,
        "vegetarians": vegetarians,
        "ingredients": ingredients_list,
        "bought_items": parsed_items,
        "total_cost": total_cost,
        "estimated_cost_per_person": per_person_cost,
        "per_person_cost": per_person_cost,
        "meat_kg": ingredients_list[0]['qty'] if ingredients_list else "0 kg",
        "wa_share_string": wa_summary,
        "whatsapp_text": wa_summary
    }

    return jsonify({
        "status": "success",
        "success": True,
        "data": result_dict,
        "calculation": result_dict
    })


@app.route('/api/comidas/pdf', methods=['GET', 'POST'])
def generar_comidas_pdf():
    from PIL import Image, ImageDraw, ImageFont
    import io
    import base64
    
    if request.method == 'POST':
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()

    people = int(payload.get('people') or 10)
    total_cost = float(payload.get('total_cost') or payload.get('total_expense') or 0.0)
    per_person = float(payload.get('per_person_cost') or payload.get('estimated_cost_per_person') or 0.0)
    menu_name = payload.get('menu_name') or "Juntada & Evento Gastronómico"
    items = payload.get('bought_items') or payload.get('ingredients') or []

    ticket_images_raw = payload.get('ticket_images') or payload.get('ticket_photos') or []
    decoded_ticket_imgs = []
    if isinstance(ticket_images_raw, list):
        for b64_item in ticket_images_raw:
            try:
                if isinstance(b64_item, str) and b64_item.strip():
                    clean_b64 = b64_item.split(',')[-1]
                    img_bytes = base64.b64decode(clean_b64)
                    t_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                    decoded_ticket_imgs.append(t_img)
            except Exception as err:
                print(f"[Error decoding ticket photo]: {err}")

    W = 1200
    items_count = len(items) if isinstance(items, list) and items else 1
    base_table_height = 550 + (items_count * 50) + 120

    ticket_section_h = 0
    if decoded_ticket_imgs:
        ticket_rows = (len(decoded_ticket_imgs) + 1) // 2
        ticket_section_h = 100 + (ticket_rows * 420)

    H = max(1600, base_table_height + ticket_section_h + 200)

    img = Image.new('RGB', (W, H), color='#ffffff')
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 40)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_body = ImageFont.truetype("arial.ttf", 22)
        font_cat = ImageFont.truetype("arial.ttf", 22)
        font_caption = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = font_sub = font_body = font_cat = font_caption = ImageFont.load_default()

    # Header
    draw.rectangle([0, 0, W, 180], fill='#0f172a')
    draw.text((W // 2, 70), "🍽️ COMPROBANTE OFICIAL DE JUNTADA", fill="#ffffff", font=font_title, anchor="mm")
    draw.text((W // 2, 130), f"{menu_name.upper()} • PRORRATEO DE GASTOS", fill="#38bdf8", font=font_sub, anchor="mm")

    # Info & Totals
    draw.text((80, 220), f"📅 FECHA DE EMISIÓN: {date.today().strftime('%d/%m/%Y')}", fill="#475569", font=font_sub)
    draw.text((80, 260), f"👥 ASISTENTES TOTALES: {people} Personas", fill="#475569", font=font_sub)

    draw.rounded_rectangle([80, 310, W - 80, 440], radius=20, fill='#f8fafc', outline='#cbd5e1', width=2)
    draw.text((120, 345), f"💵 GASTO TOTAL: ${total_cost:,.2f}", fill="#0f172a", font=font_title)
    draw.text((120, 395), f"👤 MONTO INDIVIDUAL POR PERSONA: ${per_person:,.2f}", fill="#16a34a", font=font_sub)

    # Ingredients Table
    draw.rectangle([80, 480, W - 80, 530], fill='#1e293b')
    draw.text((110, 495), "DESCRIPCIÓN / INGREDIENTE", fill="#ffffff", font=font_sub)
    draw.text((W - 120, 495), "COSTO ($)", fill="#ffffff", font=font_sub, anchor="rm")

    curr_y = 550
    if isinstance(items, list) and items:
        # Group items by category if available
        grouped = {}
        for it in items:
            if isinstance(it, dict):
                cat_lbl = it.get('category_label') or '🥩 Alimentos'
                name = it.get('name') or it.get('item') or ''
                cost = float(it.get('cost') or it.get('price') or 0.0)
            else:
                cat_lbl = '🥩 Alimentos'
                name = str(it)
                cost = 0.0
            if name:
                if cat_lbl not in grouped: grouped[cat_lbl] = []
                grouped[cat_lbl].append((name, cost))

        for cat_lbl, cat_items in grouped.items():
            draw.rectangle([80, curr_y, W - 80, curr_y + 35], fill='#f1f5f9')
            draw.text((100, curr_y + 6), cat_lbl, fill="#0f172a", font=font_cat)
            curr_y += 40
            for name, cost in cat_items:
                draw.line([(80, curr_y + 32), (W - 80, curr_y + 32)], fill='#e2e8f0', width=1)
                draw.text((120, curr_y + 4), f"• {name}", fill="#334155", font=font_body)
                draw.text((W - 120, curr_y + 4), f"${cost:,.2f}", fill="#0f172a", font=font_body, anchor="rm")
                curr_y += 40
            curr_y += 10
    else:
        draw.text((110, curr_y + 5), "• Prorrateo calculado automáticamente según comensales", fill="#64748b", font=font_body)
        curr_y += 45

    # Render Uploaded Ticket Photos
    if decoded_ticket_imgs:
        curr_y += 40
        draw.rectangle([80, curr_y, W - 80, curr_y + 50], fill='#0f172a')
        draw.text((110, curr_y + 15), f"📷 COMPROBANTES Y TICKETS ADJUNTOS ({len(decoded_ticket_imgs)})", fill="#f59e0b", font=font_sub)
        curr_y += 70

        for idx, t_img in enumerate(decoded_ticket_imgs):
            col = idx % 2
            row = idx // 2
            
            x1 = 80 + col * 530
            y1 = curr_y + row * 410
            x2 = x1 + 510
            y2 = y1 + 390
            
            draw.rounded_rectangle([x1, y1, x2, y2], radius=15, fill='#f8fafc', outline='#cbd5e1', width=2)
            draw.text((x1 + 15, y1 + 15), f"Ticket #{idx + 1} - Foto de Comprobante", fill="#1e293b", font=font_caption)
            
            thumb_w = 480
            thumb_h = 320
            
            t_resized = t_img.copy()
            t_resized.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            
            paste_x = x1 + 15 + (thumb_w - t_resized.width) // 2
            paste_y = y1 + 45 + (thumb_h - t_resized.height) // 2
            
            img.paste(t_resized, (paste_x, paste_y))

    # Footer
    footer_y = H - 90
    draw.line([(80, footer_y - 20), (W - 80, footer_y - 20)], fill='#cbd5e1', width=2)
    draw.text((W // 2, footer_y + 10), "Sistema de Gestión de Préstamos, Sorteos & Finanzas 2026", fill="#94a3b8", font=font_sub, anchor="mm")

    img_io = io.BytesIO()
    img.save(img_io, 'PNG', quality=95)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=False, download_name='comprobante_juntada.png')



import webbrowser
import threading

def open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    with app.app_context():
        init_db_and_seeds()
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    is_render = os.environ.get('RENDER') is not None or os.environ.get('PORT') is not None

    print("==========================================================")
    print("SISTEMA DE GESTION DE PRESTAMOS INICIADO CORRECTAMENTE")
    print(f"Servidor ejecutándose en: http://{host}:{port}")
    print("==========================================================")
    
    # Auto-open browser in thread only when running locally
    if not is_render:
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        from waitress import serve
        print(f"[Servidor WSGI Producción Waitress Activo]")
        serve(app, host=host, port=port)
    except ImportError:
        try:
            app.run(host=host, port=port, debug=False, use_reloader=False)
        except Exception as err:
            print(f"\n[ERROR AL INICIAR]: {err}")

