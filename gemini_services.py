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
    """Generador local inteligente de dictámenes de auditoría crediticia, contable y guía operativa completa del sistema."""
    import re
    p_lower = (prompt or "").lower()

    # Detección de consultas sobre CÓMO USAR o PARA QUÉ SIRVEN las funciones del sistema
    is_app_guide_query = any(k in p_lower for k in [
        'como usar', 'cómo usar', 'para que sirve', 'para qué sirve', 'como funciona', 'cómo funciona',
        'como hago', 'cómo hago', 'como creo', 'cómo creo', 'explicame', 'explícame', 'donde veo', 'dónde veo',
        'paso a paso', 'manual', 'tutorial', 'guia', 'guía', 'que es', 'qué es', 'para que es', 'para qué es',
        'funciones', 'modulos', 'módulos', 'opciones'
    ])

    # 1. Guías Operativas de Funciones del Sistema (cuando no es una consulta directa de datos de agenda o cliente)
    if (is_app_guide_query or any(k in p_lower for k in ['pagare', 'pagaré', 'qr', 'bcra', 'veraz', 'garante', 'scoring', 'hormiga', 'calle', 'recibo', 'camscanner', 'bingo', 'cv', 'caja', 'compras'])) and not (context_data and context_data.get('calendar_summary') and any(ck in p_lower for ck in ['calendario', 'vencimiento', 'agenda'])):
        if 'bcra' in p_lower or 'veraz' in p_lower or 'deudores' in p_lower or 'evaluacion' in p_lower or 'evaluación' in p_lower:
            return (
                "🏛️ **Evaluación Crediticia & Central de Deudores BCRA**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Permite auditar el veraz oficial del Banco Central de la República Argentina en tiempo real por CUIT/CUIL/DNI, conociendo si el cliente tiene deudas con bancos o tarjetas, días de atraso y cheques rechazados.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a la pestaña **'Evaluación Crediticia & Historial de Deudores BCRA'**.\n"
                "2. Ingresar el CUIT (11 dígitos) o DNI del cliente y presionar **'Consultar BCRA'**.\n"
                "3. Verás el veredicto del Motor de Decisiones (🟢 Aprobado, 🟡 Observado con Garante, 🔴 Rechazado) y la lista de todos los bancos con deudas exactas en ARS, situaciones 1 al 6 y días sin pagar.\n"
                "4. **Notificación por WhatsApp**: Presioná el botón **'📲 Notificar Resolución por WhatsApp'** para enviar automáticamente al cliente el dictamen formal (aprobado o rechazado por mora BCRA).\n"
                "5. **PDF Oficial**: Presioná **'📄 Descargar Informe BCRA en PDF'** para imprimir un documento completo de auditoría crediticia.\n\n"
                "💡 *Tip:* También podés consultarlo directamente desde la ficha de cada cliente o escribiendo su CUIT en este chat."
            )
        elif 'qr' in p_lower or 'pagare' in p_lower or 'pagaré' in p_lower or 'biometrico' in p_lower or 'biométrico' in p_lower:
            return (
                "📱 **Pagaré Express QR & Firma Biométrica**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Permite emitir y hacer firmar pagarés y contratos de préstamo a distancia de forma rápida y legal, capturando la firma digital táctil, foto del DNI, IP y geolocalización GPS del cliente.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. En el menú superior o en la pestaña **'Préstamos'**, seleccionar **'Pagaré Express QR'**.\n"
                "2. Completar los datos de la solicitud (Cliente, Monto, Cuotas) y generar el código QR o enlace directo.\n"
                "3. Compartir el enlace o mostrar el QR al cliente para que lo escanee desde su celular.\n"
                "4. El cliente firma en la pantalla de su teléfono y adjunta foto del DNI.\n"
                "5. El enlace expira automáticamente según el tiempo configurado en Ajustes (ej. 30 minutos) por seguridad.\n\n"
                "💡 *Tip:* En el historial del cliente podés ver y descargar los pagarés firmados en PDF."
            )
        elif 'cobro' in p_lower or 'cuotas' in p_lower or 'recibo' in p_lower or 'whatsapp' in p_lower:
            return (
                "💰 **Gestión de Cobranzas, Recibos PDF & Avisos por WhatsApp**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Permite llevar el control estricto de las cuotas a vencer, cuotas al día y cuotas en mora, emitiendo comprobantes oficiales de pago y enviando recordatorios al cliente por WhatsApp.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a la pestaña **'Cobranzas / Cuotas'**.\n"
                "2. Buscar al cliente o filtrar por estado ('Al día', 'Por Vencer', 'En Mora').\n"
                "3. Presionar **'Registrar Pago'** en la cuota correspondiente (admite cobro total o parcial en efectivo, transferencia o alias).\n"
                "4. Al confirmar el pago, el sistema genera automáticamente el **Recibo Oficial de Pago en PDF**.\n"
                "5. Presionar **'Aviso WhatsApp'** al lado de cualquier cuota para abrir WhatsApp Web/App con una plantilla personalizada de cobro o recordatorio."
            )
        elif 'caja' in p_lower or 'arqueo' in p_lower or 'gastos' in p_lower or 'calle' in p_lower or 'hormiga' in p_lower:
            return (
                "🏦 **Arqueo de Caja, Gastos Hormiga & Capital en Calle**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Audita la salud financiera de tu negocio, calculando ingresos por cobro de cuotas vs egresos por otorgamiento de préstamos y gastos operativos.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a **'Arqueo de Caja & Control Financiero'**.\n"
                "2. Consultar el **Capital en Calle** (dinero total prestado pendiente de cobro).\n"
                "3. Registrar egresos en **'Gastos Generales'** o **'Gastos Hormiga'** (compras menores para detectar fugas de liquidez).\n"
                "4. Visualizar la **Ganancia Líquida Neta** calculada en tiempo real descontando gastos e impuestos.\n"
                "5. Exportar el reporte mensual a Excel o PDF con el botón **'Exportar Arqueo'**."
            )
        elif 'garante' in p_lower or 'scoring' in p_lower or 'cliente' in p_lower:
            return (
                "👥 **Gestión de Clientes, Scoring & Garantes Solventes**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Mantiene el padrón de clientes organizando sus datos de contacto, scoring de morosidad y vinculación de garantes.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. En **'Clientes'**, presionar **'+ Nuevo Cliente'**.\n"
                "2. Ingresar Nombre, DNI/CUIT, Alias Bancario/CBU y WhatsApp.\n"
                "3. **Scoring Interno (1 a 5★)**: El sistema asigna automáticamente estrellas según la puntualidad en los pagos pasados.\n"
                "4. **Garante Solvente**: Si el cliente tiene un perfil de riesgo o Situación 2 en BCRA, podés registrar los datos del Garante (Nombre, DNI, Dirección y Recibo de sueldo) en su ficha."
            )
        elif 'rifa' in p_lower or 'bingo' in p_lower or 'flyer' in p_lower:
            return (
                "🎟️ **Rifas, Bingos & Diseñador de Banners con IA**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Organiza sorteos de rifas para clientes y genera publicidad profesional con Inteligencia Artificial.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a **'Rifas & Bingos'**.\n"
                "2. Crear un sorteo definiendo el premio y el valor del número.\n"
                "3. Presionar **'Generar Flyer Promocional con IA'** para crear un banner gráfico publicitario en base 64 listo para redes sociales.\n"
                "4. Imprimir los cartones de bingo o comprobantes de números vendidos."
            )
        elif 'camscanner' in p_lower or 'ocr' in p_lower or 'escaner' in p_lower or 'escáner' in p_lower:
            return (
                "📷 **Escáner CamScanner OCR con IA Vision**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Convierte fotos de pagarés en papel, recibos o DNI en texto editable estructurado mediante el modelo multimodal de IA.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a **'CamScanner OCR'**.\n"
                "2. Subir una imagen o tomar una foto con la cámara del celular.\n"
                "3. Presionar **'Escanear Documento'**. La IA extraerá importes, nombres, fechas y firmas formateando los datos para exportar a Word o PDF."
            )
        elif 'cv' in p_lower or 'curriculum' in p_lower or 'currículum' in p_lower:
            return (
                "📄 **Convertidor Universal & Creador de CVs con IA**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Diseña Currículums Vitae profesionales con inteligencia artificial optimizando el perfil laboral para ofertas de empleo.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a **'Convertidor Universal / CV Creator'**.\n"
                "2. Cargar la experiencia, estudios y habilidades o redactar los datos básicos.\n"
                "3. Elegir la plantilla visual preferida (**Creativa**, **Elegante**, **Minimalista**) e imprimir o descargar en PDF."
            )
        elif 'compras' in p_lower or 'voz' in p_lower or 'zero-ui' in p_lower:
            return (
                "🛒 **Lista de Compras & Dictado Zero-UI por Voz/WhatsApp**\n\n"
                "📌 **¿Para qué sirve?**\n"
                "Organiza las compras de insumos para el negocio u hogar agrupándolos por comercio y eliminando duplicados mediante IA.\n\n"
                "🚀 **¿Cómo usarlo?**\n"
                "1. Ir a **'Lista de Compras'**.\n"
                "2. Usar el botón de **Dictado por Voz** o enviar la lista por mensaje.\n"
                "3. La IA procesa el texto, separa los ítems por rubro (Verdulería, Carnicería, Almacén) y elimina repeticiones automáticamente."
            )

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

        lines.append("\n💡 *Podés consultar cualquier duda operativa o escribir el CUIT/Nombre de un cliente para auditar su BCRA.*")
    elif not ci and not bcra:
        lines.append(
            "🤖 **Bienvenido al Asesor Financiero, Contador IA & Manual Operativo del Sistema**\n\n"
            "Puedo ayudarte con:\n"
            "1. 🏛️ **Evaluación BCRA & Créditos**: Escribí el CUIT o nombre de un cliente para evaluar si otorgarle un préstamo.\n"
            "2. 📱 **Pagaré Express QR**: Explicación de cómo generar y hacer firmar pagarés a distancia.\n"
            "3. 💰 **Cobranzas & Recibos**: Cómo registrar pagos parciales/totales y notificar por WhatsApp.\n"
            "4. 🏦 **Arqueo de Caja**: Consulta de Capital en Calle, Gastos Hormiga y Ganancia Neta.\n"
            "5. 🛠️ **Guía Operativa**: Consultame cómo usar cualquier sección del sistema."
        )

    return "\n".join(lines)


