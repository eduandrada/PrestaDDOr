from app import app
from models import db, PersonalBill

with app.app_context():
    bills = PersonalBill.query.all()
    print(f"Total PersonalBills in DB: {len(bills)}")
    for b in bills:
        print(f"ID: {b.id} | Name: '{b.name}' | Month: {b.month}/{b.year} | Amount: {b.amount} | Recurring: {b.is_recurring} | Status: {b.status}")
