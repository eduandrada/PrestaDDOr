import json
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    whatsapp = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    cuit = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship('Loan', backref='client', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='client', lazy=True, cascade="all, delete-orphan")
    documents = db.relationship('ClientDocument', backref='client', lazy=True, cascade="all, delete-orphan", order_by="ClientDocument.created_at.desc()")
    biometric_requests = db.relationship('BiometricRequest', backref='client', lazy=True, cascade="all, delete-orphan")

    def calculate_scoring_and_status(self):
        all_installments = []
        for loan in self.loans:
            all_installments.extend(loan.installments)
        
        completed_loans_count = len([l for l in self.loans if l.status == 'completado'])
        active_loans_count = len([l for l in self.loans if l.status == 'activo'])

        if not all_installments:
            return {
                "score_stars": 5,
                "score_points": 100,
                "risk_level": "Bajo",
                "recommended_limit": 150000.0,
                "traffic_light": "verde",
                "traffic_light_label": "Sin historial (Nuevo - Crédito Inicial)",
                "total_loans": len(self.loans),
                "active_loans": active_loans_count,
                "completed_loans": completed_loans_count,
                "on_time_rate": 100.0
            }
        
        total_paid_installments = 0
        on_time_paid = 0
        grace_paid = 0
        late_paid_or_overdue = 0
        
        today = date.today()

        for inst in all_installments:
            grace_days = inst.loan.grace_days or 0
            due_date = inst.due_date
            
            if inst.status == 'pagado' and inst.paid_date:
                total_paid_installments += 1
                delay_days = (inst.paid_date - due_date).days
                if delay_days <= 0:
                    on_time_paid += 1
                elif delay_days <= grace_days + 3:
                    grace_paid += 1
                else:
                    late_paid_or_overdue += 1
            elif inst.status != 'pagado' and due_date < today:
                delay_days = (today - due_date).days
                if delay_days > grace_days:
                    late_paid_or_overdue += 1
                elif delay_days > 0:
                    grace_paid += 1

        total_evaluated = total_paid_installments + late_paid_or_overdue
        if total_evaluated == 0:
            return {
                "score_stars": 5,
                "score_points": 100,
                "risk_level": "Bajo",
                "recommended_limit": 150000.0,
                "traffic_light": "verde",
                "traffic_light_label": "Al día",
                "total_loans": len(self.loans),
                "active_loans": active_loans_count,
                "completed_loans": completed_loans_count,
                "on_time_rate": 100.0
            }

        on_time_percentage = ((on_time_paid + (grace_paid * 0.7)) / max(1, total_evaluated)) * 100.0
        score_pts = min(100, max(10, int(on_time_percentage + (completed_loans_count * 5) - (late_paid_or_overdue * 10))))

        if score_pts >= 85:
            stars = 5
            risk_level = "Bajo"
            rec_limit = 250000.0
        elif score_pts >= 70:
            stars = 4
            risk_level = "Bajo-Medio"
            rec_limit = 150000.0
        elif score_pts >= 50:
            stars = 3
            risk_level = "Medio"
            rec_limit = 80000.0
        elif score_pts >= 30:
            stars = 2
            risk_level = "Alto"
            rec_limit = 40000.0
        else:
            stars = 1
            risk_level = "Muy Alto"
            rec_limit = 15000.0

        if late_paid_or_overdue > 1 or (total_evaluated > 0 and late_paid_or_overdue / total_evaluated > 0.3):
            traffic_light = "rojo"
            label = f"Mora Reincidente (Riesgo {risk_level} - Limitar Cupo)"
        elif grace_paid > 0 or late_paid_or_overdue == 1:
            traffic_light = "amarillo"
            label = f"Pagos en gracia / Demoras leves (Riesgo {risk_level})"
        else:
            traffic_light = "verde"
            label = f"Cliente Confiable (Riesgo {risk_level})"

        return {
            "score_stars": stars,
            "score_points": score_pts,
            "risk_level": risk_level,
            "recommended_limit": rec_limit,
            "traffic_light": traffic_light,
            "traffic_light_label": label,
            "total_loans": len(self.loans),
            "active_loans": active_loans_count,
            "completed_loans": completed_loans_count,
            "on_time_rate": round(on_time_percentage, 1)
        }

    def to_dict(self):
        metrics = self.calculate_scoring_and_status()
        return {
            "id": self.id,
            "name": self.name,
            "whatsapp": self.whatsapp,
            "email": self.email or "",
            "address": self.address or "",
            "cuit": self.cuit or "",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "metrics": metrics,
            "documents": [d.to_dict() for d in self.documents]
        }