def chat_ia_asesor_contador(prompt: str, rol: str = "asesor", context_data: dict = None) -> str:
    """Atiende al Contador Virtual IA & Asesor Financiero inyectando contexto de Clientes, BCRA y guía completa de la app."""
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
            context_str += f"• Alias Bancario: {ci.get('bank_alias') or 'No registrado'}\n"
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

        if "calendar_summary" in context_data and context_data["calendar_summary"]:
            context_str += "\n--- AGENDA Y VENCIMIENTOS PRÓXIMOS EN CALENDARIO ---\n"
            for citem in context_data["calendar_summary"]:
                context_str += f"• [{citem.get('category', 'SERVICIO').upper()}] {citem.get('title')} - Vence: {citem.get('due_date')} {citem.get('due_time') or ''}\n"

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
        "Sos el Contador Virtual IA, Asesor Financiero & Experto Operativo del Sistema de Gestión de Préstamos.\n"
        "Conocés al 100% TODAS las funciones y módulos de la aplicación (Clientes, Préstamos, Pagaré Express QR, Cobranzas, Arqueo de Caja, Evaluación Crediticia BCRA, Notificaciones WhatsApp, PDF, Agenda, Rifas con IA, Escáner CamScanner OCR, CV Creator y Lista de Compras).\n\n"
        "TUS DOS ROLES PRINCIPALES SON:\n"
        "1. **GUÍA OPERATIVO Y MANUAL INTERACTIVO**: Si el usuario te pregunta cómo usar una función, para qué sirve, dónde está o cómo realizar un procedimiento, explicáselo paso a paso de forma sumamente clara, amable y estructurada.\n"
        "2. **AUDITOR CREDITICIO & ASESOR CONTABLE**: Si el usuario consulta sobre un cliente o si puede otorgarle determinado dinero:\n"
        "   - Analizá el Historial BCRA (Situación 1 a 6, deudas en bancos/entidades, días de atraso, cheques rechazados).\n"
        "   - Analizá el Historial Interno (Nombre, CUIT, Alias Bancario si registra, Scoring 1-5★, cuotas vencidas, cumplimiento).\n"
        "   - Emití Dictamen: 🟢 APROBADO, 🟡 OBSERVADO CON CONDICIONES (con Garante Solvente) o 🔴 RECHAZADO.\n"
        "   - Asesorá sobre cuota mensual recomendada, tasa y notificaciones por WhatsApp o PDF.\n\n"
        "Responde siempre de manera muy ejecutiva, clara y pulcra, utilizando viñetas y emojis conceptuales (🏛️ 📊 🟢 🟡 🔴 💳 💡 👤 📱 💰 🚀)."
    )

    full_prompt = prompt
    if context_str:
        full_prompt = f"{prompt}\n\n{context_str}"

    models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for m_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=m_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"[Gemini AI Chat Model Exception ({m_name})]: {e}")

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

