import os
import json
from datetime import datetime, date

def backup_db_to_json(app, db, models_dict, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, 'database_auto_backup.json')
    
    with app.app_context():
        data = {}
        for name, model in models_dict.items():
            records = model.query.all()
            model_data = []
            for r in records:
                row = {}
                for col in r.__table__.columns:
                    val = getattr(r, col.name)
                    if isinstance(val, (datetime, date)):
                        val = val.isoformat()
                    row[col.name] = val
                model_data.append(row)
            data[name] = model_data
            
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return backup_file

print("Backup logic test script ready.")
