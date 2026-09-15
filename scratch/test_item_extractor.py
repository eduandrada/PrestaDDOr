import re
from datetime import datetime, timedelta

def process_zero_ui_text_advanced(raw_text: str, source: str = "Voz/Zero-UI") -> dict:
    raw_text = (raw_text or '').strip()
    if not raw_text:
        return {"success": False, "status": "error", "error": "No se recibió texto o audio para procesar."}

    # 1. Clean repetitive text & speech artifacts
    text = re.sub(r'\b(\w+)(?:\s+\1)+\b', r'\1', raw_text, flags=re.IGNORECASE)
    text = re.sub(r'(?i)\bhola\b|\bcómo estás\b|\bcomo estas\b|\bquisiera\b|\bpor favor\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    created_items = {"shopping": [], "calendar": [], "notices": []}

    # 2. Known category mapping
    categories_kw = {
        'verduleria': ['lechuga', 'tomate', 'tomates', 'papa', 'papas', 'cebolla', 'zanahoria', 'manzana', 'banana', 'fruta', 'verdura'],
        'ferreteria': ['clavo', 'clavos', 'tornillo', 'cinta', 'cable', 'pintura', 'martillo', 'lira', 'foco'],
        'farmacia': ['remedio', 'remedios', 'aspirina', 'paracetamol', 'ibuprofeno', 'gasas', 'alcohol', 'farmacia'],
        'supermercado': ['detergente', 'leche', 'pan', 'carne', 'aceite', 'jabon', 'fideos', 'harina', 'arroz', 'queso', 'fiambre']
    }

    calendar_kw = ['turno', 'dentista', 'medico', 'médico', 'examen', 'pagar', 'factura', 'vencimiento', 'cita', 'reunion', 'reunión']
    notice_kw = ['recordar', 'nota', 'aviso', 'importante', 'ojo']

    # 3. Match quantity patterns: "2 kg de tomate", "500 gr de carne", "1 litro de leche", "3 paquetes de fideos"
    qty_pattern = r'(\d+(?:\.\d+)?\s*(?:kg|kilos|kilo|gr|gramos|g|l|litros|litro|paquetes|paquete|unidades|un)?)\s+(?:de\s+)?([a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+)'

    # Split text into action clauses and item candidates
    clean_speech = re.sub(r'(?i)\bhola\b|\bcómo estás\b|\bcomo estas\b|\bnecesito\b|\bquisiera\b|\bpor favor\b', ' ', raw_text)
    clean_speech = re.sub(r'\b(\w+)(?:\s+\1)+\b', r'\1', clean_speech, flags=re.IGNORECASE)
    clean_speech = re.sub(r'\s+', ' ', clean_speech).strip()

    clauses = re.split(r'[\.\n;]|(?:\b(?:y|también|tamien|además)\b)', clean_speech, flags=re.IGNORECASE)
    
    seen_shopping = set()
    seen_calendar = set()
    seen_notices = set()

    for clause in clauses:
        clause_str = clause.strip()
        if not clause_str or len(clause_str) < 3:
            continue
            
        c_lower = clause_str.lower()
        
        # Check calendar
        if any(k in c_lower for k in calendar_kw):
            clean_title = re.sub(r'^(?:necesito|tengo que|hay que|recordar|hacer)\s+', '', clause_str, flags=re.IGNORECASE).capitalize()
            if clean_title not in seen_calendar:
                seen_calendar.add(clean_title)
                cat = 'servicio'
                if any(k in c_lower for k in ['dentista', 'medico', 'médico', 'doctor']):
                    cat = 'medico'
                elif any(k in c_lower for k in ['vacuna', 'perro', 'gato', 'mascota']):
                    cat = 'mascota'
                
                created_items["calendar"].append({
                    "title": clean_title,
                    "category": cat,
                    "due_date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    "due_time": "17:00",
                    "notes": f"Agendado desde {source}"
                })
            continue

        # Check noticeboard
        if any(k in c_lower for k in notice_kw) and not any(k in c_lower for k in ['comprar', 'tomate', 'lechuga', 'carne']):
            clean_content = clause_str.capitalize()
            if clean_content not in seen_notices:
                seen_notices.add(clean_content)
                created_items["notices"].append({
                    "author": source,
                    "message": clean_content,
                    "content": clean_content,
                    "is_pinned": False
                })
            continue

        # Extract items - match quantity patterns
        qty_matches = re.findall(qty_pattern, clause_str, flags=re.IGNORECASE)
        if qty_matches:
            for qty, prod_raw in qty_matches:
                prod = prod_raw.strip().capitalize()
                prod = re.sub(r'^(?:comprar|necesito|compras|traer)\s+', '', prod, flags=re.IGNORECASE).strip()
                # Split multiple words if concatenated without punctuation
                prod_tokens = prod.split()
                if prod_tokens:
                    target_prod = prod_tokens[-1].capitalize() if len(prod_tokens) > 1 and prod_tokens[0].lower() in ['comprar', 'lechuga', 'tomate'] else prod
                    if target_prod and target_prod.lower() not in ['de', 'y', 'para', 'que'] and len(target_prod) > 2:
                        if target_prod.lower() not in seen_shopping:
                            seen_shopping.add(target_prod.lower())
                            cat = 'supermercado'
                            for c_name, keywords in categories_kw.items():
                                if any(k in target_prod.lower() for k in keywords):
                                    cat = c_name
                                    break
                            created_items["shopping"].append({
                                "store_category": cat,
                                "item_name": f"{target_prod} ({qty.strip()})" if qty.strip() != '1' else target_prod,
                                "name": f"{target_prod} ({qty.strip()})" if qty.strip() != '1' else target_prod,
                                "quantity": qty.strip(),
                                "added_by": source
                            })

        # Also check direct product keywords in clause (e.g. lechuga, tomate)
        for cat_name, kw_list in categories_kw.items():
            for kw in kw_list:
                if kw in c_lower and kw not in seen_shopping:
                    seen_shopping.add(kw)
                    display_name = kw.capitalize()
                    created_items["shopping"].append({
                        "store_category": cat_name,
                        "item_name": display_name,
                        "name": display_name,
                        "quantity": "1",
                        "added_by": source
                    })

    # Filter out partial word entries if a longer word starting with the same prefix exists in shopping list
    final_shopping = []
    for s_item in created_items["shopping"]:
        name_lower = re.sub(r'\s*\([^)]*\)', '', s_item["name"]).strip().lower()
        is_sub_prefix = False
        for other_item in created_items["shopping"]:
            other_name = re.sub(r'\s*\([^)]*\)', '', other_item["name"]).strip().lower()
            if len(other_name) > len(name_lower) and other_name.startswith(name_lower):
                is_sub_prefix = True
                break
        if not is_sub_prefix:
            final_shopping.append(s_item)

    created_items["shopping"] = final_shopping

    return {
        "status": "success",
        "success": True,
        "raw_text": raw_text,
        "summary": f"Se procesó el dictado: {len(created_items['shopping'])} compras, {len(created_items['calendar'])} turnos y {len(created_items['notices'])} avisos.",
        "created_items": created_items,
        "result": {
            "shopping": [i["name"] for i in created_items["shopping"]],
            "calendar": [i["title"] for i in created_items["calendar"]],
            "notices": [i["content"] for i in created_items["notices"]]
        }
    }

# Test with user prompt
test_input = """Hola Hola Hola cómo Hola cómo estás Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar lec Hola Cómo estás Necesito comprar lechu Hola Cómo estás Necesito comprar lechuga Hola Cómo estás Necesito comprar lechuga toma Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate  2  2 kg  2 kg de  2 kg de toma  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate"""

res = process_zero_ui_text_advanced(test_input)
print("RESULTADO DEL PROCESADOR AVANZADO:")
print(res["summary"])
print("COMPRAS DETECTADAS:")
for item in res["created_items"]["shopping"]:
    print("  -", item)
