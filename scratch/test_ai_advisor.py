import os
import re
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def _generar_respuesta_local_asesor(prompt: str, context_data: dict = None) -> str:
    lines = ["📊 **Dictamen de Auditoría Crediticia & Asistente Financiero IA**\n"]
    
    if context_data and "bcra_report" in context_data and context_data["bcra_report"]:
        bcra = context_data["bcra_report"]
        lines.append(f"👤 **Cliente / Titular Auditado**: {bcra.get('denominacion')}")
        lines.append(f"🪪 **CUIT / CUIL**: {bcra.get('cuit')}")
        lines.append(f"🏛️ **Peor Situación BCRA**: Situación {bcra.get('max_situacion')} ({bcra.get('situacion_label')})")
        lines.append(f"💰 **Deuda Bancaria Total Registrada**: ${bcra.get('total_deuda_pesos', 0):,.2f}")
        lines.append(f"⚠️ **Cheques Rechazados**: {bcra.get('cheques_rechazados', 0)}")
        lines.append(f"\n📋 **Bancos & Entidades Financieras Registradas**:")
        
        entidades = bcra.get("entidades") or []
        if entidades:
            for ent in entidades[:8]:
                m_pesos = ent.get("monto_pesos") or ent.get("monto") or 0
                lines.append(f"  • **{ent.get('entidad')}**: ${m_pesos:,.2f} | Sit. {ent.get('situacion')} | Atraso: {ent.get('diasAtraso', 0)} días ({ent.get('estado_texto', '')})")
        else:
            lines.append("  • *Sin deudas pendientes en el sistema bancario (Situación 1 Normal).*")
            
        lines.append(f"\n🚦 **Evaluación del Motor de Crédito**:\n{bcra.get('underwriting', {}).get('message')}")
        
    elif context_data and "financial_metrics" in context_data:
        fm = context_data["financial_metrics"]
        lines.append("📈 **Resumen de Salud Financiera de la Empresa**:")
        lines.append(f"  • Capital en calle: ${fm.get('capital_en_calle', 0):,.2f}")
        lines.append(f"  • Cobros del mes: ${fm.get('cobros_mes', 0):,.2f}")
        lines.append(f"  • Gastos del mes: ${fm.get('gastos_mes', 0):,.2f}")
        lines.append(f"  • Ganancia líquida neta: ${fm.get('net_liquid', 0):,.2f}")
        lines.append(f"  • Préstamos activos auditados: {fm.get('active_loans_count', 0)}")
    else:
        lines.append("He procesado tu consulta contable. Podés indicarme el nombre o CUIT de un cliente para evaluar su BCRA y capacidad de crédito.")
        
    return "\n".join(lines)

