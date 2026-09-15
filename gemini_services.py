import os
import base64
from io import BytesIO
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def _generar_respuesta_local_asesor(prompt: str, context_data: dict = None) -> str:
    """Generador local inteligente de dictámenes de auditoría crediticia y contable cuando no hay API Key o falla el servicio."""
    import re
    lines = ["📊 **Dictamen de Auditoría Crediticia & Asistente Financiero IA**\n"]
    
    # Extraer si el usuario pregunta por un monto específico
    monto_match = re.search(r'\$?\s*(\d{1,3}(?:\.\d{3})*|\d+)', prompt)
    monto_solicitado = None
    if monto_match:
        try:
            m_str = monto_match.group(1).replace('.', '')
            val = float(m_str)
            if val >= 5000:
                monto_solicitado = val
        except Exception:
            pass

    ci = context_data.get("client_info") if context_data else None
    bcra = context_data.get("bcra_report") if context_data else None

    # Información de Cliente Interno
    if ci:
        lines.append(f"👤 **Cliente Auditado**: {ci.get('name')}")
        lines.append(f"🪪 **CUIT / CUIL**: {ci.get('cuit') or 'N/A'}")
        lines.append(f"💳 **Alias Bancario**: {ci.get('bank_alias') or 'No registrado'}")
        lines.append(f"⭐ **Scoring Interno**: {ci.get('scoring_stars', 5)} Estrellas")
        lines.append(f"📋 **Préstamos Activos Internos**: {ci.get('active_loans_count', 0)} (Saldo Pendiente: ${ci.get('remaining_balance', 0):,.2f})")
        lines.append(f"⚠️ **Cuotas Vencidas Internas**: {ci.get('overdue_count', 0)}")
        
        loans_det = ci.get("active_loans_details") or []
        if loans_det:
            lines.append("  *Detalle de Préstamos Internos:*")
            for ld in loans_det:
                lines.append(f"    • Préstamo #{ld.get('id')} - Monto: ${ld.get('amount', 0):,.2f} | Saldo: ${ld.get('remaining_balance', 0):,.2f} | Otorgado por: {ld.get('created_by', 'Administración')}")
        lines.append("")

    elif bcra:
        lines.append(f"👤 **Cliente Auditado**: {bcra.get('denominacion') or 'Cliente registrado en Sistema BCRA'}")
        lines.append(f"🪪 **CUIT / CUIL**: {bcra.get('cuit') or 'N/A'}")

    # Información BCRA
    if bcra:
        max_sit = bcra.get('max_situacion', 1)
        tot_deuda = bcra.get('total_deuda_pesos', 0.0)
        ch_rech = bcra.get('cheques_rechazados', 0)
        entidades = bcra.get("entidades") or []
        underwriting = bcra.get("underwriting") or {}

        lines.append(f"🏛️ **Situación Central de Deudores BCRA**: Situación {max_sit} ({bcra.get('situacion_label', 'Sin mora')})")
        lines.append(f"💰 **Deuda Bancaria Total en Sistema**: ${tot_deuda:,.2f}")
        lines.append(f"⚠️ **Cheques Rechazados Registrados**: {ch_rech}")
        
        lines.append(f"\n📋 **Detalle por Entidad Financiera ({len(entidades)} registradas)**:")
        if entidades:
            for ent in entidades[:8]:
                m_pesos = ent.get("monto_pesos") or ent.get("monto") or 0.0
                sit = ent.get("situacion", 1)
                dias = ent.get("diasAtraso") or ent.get("dias_atraso") or 0
                lines.append(f"  • **{ent.get('entidad')}**: ${m_pesos:,.2f} | Sit. {sit} | Atraso: {dias} días ({ent.get('estado_texto', '')})")
        else:
            lines.append("  • *Sin deudas registradas en entidades financieras (Situación 1 Normal al día).*")

        lines.append(f"\n🚦 **Evaluación del Motor de Decisiones BCRA**:\n{underwriting.get('message', 'Perfil evaluado correctamente.')}")

        if monto_solicitado:
            lines.append(f"\n💡 **Asesoramiento de Préstamo para ${monto_solicitado:,.2f}**:")
            if max_sit >= 3 or ch_rech > 0:
                lines.append(f"🔴 **DICTAMEN: RECHAZADO**. El cliente presenta Situación BCRA {max_sit} o cheques rechazados. No se recomienda otorgar los ${monto_solicitado:,.2f} por alto riesgo de insolvencia.")
            elif max_sit == 2:
                monto_aprobado = monto_solicitado * 0.5
                lines.append(f"🟡 **DICTAMEN: OBSERVADO CON CONDICIONES**. Debido a atrasos leves en bancos (Situación 2), se sugiere limitar el cupo a ${monto_aprobado:,.2f} exigiendo un Garante Solvente con recibo de sueldo verificado.")
            else:
                lines.append(f"🟢 **DICTAMEN: APROBADO**. Excelente historial crediticio al día (Situación 1). Se aprueba el préstamo de ${monto_solicitado:,.2f} en 6 o 12 cuotas fijas.")

    elif not ci and context_data and "financial_metrics" in context_data:
        fm = context_data["financial_metrics"]
        lines.append("📈 **Resumen General de Cartera & Arqueo de Caja**:")
        lines.append(f"  • Capital Total en Calle: ${fm.get('capital_en_calle', 0):,.2f}")
        lines.append(f"  • Cobros del Mes: ${fm.get('cobros_mes', 0):,.2f}")
        lines.append(f"  • Gastos del Mes: ${fm.get('gastos_mes', 0):,.2f} (Hormiga: ${fm.get('ant_expenses', 0):,.2f})")
        lines.append(f"  • Ganancia Líquida Neta: ${fm.get('net_liquid', 0):,.2f}")
        lines.append(f"  • Préstamos Activos: {fm.get('active_loans_count', 0)}")

        cal_sum = context_data.get("calendar_summary") or []
        if cal_sum or any(k in prompt.lower() for k in ['calendario', 'vencimiento', 'agenda', 'recordatorio', 'servicio']):
            if cal_sum:
                lines.append("\n📅 **Agenda del Asesor IA & Vencimientos Próximos**:")
                for citem in cal_sum:
                    lines.append(f"  • [{citem.get('category', 'SERVICIO').upper()}] **{citem.get('title')}** - Vence: {citem.get('due_date')} {citem.get('due_time') or ''}")

        lines.append("\n💡 *Podés ingresar el nombre o CUIT de cualquier cliente para auditar su BCRA y evaluar préstamos.*")
    elif not ci and not bcra:
        lines.append("Bienvenido al Asesor Financiero & Contador IA. Podés ingresar el nombre o CUIT de un cliente para evaluar su historial crediticio BCRA y pedir recomendaciones sobre el otorgamiento de un préstamo.")

    return "\n".join(lines)