class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    rate_type = db.Column(db.String(20), default='mensual')
    modality = db.Column(db.String(30), default='mensual')
    installments_count = db.Column(db.Integer, nullable=False, default=1)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='activo')
    grace_days = db.Column(db.Integer, default=3)
    late_fee_type = db.Column(db.String(20), default='porcentaje')
    late_fee_value = db.Column(db.Float, default=1.0)
    notes = db.Column(db.Text, nullable=True)
    signature_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    installments = db.relationship('Installment', backref='loan', lazy=True, cascade="all, delete-orphan", order_by="Installment.number")
    payments = db.relationship('Payment', backref='loan', lazy=True, cascade="all, delete-orphan")
    documents = db.relationship('ClientDocument', backref='loan', lazy=True, cascade="all, delete-orphan")

    def generate_amortization_schedule(self):
        if self.rate_type == 'directo':
            total_interest = self.amount * (self.interest_rate / 100.0)
        else:
            months = self.installments_count
            if self.modality == 'semanal':
                months = self.installments_count / 4.0
            elif self.modality == 'quincenal':
                months = self.installments_count / 2.0
            elif self.modality == 'pago_unico':
                months = 1.0
            total_interest = self.amount * (self.interest_rate / 100.0) * max(0.25, months)

        total_to_pay = self.amount + total_interest
        installment_amount = round(total_to_pay / self.installments_count, 2)
        capital_per_inst = round(self.amount / self.installments_count, 2)
        interest_per_inst = round(total_interest / self.installments_count, 2)

        cur_date = self.start_date
        installments_list = []

        for i in range(1, self.installments_count + 1):
            if self.modality == 'semanal':
                cur_date = cur_date + timedelta(days=7)
            elif self.modality == 'quincenal':
                cur_date = cur_date + timedelta(days=15)
            elif self.modality == 'mensual':
                cur_date = cur_date + timedelta(days=30)
            elif self.modality == 'pago_unico':
                cur_date = cur_date + timedelta(days=30)
            else:
                cur_date = cur_date + timedelta(days=30)

            if i == self.installments_count:
                actual_capital = round(self.amount - (capital_per_inst * (self.installments_count - 1)), 2)
                actual_interest = round(total_interest - (interest_per_inst * (self.installments_count - 1)), 2)
                actual_amount = round(actual_capital + actual_interest, 2)
            else:
                actual_capital = capital_per_inst
                actual_interest = interest_per_inst
                actual_amount = installment_amount

            inst = Installment(
                loan_id=self.id,
                number=i,
                due_date=cur_date,
                amount=actual_amount,
                capital_portion=actual_capital,
                interest_portion=actual_interest,
                paid_amount=0.0,
                status='pendiente'
            )
            installments_list.append(inst)
        
        return installments_list

    def to_dict(self):
        total_paid = sum(i.paid_amount for i in self.installments)
        total_loan_amount = sum(i.amount for i in self.installments)
        remaining_balance = round(total_loan_amount - total_paid, 2)
        
        today = date.today()
        is_overdue = any(i.status != 'pagado' and i.due_date < today and (today - i.due_date).days > (self.grace_days or 0) for i in self.installments)
        all_paid = all(i.status == 'pagado' for i in self.installments) if self.installments else False
        
        calculated_status = 'completado' if all_paid else ('en_mora' if is_overdue else 'activo')

        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else "",
            "client_whatsapp": self.client.whatsapp if self.client else "",
            "amount": self.amount,
            "interest_rate": self.interest_rate,
            "rate_type": self.rate_type,
            "modality": self.modality,
            "installments_count": self.installments_count,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "status": calculated_status,
            "grace_days": self.grace_days,
            "late_fee_type": self.late_fee_type,
            "late_fee_value": self.late_fee_value,
            "notes": self.notes or "",
            "signature_data": self.signature_data or "",
            "total_loan_amount": round(total_loan_amount, 2),
            "total_paid": round(total_paid, 2),
            "documents": [d.to_dict() for d in self.documents],
            "remaining_balance": remaining_balance,
            "total_interest": round(sum(i.interest_portion for i in self.installments), 2),
            "installments": [i.to_dict() for i in self.installments]
        }