def chat_ia_asesor_contador(prompt: str, rol: str = "asesor", context_data: dict = None) -> str:
    if not client:
        return _generar_respuesta_local_asesor(prompt, context_data)

    context_str = ""
    if context_data:
        context_str += "\n--- DATOS EN TIEMPO REAL DEL SISTEMA ---\n"
        if "financial_metrics" in context_data:
            fm = context_data["financial_metrics"]
            context_str += f"• Capital en calle: ${fm.get('capital_en_calle', 0):,.2f}\n"
            context_str += f"• Cobros del mes: ${fm.get('cobros_mes', 0):,.2f}\n"
            context_str += f"• Gastos del mes: ${fm.get('gastos_mes', 0):,.2f}\n"
            context_str += f"• Ganancia neta líquida: ${fm.get('net_liquid', 0):,.2f}\n"
            context_str += f"• Préstamos activos: {fm.get('active_loans_count', 0)}\n"
        
        if "clients_summary" in context_data:
            context_str += "\n--- REGISTRO DE CLIENTES DEL SISTEMA ---\n"
            for c in context_data["clients_summary"]:
                context_str += f"• Cliente: {c.get('name')} | CUIT: {c.get('cuit') or 'N/A'} | Scoring: {c.get('scoring_stars')}★ | Préstamos Activos: {c.get('active_loans_count')} | Saldo Pendiente: ${c.get('remaining_balance', 0):,.2f} | Cuotas Vencidas: {c.get('overdue_count', 0)}\n"

        if "bcra_report" in context_data and context_data["bcra_report"]:
            bcra = context_data["bcra_report"]
            context_str += "\n--- INFORME OFICIAL BCRA (CENTRAL DE DEUDORES) ---\n"
            context_str += f"• Titular / Denominación: {bcra.get('denominacion')}\n"
            context_str += f"• CUIT/CUIL: {bcra.get('cuit')}\n"
            context_str += f"• Peor Situación Registrada: Situación {bcra.get('max_situacion')} ({bcra.get('situacion_label')})\n"
            context_str += f"• Deuda Bancaria Total en Pesos: ${bcra.get('total_deuda_pesos', 0):,.2f}\n"
            context_str += f"• Cheques Rechazados: {bcra.get('cheques_rechazados', 0)}\n"
            context_str += f"• Dictamen Motor de Crédito: {bcra.get('underwriting', {}).get('message')}\n"
            
            entidades = bcra.get("entidades") or []
            if entidades:
                context_str += "• Entidades Financieras / Bancos Registrados:\n"
                for ent in entidades:
                    m_pesos = ent.get("monto_pesos") or ent.get("monto") or 0
                    context_str += f"   - {ent.get('entidad')}: Deuda ${m_pesos:,.2f} | Sit. {ent.get('situacion')} | {ent.get('diasAtraso', 0)} días atraso ({ent.get('estado_texto', '')})\n"

    system_instruction = (
        "Sos el Contador Virtual IA & Auditor Crediticio Senior de la empresa de préstamos.\n"
        "Tenés conocimiento total del negocio, del flujo de caja, de cada cliente registrado y de la Central de Deudores del BCRA.\n"
        "Cuando el usuario te consulte si se le puede prestar cierta cantidad de dinero a una persona o cliente:\n"
        "1. Analizá su historial crediticio BCRA (Situación 1 a 6, deudas bancarias en pesos, bancos donde opera, días de atraso, cheques rechazados).\n"
        "2. Analizá su historial interno con la empresa (scoring, deudas vigentes, comportamiento de pago).\n"
        "3. Dictaminá con claridad si APROBAS, OBSERVÁS o RECHAZÁS la solicitud de préstamo.\n"
        "4. Indicá el monto máximo seguro recomendable a prestar, la cuota sugerida y si requiere exigir un garante o recibo de sueldo verificado.\n"
        "Respondé siempre de manera profesional, ejecutiva, estructurada con viñetas y emojis, usando valores formateados en pesos argentinos ($ ARS)."
    )

    full_prompt = prompt
    if context_str:
        full_prompt = f"{prompt}\n\n{context_str}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
        )
        return response.text
    except Exception as e:
        print(f"[Gemini AI Chat Exception]: {e}")
        return _generar_respuesta_local_asesor(prompt, context_data)

if __name__ == '__main__':
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sample_bcra = {
        "cuit": "30500010912",
        "denominacion": "BANCO DE LA NACION ARGENTINA",
        "max_situacion": 1,
        "situacion_label": "Situación 1: Normal",
        "total_deuda_pesos": 325328816000.0,
        "cheques_rechazados": 0,
        "underwriting": {
            "status": "APROBADO_NORMAL",
            "traffic_light": "verde",
            "message": "✅ MOTOR DE DECISIONES: Cliente Aprobado. Comportamiento normal en BCRA."
        },
        "entidades": [
            {"entidad": "BANCO GALICIA Y BUENOS AIRES S.A.", "monto_pesos": 28405173000.0, "situacion": 1, "diasAtraso": 0, "estado_texto": "Al día"},
            {"entidad": "BANCO SANTANDER ARGENTINA S.A.", "monto_pesos": 42863168000.0, "situacion": 1, "diasAtraso": 0, "estado_texto": "Al día"}
        ]
    }

    context = {
        "financial_metrics": {"capital_en_calle": 975000.0, "cobros_mes": 48750.0, "gastos_mes": 15000.0, "net_liquid": 33750.0, "active_loans_count": 5},
        "bcra_report": sample_bcra
    }

    res = chat_ia_asesor_contador("¿Le puedo prestar $500.000 a este cliente en 6 cuotas?", rol="asesor", context_data=context)
    print("RESPUESTA ASESOR / CONTADOR IA:")
    print(res)