def chat_ia_asesor_contador(prompt: str, rol: str = "asesor", context_data: dict = None) -> str:
    """Atiende al Contador Virtual IA & Asesor Financiero inyectando contexto de Clientes y BCRA."""
    if not client:
        return _generar_respuesta_local_asesor(prompt, context_data)

    context_str = ""
    if context_data:
        context_str += "\n--- CONTEXTO Y DATOS DEL SISTEMA EN TIEMPO REAL ---\n"
        
        if "financial_metrics" in context_data:
            fm = context_data["financial_metrics"]
            context_str += f"• Capital en calle: ${fm.get('capital_en_calle', 0):,.2f}\n"
            context_str += f"• Cobros del mes: ${fm.get('cobros_mes', 0):,.2f}\n"
            context_str += f"• Gastos del mes: ${fm.get('gastos_mes', 0):,.2f}\n"
            context_str += f"• Ganancia neta líquida: ${fm.get('net_liquid', 0):,.2f}\n"
            context_str += f"• Préstamos activos en cartera: {fm.get('active_loans_count', 0)}\n"

        if "client_info" in context_data and context_data["client_info"]:
            ci = context_data["client_info"]
            context_str += "\n--- INFORMACIÓN INTERNA DEL CLIENTE CONSULTADO ---\n"
            context_str += f"• Nombre: {ci.get('name')}\n"
            context_str += f"• CUIT: {ci.get('cuit') or 'N/A'}\n"
            context_str += f"• Scoring Interno: {ci.get('scoring_stars', 5)}★\n"
            context_str += f"• Préstamos Activos Internos: {ci.get('active_loans_count', 0)}\n"
            context_str += f"• Saldo Pendiente Interno: ${ci.get('remaining_balance', 0):,.2f}\n"
            context_str += f"• Cuotas Vencidas Internas: {ci.get('overdue_count', 0)}\n"

            loans_det = ci.get("active_loans_details") or []
            if loans_det:
                context_str += "• Detalle de Préstamos Internos:\n"
                for ld in loans_det:
                    context_str += f"   - Préstamo #{ld.get('id')} | Monto: ${ld.get('amount', 0):,.2f} | Saldo: ${ld.get('remaining_balance', 0):,.2f} | Otorgado por: {ld.get('created_by', 'Administración')}\n"

        if "clients_summary" in context_data:
            context_str += "\n--- RESUMEN DE OTROS CLIENTES REGISTRADOS ---\n"
            for c in context_data["clients_summary"][:15]:
                context_str += f"• Cliente: {c.get('name')} | CUIT: {c.get('cuit') or 'N/A'} | Scoring: {c.get('scoring_stars')}★ | Préstamos Activos: {c.get('active_loans_count')} | Saldo Pendiente: ${c.get('remaining_balance', 0):,.2f} | Cuotas Vencidas: {c.get('overdue_count', 0)}\n"

        if "bcra_report" in context_data and context_data["bcra_report"]:
            bcra = context_data["bcra_report"]
            context_str += "\n--- INFORME OFICIAL BCRA (CENTRAL DE DEUDORES BANCO CENTRAL) ---\n"
            context_str += f"• Titular / Denominación: {bcra.get('denominacion')}\n"
            context_str += f"• CUIT/CUIL Auditado: {bcra.get('cuit')}\n"
            context_str += f"• Peor Situación Registrada: Situación {bcra.get('max_situacion')} ({bcra.get('situacion_label')})\n"
            context_str += f"• Deuda Bancaria Total en Pesos: ${bcra.get('total_deuda_pesos', 0):,.2f}\n"
            context_str += f"• Cheques Rechazados Registrados: {bcra.get('cheques_rechazados', 0)}\n"
            context_str += f"• Dictamen Motor de Crédito: {bcra.get('underwriting', {}).get('message')}\n"
            
            entidades = bcra.get("entidades") or []
            if entidades:
                context_str += "• Entidades Financieras / Bancos Registrados:\n"
                for ent in entidades:
                    m_pesos = ent.get("monto_pesos") or ent.get("monto") or 0.0
                    context_str += f"   - {ent.get('entidad')}: Deuda ${m_pesos:,.2f} | Sit. {ent.get('situacion')} | {ent.get('diasAtraso', 0)} días atraso ({ent.get('estado_texto', '')})\n"

    system_instruction = (
        "Sos el Contador Virtual IA & Auditor Crediticio de elite del Sistema de Gestión de Préstamos.\n"
        "Tenés acceso total a la información de clientes, historial de préstamos, cobranzas y a la Central de Deudores del Banco Central (BCRA).\n"
        "Cuando el usuario consulte si se le puede otorgar o prestar determinado dinero a un cliente o persona:\n"
        "1. Analizá el Historial BCRA: Situación 1 a 6, deuda bancaria acumulada en pesos, bancos donde registra deuda, días de atraso y cheques rechazados.\n"
        "2. Analizá el Historial Interno: Scoring del cliente, cuotas activas/vencidas en la empresa, cumplimiento de pagos y quién otorgó los préstamos.\n"
        "3. Emití un Dictamen Claro de Evaluación Crediticia: 🟢 APROBADO, 🟡 OBSERVADO CON CONDICIONES o 🔴 RECHAZADO.\n"
        "4. Asesorá sobre el monto aconsejable a prestar, cuota mensual estimada, tasa de interés y si requiere solicitar garante o recibo de sueldo.\n"
        "Formateá la respuesta de manera ejecutiva, muy clara, utilizando viñetas, emojis conceptuales (🏛️ 📊 🟢 🟡 🔴 💳 💡 👤 ⚠️) y valores en Pesos Argentinos ($ ARS)."
    )

    full_prompt = prompt
    if context_str:
        full_prompt = f"{prompt}\n\n{context_str}"

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
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