class Installment(db.Model):
    __tablename__ = 'installments'
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    capital_portion = db.Column(db.Float, nullable=False)
    interest_portion = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pendiente')
    paid_date = db.Column(db.Date, nullable=True)

    def calculate_late_fee(self):
        today = date.today()
        if self.status == 'pagado' or self.due_date >= today:
            return 0.0
        
        grace_days = self.loan.grace_days or 0
        overdue_days = (today - self.due_date).days - grace_days
        if overdue_days <= 0:
            return 0.0
        
        if self.loan.late_fee_type == 'monto_fijo':
            return round(overdue_days * self.loan.late_fee_value, 2)
        else:
            daily_rate = (self.loan.late_fee_value / 100.0)
            pending_principal = max(0.0, self.amount - self.paid_amount)
            return round(pending_principal * daily_rate * overdue_days, 2)

    def to_dict(self):
        today = date.today()
        late_fee = self.calculate_late_fee()
        grace_days = self.loan.grace_days or 0
        days_diff = (today - self.due_date).days

        current_status = self.status
        if self.status != 'pagado':
            if days_diff > grace_days:
                current_status = 'en_mora'
            elif self.paid_amount > 0:
                current_status = 'parcial'

        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "number": self.number,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "amount": round(self.amount, 2),
            "capital_portion": round(self.capital_portion, 2),
            "interest_portion": round(self.interest_portion, 2),
            "paid_amount": round(self.paid_amount, 2),
            "pending_amount": round(max(0.0, self.amount - self.paid_amount), 2),
            "late_fee": late_fee,
            "total_due": round(max(0.0, self.amount - self.paid_amount) + late_fee, 2),
            "status": current_status,
            "paid_date": self.paid_date.strftime("%Y-%m-%d") if self.paid_date else None,
            "client_name": self.loan.client.name if self.loan and self.loan.client else "",
            "client_whatsapp": self.loan.client.whatsapp if self.loan and self.loan.client else ""
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    installment_id = db.Column(db.Integer, db.ForeignKey('installments.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), default='Transferencia')
    notes = db.Column(db.String(255), nullable=True)
    receipt_number = db.Column(db.String(50), nullable=False)

    installment = db.relationship('Installment', backref='payments_rel', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "installment_id": self.installment_id,
            "loan_id": self.loan_id,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else "",
            "amount": round(self.amount, 2),
            "payment_date": self.payment_date.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method": self.payment_method,
            "notes": self.notes or "",
            "receipt_number": self.receipt_number,
            "installment_number": self.installment.number if self.installment else 1
        }


class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    is_ant_expense = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "amount": round(self.amount, 2),
            "date": self.date.strftime("%Y-%m-%d"),
            "is_ant_expense": self.is_ant_expense
        }


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    @classmethod
    def get_val(cls, key, default=""):
        row = cls.query.filter_by(key=key).first()
        return row.value if row and row.value is not None else default

    @classmethod
    def set_val(cls, key, value):
        row = cls.query.filter_by(key=key).first()
        if not row:
            row = cls(key=key, value=str(value))
            db.session.add(row)
        else:
            row.value = str(value)
        db.session.commit()


class ClientDocument(db.Model):
    __tablename__ = 'client_documents'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey('loans.id'), nullable=True)
    doc_type = db.Column(db.String(50), nullable=False) # 'dni_frente', 'dni_dorso', 'pagare_firmado', 'domicilio', 'otro'
    title = db.Column(db.String(150), nullable=False)
    image_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "loan_id": self.loan_id,
            "doc_type": self.doc_type,
            "title": self.title,
            "image_data": self.image_data,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M")
        }


class PersonalBill(db.Model):
    __tablename__ = 'personal_bills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='servicio') # 'tarjeta', 'servicio', 'fijo', 'variable', 'otro'
    owner = db.Column(db.String(50), nullable=False, default='Compartido') # 'Eduardo', 'Maira', 'Compartido'
    amount = db.Column(db.Float, nullable=False, default=0.0)
    due_day = db.Column(db.Integer, nullable=False, default=10) # Day of month (1-31)
    status = db.Column(db.String(20), nullable=False, default='pendiente') # 'pendiente', 'pagado'
    notes = db.Column(db.String(255), nullable=True)
    month = db.Column(db.Integer, nullable=False, default=9)
    year = db.Column(db.Integer, nullable=False, default=2026)
    installments_count = db.Column(db.Integer, nullable=False, default=1)
    current_installment = db.Column(db.Integer, nullable=False, default=1)
    is_recurring = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        today = date.today()
        b_year = self.year or today.year
        b_month = self.month or today.month
        try:
            import calendar
            max_days = calendar.monthrange(b_year, b_month)[1]
            actual_day = min(self.due_day, max_days)
            bill_due_date = date(b_year, b_month, actual_day)
            days_left = (bill_due_date - today).days
        except Exception:
            bill_due_date = today
            days_left = 0

        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "owner": self.owner,
            "amount": round(self.amount, 2),
            "due_day": self.due_day,
            "status": self.status,
            "notes": self.notes or "",
            "month": self.month,
            "year": self.year,
            "installments_count": self.installments_count or 1,
            "current_installment": self.current_installment or 1,
            "is_recurring": bool(self.is_recurring),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "next_due_date": bill_due_date.strftime("%Y-%m-%d"),
            "days_left": days_left
        }