def chat_ia(prompt: str, rol: str = "asesor") -> str:
    """Atiende al Asesor IA y al Contador IA según el rol."""
    return chat_ia_asesor_contador(prompt, rol=rol)


def generar_cv_ia(datos_usuario: str) -> str:
    """Genera un CV profesional formateado en Markdown / HTML para el Convertidor Universal."""
    if not client:
        return "Error: Falta GEMINI_API_KEY"

    prompt = f"""Con los siguientes datos, redactá un Curriculum Vitae profesional, optimizado y moderno:
    {datos_usuario}
    Formatealo de manera limpia en Markdown (o secciones estructuradas listas para imprimir)."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error al redactar CV con IA: {str(e)}"

def generar_imagen_sorteo(descripcion_premio: str) -> str:
    """Genera un banner/flyer publicitario del sorteo y devuelve la imagen en Base64."""
    if not client:
        return None

    prompt = f"Flyer promocional vibrante para sorteo de rifa o bingo: {descripcion_premio}. Estilo publicitario profesional, colores llamativos, render 3D hiperrealista, composición centrada."
    
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="1:1"
            )
        )
        
        for img in result.generated_images:
            return base64.b64encode(img.image.image_bytes).decode("utf-8")
    except Exception as e:
        print(f"Error generando imagen de sorteo con Imagen 3: {e}")
        
    return None

def escaneo_camscanner_ia(imagen_bytes: bytes, formato_salida: str = "docx") -> str:
    """Procesa una imagen de recibo/pagaré con Gemini 2.5 Vision para extraer texto y estructura."""
    if not client:
        return "Error: Clave de Gemini API no configurada."

    prompt = f"""Sos un escáner OCR profesional CamScanner de alta precisión.
Analizá minuciosamente esta imagen (pagaré, recibo, factura o documento).
Extraé y transcribí todo el texto, importes en pesos/dólares, fechas, nombres de clientes/firmantes y detalles.
Formatealo de manera limpia y estructurada para exportar a {formato_salida.upper()}."""

    try:
        image_part = types.Part.from_bytes(
            data=imagen_bytes,
            mime_type="image/jpeg"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, prompt]
        )
        return response.text
    except Exception as e:
        return f"Error en escaneo OCR con Gemini IA: {str(e)}"