class BiometricRequest(db.Model):
    __tablename__ = 'biometric_requests'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    installments_count = db.Column(db.Integer, nullable=False, default=1)
    interest_rate = db.Column(db.Float, nullable=False, default=15.0)
    rate_type = db.Column(db.String(20), default='mensual')
    modality = db.Column(db.String(30), default='mensual')
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='pendiente') # 'pendiente', 'firmado', 'otorgado', 'cancelado'
    signature_data = db.Column(db.Text, nullable=True)
    selfie_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    signed_at = db.Column(db.DateTime, nullable=True)

    @property
    def remaining_seconds(self):
        if not self.created_at:
            return 0
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return max(0, int(1800 - elapsed))

    @property
    def is_expired(self):
        return self.remaining_seconds <= 0

    def to_dict(self):
        return {
            "id": self.id,
            "token": self.token,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else "",
            "client_whatsapp": self.client.whatsapp if self.client else "",
            "amount": self.amount,
            "installments_count": self.installments_count,
            "interest_rate": self.interest_rate,
            "rate_type": self.rate_type,
            "modality": self.modality,
            "notes": self.notes or "",
            "status": self.status,
            "signature_data": self.signature_data or "",
            "selfie_data": self.selfie_data or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "signed_at": self.signed_at.strftime("%Y-%m-%d %H:%M:%S") if self.signed_at else None,
            "remaining_seconds": self.remaining_seconds,
            "is_expired": self.is_expired
        }


class Raffle(db.Model):
    __tablename__ = 'raffles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    motive = db.Column(db.String(255), nullable=True)
    mode = db.Column(db.String(30), default='numbers')
    number_min = db.Column(db.Integer, default=1)
    number_max = db.Column(db.Integer, default=100)
    ticket_price = db.Column(db.Float, default=0.0)
    prizes_json = db.Column(db.Text, nullable=True)
    participants_json = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='activo')
    winners_json = db.Column(db.Text, nullable=True)
    draw_date = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        prizes = json.loads(self.prizes_json) if self.prizes_json else []
        participants = json.loads(self.participants_json) if self.participants_json else []
        winners = json.loads(self.winners_json) if self.winners_json else []
        return {
            "id": self.id,
            "title": self.title,
            "motive": self.motive or "",
            "description": self.motive or "",
            "mode": self.mode,
            "number_min": self.number_min,
            "number_max": self.number_max,
            "range_min": self.number_min,
            "range_max": self.number_max,
            "ticket_price": self.ticket_price or 0.0,
            "prizes": prizes,
            "prizes_json": prizes,
            "participants": participants,
            "participants_json": participants,
            "status": self.status,
            "winners": winners,
            "winners_json": winners,
            "draw_date": self.draw_date or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else ""
        }


class ShoppingItem(db.Model):
    __tablename__ = 'shopping_items'
    id = db.Column(db.Integer, primary_key=True)
    store_category = db.Column(db.String(50), default='supermercado')
    item_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.String(50), default='1')
    is_checked = db.Column(db.Boolean, default=False)
    added_by = db.Column(db.String(50), default='Familia')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        cat_map = {
            'supermercado': 'Supermercado',
            'verduleria': 'Verdulería',
            'ferreteria': 'Ferretería',
            'farmacia': 'Farmacia'
        }
        display_cat = cat_map.get(self.store_category.lower(), self.store_category.capitalize())
        return {
            "id": self.id,
            "store_category": self.store_category,
            "category": display_cat,
            "item_name": self.item_name,
            "name": self.item_name,
            "quantity": self.quantity or "1",
            "is_checked": bool(self.is_checked),
            "is_bought": bool(self.is_checked),
            "added_by": self.added_by or "Familia",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else ""
        }


class NoticeBoardItem(db.Model):
    __tablename__ = 'notice_board_items'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(50), default='Familia')
    message = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author or "Familia",
            "title": self.author or "Familia",
            "message": self.message,
            "content": self.message,
            "color": "yellow",
            "is_pinned": bool(self.is_pinned),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else ""
        }


class HomeCalendarItem(db.Model):
    __tablename__ = 'home_calendar_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), default='servicio')
    due_date = db.Column(db.String(20), nullable=False)
    due_time = db.Column(db.String(10), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "due_date": self.due_date,
            "event_date": self.due_date,
            "due_time": self.due_time or "",
            "notes": self.notes or "",
            "is_completed": bool(self.is_completed),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else ""
        }





