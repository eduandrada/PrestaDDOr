/* Frontend Logic with Alpine.js & Chart.js for Loan Management Application */

function registerPrestamosApp() {
    if (window.Alpine && !window._prestamosAppRegistered) {
        window._prestamosAppRegistered = true;
        window.Alpine.data('prestamosApp', () => ({
            // App Navigation State
            activeTab: 'dashboard',
            clientSubTab: 'directorio', // 'directorio' | 'simulador'
            privacyMode: localStorage.getItem('privacyMode') === 'true',
            darkMode: localStorage.getItem('darkMode') === 'true',
            
            // Data Collections
            stats: {
                capital_en_calle: 0,
                intereses_a_cobrar: 0,
                ganancia_liquida_mes: 0,
                deployed_capital: 0,
                total_interest_collected: 0,
                total_capital_recovered: 0,
                total_expenses: 0,
                fixed_expenses: 0,
                ant_expenses: 0,
                ant_expenses_count: 0,
                net_yield: 0,
                roi_percentage: 0,
                real_rate_percentage: 0,
                mora_percentage: 0,
                overdue_inst_count: 0,
                total_inst_count: 0,
                alerts: [],
                expenses_by_cat: { Fijo: 0, Variable: 0, Extraordinario: 0 },
                clients_count: 0,
                active_loans_count: 0,
                completed_loans_count: 0
            },
            clients: [],
            loans: [],
            expenses: [],
            settings: {
                company_name: 'Prestamos & Finanzas Familia Andrada',
                alias_cbu: 'FAMILIA.ANDRADA.MP',
                qr_text: '',
                company_cuit: '', bank_alias: '',
                company_bank: '',
                company_titular: '',
                company_phone: '',
                company_address: '',
                default_grace_days: '3',
                default_late_fee: '1.0',
                ant_expense_threshold: '2500'
            },

            // Personal Accounts & AI Cashflow State (Pareja: Eduardo & Maira)
            personalBills: [],
            // Dólar Rates & USD Calculator State
            accountSubSection: 'cuentas', // 'cuentas' | 'sueldos' | 'gastos' | 'dolar' | 'ia' | 'todas'
            dolarRates: null,
            dolarLoading: false,
            dolarLastUpdated: '',
            usdInput: 100,
            selectedDolarType: 'oficial', // 'oficial' | 'tarjeta' | 'blue'
            salaryEduardo: 550000,
            salaryMaira: 450000,
            isEditingSalaries: false,
            salarySavedMessage: '',
            selectedAccountMonth: 9,
            selectedAccountYear: 2026,
            monthNames: ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
            personalAccountsMetrics: {
                total_bills_amount: 0,
                total_pending: 0,
                total_paid: 0,
                cards_total: 0,
                services_total: 0,
                free_flow: 0,
                debt_ratio: 0,
                health_status: 'Saludable',
                badge_color: 'emerald',
                eduardo: { salary: 550000, bills_total: 0, free_flow: 0, debt_ratio: 0 },
                maira: { salary: 450000, bills_total: 0, free_flow: 0, debt_ratio: 0 }
            },
            billCategoryFilter: 'todos',
            billOwnerFilter: 'todos',
            billForm: {
                id: null,
                name: '',
                category: 'tarjeta',
                owner: 'Compartido',
                amount: '',
                due_day: 10,
                status: 'pendiente',
                notes: '',
                month: 9,
                year: 2026,
                installments_count: 1,
                is_recurring: true
            },
            aiTips: [],
            currentAiTipIndex: 0,
            aiAdvisorQuery: '',
            aiAdvisorResponse: '',
            isAiAdvisorLoading: false,
            historySummary: [],

            // Search & Filters
            clientSearch: '',
            loanSearch: '',
            loanStatusFilter: 'todos',
            selectedMonthFilter: 'todos',
            selectedYearFilter: 'todos',

            // Loan Selection for Bulk Actions
            selectedLoanIds: [],
            selectAllLoans: false,

            // Expenses Filter & Selection
            selectedExpenseMonthFilter: 'todos',
            selectedExpenseYearFilter: 'todos',
            selectedExpenseCategoryFilter: 'todos',
            selectedExpenseIds: [],
            selectAllExpenses: false,

            // Cajas Details State
            activeCajaDetail: null,

            // General History & Selective Deletion
            generalHistory: [],
            historyMonthFilter: 'todos',
            historyYearFilter: 'todos',
            historyTypeFilter: 'todos',
            selectedHistoryItems: [], // List of { raw_type, id }
            selectAllHistory: false,

            // AI Financial Advisor Bot State
            aiAdvisor: {
                status: 'idle',
                capital_inviolable: 0,
                safe_withdrawable_amount: 0,
                reinvestment_portion: 0,
                net_liquid_profit: 0,
                ant_expenses_month: 0,
                mora_percentage: 0,
                alerts: [],
                recommendations: [],
                chatMessages: [
                    { role: 'assistant', text: '¡Hola! Soy tu Asistente de Educación Financiera con IA. Analizo tus números en tiempo real para enseñarte qué dinero tocar y no tocar, eliminar gastos extras e invertir de forma inteligente. ¿En qué te puedo asesorar hoy?' }
                ],
                userPrompt: ''
            },

            // Simulator Reactive State
            sim: {
                amount: 50000,
                interestRate: 15,
                rateType: 'mensual',
                modality: 'mensual',
                installments: 4
            },

            // Modals & Active State
            activeModal: null, // 'newClient', 'editClient', 'clientHistory', 'newLoan', 'viewLoan', 'payInstallment', 'newExpense', 'whatsapp', 'receipt', 'quoteModal', 'cajaDetail', 'generalHistoryModal', 'aiAdvisorModal', 'lightbox'
            activeLightbox: null,
            selectedClient: null,
            selectedClientHistory: null,
            selectedLoan: null,
            selectedInstallment: null,
            activeReceipt: null,
            activeWhatsapp: {
                phone: '',
                message: '',
                clientName: '',
                url: ''
            },
            quoteForm: {
                client_id: '',
                client_name: 'Cliente Estimado/a',
                whatsapp: '',
                email: '',
                channel: 'whatsapp', // 'whatsapp', 'email', 'sms'
                amount: 50000,
                installments_count: 4,
                interest_rate: 15,
                rate_type: 'mensual',
                modality: 'mensual'
            },

            // Toast & Notifications State
            toastMessage: '',
            toastType: 'success', // 'success', 'error', 'info'
            showToast(msg, type = 'success') {
                this.toastMessage = msg;
                this.toastType = type;
                setTimeout(() => { this.toastMessage = ''; }, 4500);
            },

            // BCRA State
            bcraSearchCuit: '',
            bcraReport: { loading: false, data: null, error: null },

            // Forms State
            createdClientSuccess: null,
            selectedGuarantorClient: null,
            createdLoanSuccess: null,
            marqueeNews: [],
            isRefreshingNews: false,
            newsRefreshMessage: '',
            clientForm: { 
                id: null, 
                name: '', 
                whatsapp: '', 
                address: '', 
                cuit: '', 
                email: '', 
                notes: '',
                has_guarantor: false,
                guarantor_name: '',
                guarantor_address: '',
                guarantor_cuit: '',
                guarantor_phone: '',
                send_whatsapp: false,
                download_pdf: false,
                whatsapp_target: 'client',
                custom_phone: ''
            },
            loanForm: { 
                client_id: '', 
                amount: 50000, 
                interest_rate: 15, 
                rate_type: 'mensual', 
                modality: 'mensual', 
                installments_count: 4, 
                start_date: new Date().toISOString().split('T')[0], 
                grace_days: 3, 
                late_fee_type: 'porcentaje', 
                late_fee_value: 1.0, 
                notes: '',
                send_whatsapp: true,
                download_pdf: false,
                whatsapp_target: 'titular'
            },
            editLoanForm: { id: null, notes: '', grace_days: 3, late_fee_type: 'porcentaje', late_fee_value: 1.0, status: 'activo' },
            cashflowDetailData: { total_received: 0, total_capital: 0, total_interest: 0, payments_count: 0, by_method: {}, payments: [] },
            paymentForm: { installment_id: null, amount: 0, payment_method: 'Transferencia', notes: '' },
            expenseForm: { category: 'Fijo', description: '', amount: '', date: new Date().toISOString().split('T')[0], is_ant_expense: false },
            docForm: { client_id: '', loan_id: '', doc_type: 'dni_frente', title: 'DNI (Frente)', image_data: '', is_uploading: false },

            // PWA Prompt & Express Pagaré State
            deferredPwaPrompt: null,
            isPwaInstalled: false,
            expressPagare: {
                client_id: '',
                client_name: '',
                amount: 50000,
                installments_count: 4,
                interest_rate: 15,
                modality: 'mensual',
                return_date: '',
                notes: '',
                token: '',
                qr_img_url: '',
                sign_url: '',
                wa_url: ''
            },

            // Sorteo Express & Rifas State
            raffles: [],
            currentRaffle: null,
            raffleForm: {
                title: '',
                description: '',
                mode: 'numbers', // 'numbers', 'names', 'scratch', 'slot', 'bingo', 'loteria'
                range_min: 1,
                range_max: 100,
                custom_numbers: '',
                names_list: '',
                ticket_price: 1000,
                prizes: [{ rank: 1, title: '1° Premio: Asado Completo' }]
            },
            goldenTicketModal: null, // { hash, ticket_code, winner_name, raffle_title, prize_title }
            scratchState: { active: false, canvas: null, ctx: null, prizeRevealed: false },
            slotState: { active: false, spinning: false, reels: ['❓', '❓', '❓'], winner: null },
            flyerModal: { open: false, imgUrl: '', raffleTitle: '' },

            // Compras & Hogar State
            shoppingItems: [],
            shoppingSubTab: 'compras', // 'compras' | 'calendario' | 'zeroui' | 'asado'
            shoppingCategoryFilter: 'todos',
            shoppingForm: { category: 'Supermercado', name: '', quantity: '1', notes: '' },
            noticeItems: [],
            noticeForm: { title: '', content: '', color: 'yellow', is_pinned: false },
            calendarItems: [],
            calendarForm: { event_date: new Date().toISOString().split('T')[0], title: '', category: 'servicios', notes: '' },
            zeroUiText: '',
            zeroUiResult: null,
            isZeroUiProcessing: false,

            // Marquee Header Live State (Clima Catamarca, Reloj & Novedades Únicas)
            catamarcaWeather: { temp: '--°C', condition: 'Catamarca', icon: '📍' },
            currentDateStr: '',
            currentTimeStr: '',
            currentDateTimeStr: '',

            // BCRA Sub-section State & Method
            bcraSearchCuit: '',
            bcraResult: null,
            bcraLoading: false,

            // Settings & Global Audit Log State
            settingsTab: 'empresa', // 'empresa' | 'parametros' | 'auditoria'
            settingsForm: {
                company_name: '',
                company_cuit: '',
                alias_cbu: '',
                company_cbu: '',
                company_bank: '',
                company_titular: '',
                company_phone: '',
                company_address: '',
                default_grace_days: '3',
                default_late_fee: '1.0',
                ant_expense_threshold: '2500',
                qr_biometric_expiry_minutes: '30',
                biometric_sign_title: 'Firma Digital Biométrica 2026'
            },
            globalVaultDocTypeFilter: 'todos',
            globalVaultSearch: '',
            globalVaultDocs: [],
            clientQrRequests: [],
            selectedQrRequest: null,
            auditLogs: [],
            auditSearch: '',
            isAuditLoading: false,
            createdLoanSuccess: null,

            async consultarBcraSubSection() {
                if (!this.bcraSearchCuit || this.bcraSearchCuit.trim().length < 7) {
                    alert("Por favor ingrese un CUIT/CUIL o DNI válido (ej: 20301234567)");
                    return;
                }
                this.bcraLoading = true;
                try {
                    const clean = this.bcraSearchCuit.trim().replace(/-/g, '');
                    const res = await fetch(`/api/bcra/${clean}`);
                    const data = await res.json();
                    if (data.success) {
                        this.bcraResult = data.data;
                    } else {
                        alert(data.error || "No se obtuvieron datos para el CUIT ingresado.");
                    }
                } catch (e) {
                    console.error("Error al consultar BCRA:", e);
                    alert("Error de comunicación con la Central de Deudores BCRA.");
                } finally {
                    this.bcraLoading = false;
                }
            },

            get latestNotice() {
                if (!this.noticeItems || this.noticeItems.length === 0) return null;
                const pinned = this.noticeItems.find(n => n.is_pinned);
                return pinned || this.noticeItems[0];
            },

            get top2Notices() {
                if (!this.noticeItems || !Array.isArray(this.noticeItems)) return [];
                return this.noticeItems.slice(0, 2);
            },

            openExternalNews(url) {
                if (url) window.open(url, '_blank');
            },

            get latestCalendarEvent() {
                if (!this.calendarItems || this.calendarItems.length === 0) return null;
                return this.calendarItems[0];
            },

            comidasForm: {
                event_type: 'asado',
                menu_type: 'asado',
                people: 10,
                adults: 10,
                children: 0,
                vegetarians: 0,
                ticket_price: 0,
                bought_items: [
                    { name: 'Carne / Asado / Verduras', price: 15000, category: 'alimentos' },
                    { name: 'Vino / Cerveza / Gaseosas', price: 6500, category: 'bebidas' },
                    { name: 'Helado / Torta', price: 4000, category: 'postres' },
                    { name: 'Hielo / Carbón / Servilletas', price: 2500, category: 'varios' }
                ],
                ticket_images: []
            },
            comidasResult: null,
            asadoForm: { people: 10, include_asado: true, include_drinks: true, include_ice: true, ticket_price: 0, custom_notes: '' },
            asadoResult: null,

            // Universal Converter State (Mobile-First 2026)
            converterCategory: 'doc',
            converterForm: {
                targetFormat: 'docx',
                isOcr: false,
                isRecording: false,
                recordingTime: 0,
                recordingTimer: null,
                mediaRecorder: null,
                audioChunks: [],
                audioBlob: [],
                statusText: '',
                isConverting: false
            },

            // Chart References

            expenseChart: null,
            recoveryChart: null,

            // Application Lifecycle Initializer
            init() {
                if (this.darkMode) document.documentElement.classList.add('dark');
                if (this.privacyMode) document.body.classList.add('privacy-mode');
                this.loadAllData();
                this.fetchClientRegistrationRequests();
                this.fetchDolarRates();
                this.fetchCatamarcaWeather();
                this.startMarqueeClock();

                window.addEventListener('beforeinstallprompt', (e) => {
                    e.preventDefault();
                    this.deferredPwaPrompt = e;
                });
                window.addEventListener('appinstalled', () => {
                    this.isPwaInstalled = true;
                    this.deferredPwaPrompt = null;
                });
                
                // Real-time synchronization polling (syncs stats & marquee live across devices every 4 sec)
                setInterval(() => {
                    this.fetchStats();
                    this.fetchNotices();
                    this.fetchCalendarEvents();
                    if (this.activeTab === 'loans') this.fetchLoans();
                    if (this.activeTab === 'expenses' || (this.activeTab === 'accounts' && (this.accountSubSection === 'gastos' || this.accountSubSection === 'todas'))) this.fetchExpenses();
                    if (this.activeTab === 'accounts') this.fetchPersonalAccounts();
                    if (this.activeTab === 'raffles') this.fetchRaffles();
                    if (this.activeTab === 'shopping') this.fetchShoppingItems();
                }, 4000);
            },

            switchTab(tabName) {
                if (tabName === 'simulator') {
                    this.activeTab = 'clients';
                    this.clientSubTab = 'simulador';
                } else if (tabName === 'expenses') {
                    this.activeTab = 'accounts';
                    this.accountSubSection = 'gastos';
                    this.fetchExpenses();
                } else {
                    this.activeTab = tabName;
                }
                window.scrollTo({ top: 0, behavior: 'smooth' });
                if (this.activeTab === 'dashboard') {
                    this.fetchDolarRates();
                    this.$nextTick(() => this.renderCharts());
                }
                if (this.activeTab === 'accounts') {
                    this.fetchPersonalAccounts();
                    if (this.accountSubSection === 'gastos' || this.accountSubSection === 'todas') {
                        this.fetchExpenses();
                    }
                }
                if (this.activeTab === 'raffles') {
                    this.fetchRaffles();
                }
                if (this.activeTab === 'shopping') {
                    this.fetchShoppingItems();
                    this.fetchNotices();
                    this.fetchCalendarEvents();
                }
            },

            togglePrivacy() {
                this.privacyMode = !this.privacyMode;
                localStorage.setItem('privacyMode', this.privacyMode);
                if (this.privacyMode) {
                    document.body.classList.add('privacy-mode');
                } else {
                    document.body.classList.remove('privacy-mode');
                }
            },

            toggleDarkMode() {
                this.darkMode = !this.darkMode;
                localStorage.setItem('darkMode', this.darkMode);
                if (this.darkMode) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                this.renderCharts();
            },

            async loadAllData() {
                await Promise.all([
                    this.fetchStats(),
                    this.fetchClients(),
                    this.fetchLoans(),
                    this.fetchExpenses(),
                    this.fetchSettings(),
                    this.fetchPersonalAccounts(),
                    this.fetchRaffles(),
                    this.fetchShoppingItems(),
                    this.fetchNotices(),
                    this.fetchCalendarEvents(),
                    this.fetchNews()
                ]);
                this.$nextTick(() => this.renderCharts());
            },

            async fetchNews() {
                try {
                    const res = await fetch('/api/news');
                    if (res.ok) {
                        this.marqueeNews = await res.json();
                    }
                } catch (e) {
                    console.error("Error fetching Catamarca news:", e);
                }
            },

            async refreshNewsManual() {
                this.isRefreshingNews = true;
                this.newsRefreshMessage = '';
                try {
                    const res = await fetch('/api/news/refresh', { method: 'POST' });
                    const data = await res.json();
                    if (data.success) {
                        await this.fetchNews();
                        this.newsRefreshMessage = `✅ ¡${data.count} noticias actualizadas con éxito a las ${data.updated_at}!`;
                        setTimeout(() => { this.newsRefreshMessage = ''; }, 4500);
                    } else {
                        this.newsRefreshMessage = '⚠️ No se pudieron refrescar las noticias.';
                    }
                } catch (e) {
                    console.error("Error al actualizar noticias:", e);
                    this.newsRefreshMessage = '❌ Error al conectar con el servidor.';
                } finally {
                    this.isRefreshingNews = false;
                }
            },

            getMarqueeDurationStyle() {
                if (this.settings.marquee_speed_seconds || (this.settingsForm && this.settingsForm.marquee_speed_seconds)) {
                    const secs = this.settingsForm?.marquee_speed_seconds || this.settings.marquee_speed_seconds;
                    return `animation-duration: ${secs}s;`;
                }
                const speed = this.settings.marquee_speed || 'normal';
                if (speed === 'lenta') return 'animation-duration: 65s;';
                if (speed === 'rapida') return 'animation-duration: 22s;';
                return 'animation-duration: 38s;';
            },

            isMarqueeVisible() {
                const val = this.settings.marquee_enabled;
                return val === undefined || val === '1' || val === true || val === 'true';
            },

            async fetchStats() {
                try {
                    const res = await fetch('/api/dashboard/stats');
                    this.stats = await res.json();
                } catch (err) {
                    console.error("Error fetching stats:", err);
                }
            },

            async fetchClients() {
                try {
                    const res = await fetch('/api/clients');
                    this.clients = await res.json();
                } catch (err) {
                    console.error("Error fetching clients:", err);
                }
            },

            async fetchLoans() {
                try {
                    const res = await fetch('/api/loans');
                    this.loans = await res.json();
                    if (this.selectedLoan) {
                        const updated = this.loans.find(l => l.id === this.selectedLoan.id);
                        if (updated) this.selectedLoan = updated;
                    }
                } catch (err) {
                    console.error("Error fetching loans:", err);
                }
            },

            async fetchExpenses() {
                try {
                    const res = await fetch('/api/expenses');
                    const data = await res.json();
                    this.expenses = data.expenses;
                } catch (err) {
                    console.error("Error fetching expenses:", err);
                }
            },

            async fetchSettings() {
                try {
                    const res = await fetch('/api/settings');
                    const data = await res.json();
                    this.settings = { ...this.settings, ...data };
                    this.loanForm.grace_days = parseInt(this.settings.default_grace_days || '3');
                    this.loanForm.late_fee_value = parseFloat(this.settings.default_late_fee || '1.0');
                } catch (err) {
                    console.error("Error fetching settings:", err);
                }
            },

            // Client Methods & BCRA Deudores
            openNewClientModal() {
                this.clientForm = { 
                    id: null, 
                    name: '', 
                    whatsapp: '', 
                    address: '', 
                    cuit: '', 
                    email: '', 
                    notes: '',
                    has_guarantor: false,
                    guarantor_name: '',
                    guarantor_address: '',
                    guarantor_cuit: '',
                    guarantor_phone: '',
                    send_whatsapp: false,
                    download_pdf: false,
                    whatsapp_target: 'client',
                    custom_phone: ''
                };
                this.activeModal = 'newClient';
            },

            openEditClientModal(client) {
                this.clientForm = {
                    id: client.id,
                    name: client.name || '',
                    whatsapp: client.whatsapp || '',
                    address: client.address || '',
                    cuit: client.cuit || '', bank_alias: client.bank_alias || '',
                    email: client.email || '',
                    notes: client.notes || '',
                    has_guarantor: !!client.has_guarantor,
                    guarantor_name: client.guarantor_name || '',
                    guarantor_address: client.guarantor_address || '',
                    guarantor_cuit: client.guarantor_cuit || '',
                    guarantor_phone: client.guarantor_phone || '',
                    send_whatsapp: false,
                    download_pdf: false,
                    whatsapp_target: 'client',
                    custom_phone: ''
                };
                this.activeModal = 'editClient';
            },

            async viewClientHistory(client) {
                try {
                    const res = await fetch(`/api/clients/${client.id}/history`);
                    this.selectedClientHistory = await res.json();
                    this.activeModal = 'clientHistory';
                    if (client.cuit) {
                        this.checkBcra(client.cuit);
                    } else {
                        this.bcraReport = { loading: false, data: null, error: null };
                    }
                } catch (err) {
                    alert("Error al cargar historial del cliente.");
                }
            },

            async checkBcra(cuitOrId) {
                const targetCuit = cuitOrId || (this.selectedClientHistory && this.selectedClientHistory.client ? this.selectedClientHistory.client.cuit : this.bcraSearchCuit);
                if (!targetCuit) {
                    this.bcraReport = { loading: false, data: null, error: 'Por favor ingrese o asegúrese de que el cliente posea un CUIT/CUIL válido.' };
                    return;
                }
                this.bcraReport = { loading: true, data: null, error: null };
                try {
                    const res = await fetch(`/api/bcra/check/${targetCuit}`);
                    const data = await res.json();
                    if (res.ok) {
                        this.bcraReport = { loading: false, data: data, error: null };
                    } else {
                        this.bcraReport = { loading: false, data: null, error: data.error || 'Error al consultar Central de Deudores del BCRA.' };
                    }
                } catch (err) {
                    this.bcraReport = { loading: false, data: null, error: 'Error de conexión con el servidor del BCRA.' };
                }
            },

            async saveClient() {
                if (!this.clientForm || !this.clientForm.name || !this.clientForm.name.trim()) {
                    alert("Por favor ingrese el Nombre Completo del cliente.");
                    return;
                }
                if (!this.clientForm.whatsapp || !this.clientForm.whatsapp.trim()) {
                    alert("Por favor ingrese el WhatsApp / Teléfono del cliente.");
                    return;
                }
                if (!this.clientForm.address || !this.clientForm.address.trim()) {
                    alert("Por favor ingrese el Domicilio Real / Referencias del cliente.");
                    return;
                }
                if (!this.clientForm.cuit || !this.clientForm.cuit.trim()) {
                    alert("Por favor ingrese el CUIT / CUIL del cliente (11 dígitos numéricos).");
                    return;
                }
                const cleanCuit = this.clientForm.cuit.replace(/\D/g, '');
                if (cleanCuit.length !== 11) {
                    alert("El CUIT / CUIL debe contener exactamente 11 dígitos numéricos (ej. 20123456789).");
                    return;
                }

                // Validación de Garante Solidario (si está marcado)
                if (this.clientForm.has_guarantor) {
                    if (!this.clientForm.guarantor_name || !this.clientForm.guarantor_name.trim()) {
                        alert("Por favor ingrese el Nombre y Apellido del Garante.");
                        return;
                    }
                    if (!this.clientForm.guarantor_address || !this.clientForm.guarantor_address.trim()) {
                        alert("Por favor ingrese el Domicilio Real del Garante.");
                        return;
                    }
                    if (!this.clientForm.guarantor_cuit || !this.clientForm.guarantor_cuit.trim()) {
                        alert("Por favor ingrese el CUIT / CUIL del Garante.");
                        return;
                    }
                    const cleanGCuit = this.clientForm.guarantor_cuit.replace(/\D/g, '');
                    if (cleanGCuit.length !== 11) {
                        alert("El CUIT / CUIL del Garante debe contener exactamente 11 dígitos numéricos (ej. 20123456789).");
                        return;
                    }
                    if (!this.clientForm.guarantor_phone || !this.clientForm.guarantor_phone.trim()) {
                        alert("Por favor ingrese el Teléfono / WhatsApp del Garante.");
                        return;
                    }
                }

                const isEdit = !!this.clientForm.id;
                const url = isEdit ? `/api/clients/${this.clientForm.id}` : '/api/clients';
                const method = isEdit ? 'PUT' : 'POST';

                try {
                    const res = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.clientForm)
                    });
                    if (res.ok) {
                        const savedClient = await res.json();
                        const wantsPdf = !!this.clientForm.download_pdf;
                        const wantsWa = !!this.clientForm.send_whatsapp;
                        const waTarget = this.clientForm.whatsapp_target || 'client';
                        const customPh = this.clientForm.custom_phone || '';

                        this.activeModal = null;
                        await this.fetchClients();
                        await this.fetchStats();
                        if (savedClient && savedClient.id && this.loanForm) {
                            this.loanForm.client_id = savedClient.id;
                        }

                        // Acción: Descargar Ficha Oficial en PDF si fue seleccionada
                        if (wantsPdf) {
                            this.downloadClientFichaPDF(savedClient.id);
                        }

                        // Acción: Enviar WhatsApp redactado si fue seleccionado
                        if (wantsWa) {
                            this.sendClientWelcomeWhatsApp(savedClient, waTarget, customPh);
                        }

                        // Mostrar modal de éxito interactivo con accesos directos
                        this.createdClientSuccess = savedClient;
                        this.activeModal = 'clientCreatedSuccess';

                        const successMsg = isEdit 
                            ? `✅ Cliente "${savedClient.name}" actualizado correctamente.`
                            : `🎉 ¡Cliente "${savedClient.name}" registrado satisfactoriamente en el sistema!`;
                        this.showToast(successMsg, 'success');
                    } else {
                        const errData = await res.json().catch(() => ({}));
                        alert(errData.error || "Error al guardar el cliente.");
                    }
                } catch (err) {
                    console.error("saveClient error:", err);
                    alert("Error de conexión al guardar cliente.");
                }
            },

            downloadClientFichaPDF(clientId) {
                if (!clientId) return;
                window.open(`/api/clients/${clientId}/ficha_pdf`, '_blank');
            },

            getClientWelcomeWhatsAppMessage(client) {
                const c = client || this.clientForm || {};
                const name = c.name || 'Cliente';
                const comp = (this.settings && this.settings.company_name) || 'Prestamos & Finanzas';
                const alias = (this.settings && this.settings.alias_cbu) || 'Consultar';
                const phone = (this.settings && this.settings.company_phone) || '';
                const cuit = c.cuit || '';
                const hasG = c.has_guarantor;
                const gName = c.guarantor_name;

                let gText = '';
                if (hasG && gName) {
                    gText = `\n🛡️ *Garante Solidario Registrado:* ${gName}`;
                }

                return `🏛️ *BIENVENIDA & ALTA DE CLIENTE - ${comp.toUpperCase()}* 🏛️\n` +
                       `-----------------------------------------\n` +
                       `👤 *Titular:* ${name}\n` +
                       `🆔 *CUIT/CUIL:* ${cuit}` + gText + `\n\n` +
                       `Estimado/a, le confirmamos que su ficha de cliente ha sido dada de alta satisfactoriamente en nuestro sistema de créditos.\n\n` +
                       `💳 *Datos Bancarios Oficiales para Pagos/Transferencias:* \n` +
                       `• *Alias CBU/CVU:* ${alias}\n` +
                       `• *Atención & Consultas:* ${phone}\n\n` +
                       `Quedamos a su entera disposición para cualquier consulta o solicitud de préstamo.\n` +
                       `Atentamente,\n*${comp}*`;
            },

            sendClientWelcomeWhatsApp(client, target = 'client', customPhone = '') {
                const c = client || this.clientForm || {};
                let phone = '';
                if (target === 'client') {
                    phone = c.whatsapp || '';
                } else if (target === 'guarantor') {
                    phone = c.guarantor_phone || '';
                } else if (target === 'custom') {
                    phone = customPhone || '';
                }
                phone = (phone || '').replace(/\D/g, '');
                const msg = encodeURIComponent(this.getClientWelcomeWhatsAppMessage(c));
                if (phone) {
                    window.open(`https://wa.me/${phone}?text=${msg}`, '_blank');
                } else {
                    window.open(`https://wa.me/?text=${msg}`, '_blank');
                }
            },

            // Guarantor Methods (Perfil del Cliente)
            openGuarantorModal(client) {
                this.selectedGuarantorClient = client || (this.selectedClientHistory ? this.selectedClientHistory.client : null);
                this.activeModal = 'guarantorModal';
            },

            downloadGuarantorCobroPDF(clientId) {
                if (!clientId) return;
                window.open(`/api/clients/${clientId}/garante_cobro_pdf`, '_blank');
            },

            getGuarantorCollectionMessage(client) {
                const c = client || this.selectedGuarantorClient || (this.selectedClientHistory ? this.selectedClientHistory.client : {}) || {};
                const gName = c.guarantor_name || 'Garante Solidario';
                const comp = (this.settings && this.settings.company_name) || 'Prestamos & Finanzas';
                const alias = (this.settings && this.settings.alias_cbu) || 'Consultar';
                const phone = (this.settings && this.settings.company_phone) || '';
                const titular = (this.settings && this.settings.company_titular) || 'Eduardo Andrada';
                const deudor = c.name || 'el Titular Deudor';

                // Calcular deuda pendiente real si está disponible en el historial
                let pendingDebtStr = "regularización de cuotas pendientes";
                if (this.selectedClientHistory && this.selectedClientHistory.loans) {
                    let totalPending = 0;
                    for (const l of this.selectedClientHistory.loans) {
                        if (l.status !== 'completado' && l.status !== 'cancelado') {
                            totalPending += (l.remaining_amount || l.amount);
                        }
                    }
                    if (totalPending > 0) {
                        pendingDebtStr = `$${totalPending.toLocaleString('es-AR', {minimumFractionDigits: 2})}`;
                    }
                }

                return `⚖️ *REQUERIMIENTO FORMAL DE COBRO A GARANTE SOLIDARIO* ⚖️\n` +
                       `-----------------------------------------\n` +
                       `🛡️ *Estimado/a:* ${gName}\n` +
                       `👤 *En su carácter de Garante / Fiador Solidario de:* ${deudor}\n\n` +
                       `Nos comunicamos formalmente del Departamento de Cobranzas de *${comp}* para informarle que ante el vencimiento e impago de las obligaciones contraídas por el titular avalado, se requiere la cancelación del saldo exigible correspondiente (*${pendingDebtStr}*).\n\n` +
                       `💳 *Datos Bancarios para Cancelación Inmediata:*\n` +
                       `• *Alias CBU/CVU:* ${alias}\n` +
                       `• *Titular:* ${titular}\n` +
                       `• *Atención & Consultas:* ${phone}\n\n` +
                       `Por favor, proceda a la cancelación o comuníquese a la brevedad para regularizar la situación y evitar acciones legales ejecutivas.\n` +
                       `Atentamente,\n*Cobranzas & Asuntos Legales - ${comp}*`;
            },

            sendGuarantorWhatsApp(client) {
                const c = client || this.selectedGuarantorClient || (this.selectedClientHistory ? this.selectedClientHistory.client : {}) || {};
                let phone = (c.guarantor_phone || '').replace(/\D/g, '');
                const msg = encodeURIComponent(this.getGuarantorCollectionMessage(c));
                if (phone) {
                    window.open(`https://wa.me/${phone}?text=${msg}`, '_blank');
                } else {
                    window.open(`https://wa.me/?text=${msg}`, '_blank');
                }
            },

            async deleteClient(id) {
                if (!confirm("¿Desea eliminar este cliente y todos sus registros asociados?")) return;
                try {
                    const res = await fetch(`/api/clients/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al eliminar cliente.");
                }
            },

            downloadVCard(clientId) {
                window.location.href = `/api/clients/${clientId}/vcard`;
            },

            openPagarePDF(loanId) {
                window.open(`/api/loans/${loanId}/pagare_pdf`, '_blank');
            },

            // Client Documents & Gallery Vault Methods
            getDocTypeLabel(type) {
                if (type === 'dni_frente') return 'DNI (Frente)';
                if (type === 'dni_dorso') return 'DNI (Dorso)';
                if (type === 'pagare_firmado') return 'Pagaré Firmado (Foto)';
                if (type === 'domicilio') return 'Comprobante de Domicilio';
                if (type === 'recibo_sueldo') return 'Recibo de Sueldo';
                return 'Documento Adjunto';
            },

            openDocUploadModal(clientId, docType = 'dni_frente', loanId = null) {
                this.docForm = {
                    client_id: clientId,
                    loan_id: loanId || '',
                    doc_type: docType,
                    title: this.getDocTypeLabel(docType),
                    image_data: '',
                    is_uploading: false
                };
                this.activeModal = 'docUploadModal';
            },

            onDocTypeChange() {
                this.docForm.title = this.getDocTypeLabel(this.docForm.doc_type);
            },

            onDocFileSelected(event) {
                const file = event.target.files[0];
                if (!file) return;

                if (file.size > 10 * 1024 * 1024) {
                    alert("La imagen excede el límite de 10 MB. Por favor seleccione una imagen más liviana.");
                    event.target.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = (e) => {
                    this.docForm.image_data = e.target.result;
                };
                reader.readAsDataURL(file);
            },

            async submitClientDocument() {
                if (!this.docForm.client_id) {
                    alert("Seleccione un cliente.");
                    return;
                }
                if (!this.docForm.image_data) {
                    alert("Por favor tome una foto o seleccione una imagen antes de guardar.");
                    return;
                }

                this.docForm.is_uploading = true;
                try {
                    const res = await fetch(`/api/clients/${this.docForm.client_id}/documents`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            doc_type: this.docForm.doc_type,
                            title: this.docForm.title,
                            image_data: this.docForm.image_data,
                            loan_id: this.docForm.loan_id || null
                        })
                    });

                    if (res.ok) {
                        const newDoc = await res.json();
                        if (this.selectedClientHistory && this.selectedClientHistory.client.id == this.docForm.client_id) {
                            if (!this.selectedClientHistory.documents) this.selectedClientHistory.documents = [];
                            this.selectedClientHistory.documents.unshift(newDoc);
                        }
                        await this.fetchClients();
                        alert(`¡Documento "${this.docForm.title}" guardado y subido correctamente!`);
                        this.activeModal = 'clientHistory';
                    } else {
                        alert("Error al guardar el documento en la base de datos.");
                    }
                } catch (err) {
                    alert("Error de conexión al subir el documento.");
                } finally {
                    this.docForm.is_uploading = false;
                }
            },

            async deleteClientDocument(docId, clientId) {
                if (!confirm("¿Confirma eliminar este documento de la bóveda del cliente?")) return;
                try {
                    const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
                    if (res.ok) {
                        if (this.selectedClientHistory && this.selectedClientHistory.documents) {
                            this.selectedClientHistory.documents = this.selectedClientHistory.documents.filter(d => d.id !== docId);
                        }
                        await this.fetchClients();
                    }
                } catch (err) {
                    alert("Error al eliminar el documento.");
                }
            },

            openLightbox(doc) {
                this.activeLightbox = doc;
            },

            closeLightbox() {
                this.activeLightbox = null;
            },

            // Signature Canvas Methods
            initSignaturePad() {
                this.$nextTick(() => {
                    const canvas = document.getElementById('signatureCanvasPad');
                    if (!canvas) return;
                    const ctx = canvas.getContext('2d');
                    ctx.strokeStyle = '#0f172a';
                    ctx.lineWidth = 2.5;
                    ctx.lineCap = 'round';
                    
                    let isDrawing = false;
                    const getPos = (e) => {
                        const rect = canvas.getBoundingClientRect();
                        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
                        return {
                            x: clientX - rect.left,
                            y: clientY - rect.top
                        };
                    };

                    const start = (e) => {
                        isDrawing = true;
                        const pos = getPos(e);
                        ctx.beginPath();
                        ctx.moveTo(pos.x, pos.y);
                    };

                    const move = (e) => {
                        if (!isDrawing) return;
                        e.preventDefault();
                        const pos = getPos(e);
                        ctx.lineTo(pos.x, pos.y);
                        ctx.stroke();
                    };

                    const stop = () => {
                        if (isDrawing) {
                            isDrawing = false;
                            this.loanForm.signature_data = canvas.toDataURL();
                        }
                    };

                    canvas.onmousedown = start;
                    canvas.onmousemove = move;
                    canvas.onmouseup = stop;
                    canvas.ontouchstart = start;
                    canvas.ontouchmove = move;
                    canvas.ontouchend = stop;
                });
            },

            clearSignaturePad() {
                const canvas = document.getElementById('signatureCanvasPad');
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }
                this.loanForm.signature_data = '';
            },

            // Loan Methods
            openNewLoanModal(clientId = null) {
                this.loanForm = {
                    client_id: clientId || (this.clients.length > 0 ? this.clients[0].id : ''),
                    amount: 50000,
                    interest_rate: parseFloat(this.settings.default_interest_rate || '15'),
                    rate_type: 'mensual',
                    modality: this.settings.default_modality || 'mensual',
                    installments_count: parseInt(this.settings.default_installments_count || '4'),
                    start_date: new Date().toISOString().split('T')[0],
                    grace_days: parseInt(this.settings.default_grace_days || '3'),
                    late_fee_type: 'porcentaje',
                    late_fee_value: parseFloat(this.settings.default_late_fee || '1.0'),
                    notes: '',
                    signature_data: '',
                    send_whatsapp: false,
                    download_pdf: false,
                    download_pagare_pdf: false,
                    download_ficha_pdf: false,
                    auto_deliver: false,
                    has_guarantor: false,
                    existing_guarantor_client_id: '',
                    guarantor_name: '',
                    guarantor_dni: '',
                    guarantor_phone: '',
                    guarantor_address: ''
                };
                this.activeModal = 'newLoan';
                this.initSignaturePad();
            },

            toggleAutoDeliverLoanOptions() {
                const isAuto = !!this.loanForm.auto_deliver;
                this.loanForm.send_whatsapp = isAuto;
                this.loanForm.download_pdf = isAuto;
                this.loanForm.download_pagare_pdf = isAuto;
                this.loanForm.download_ficha_pdf = isAuto;
            },

            deliverAllLoanDocuments(loan) {
                if (!loan) return;
                const loanId = loan.id;
                const clientId = loan.client_id;
                
                // 1. Abrir Pagaré PDF
                window.open(`/api/loans/${loanId}/pagare_pdf`, '_blank');
                
                // 2. Abrir Resumen Pre-Vencimiento Día 24
                window.open(`/api/loans/${loanId}/resumen_prevencimiento_pdf`, '_blank');
                
                // 3. Abrir Resumen IA PDF
                window.open(`/api/loans/${loanId}/pdf`, '_blank');

                // 4. Abrir Ficha/Contrato
                if (clientId) {
                    window.open(`/api/clients/${clientId}/ficha_pdf`, '_blank');
                }
                
                // 5. Enviar Notificación por WhatsApp
                if (loan.preview_message) {
                    this.sendLoanWhatsApp(
                        loan.whatsapp_target === 'titular' ? loan.client?.whatsapp : 
                        (loan.whatsapp_target === 'garante' ? loan.client?.guarantor_phone : loan.custom_phone),
                        loan.preview_message
                    );
                } else {
                    this.sendLoanWhatsApp(loan);
                }
            },

            get selectedLoanClient() {
                if (!this.loanForm.client_id) return null;
                return this.clients.find(c => c.id == this.loanForm.client_id) || null;
            },

            get simulatedLoanSummary() {
                const amount = parseFloat(this.loanForm.amount || 0);
                const rate = parseFloat(this.loanForm.interest_rate || 0);
                const count = parseInt(this.loanForm.installments_count || 1);
                const rateType = this.loanForm.rate_type || 'mensual';
                const modality = this.loanForm.modality || 'mensual';

                if (amount <= 0 || count < 1) {
                    return { capital: 0, interest: 0, total: 0, installment: 0 };
                }

                let totalInterest = 0;
                if (rateType === 'directo') {
                    totalInterest = amount * (rate / 100.0);
                } else {
                    let months = count;
                    if (modality === 'semanal') months = count / 4.0;
                    else if (modality === 'quincenal') months = count / 2.0;
                    else if (modality === 'pago_unico') months = 1.0;
                    totalInterest = amount * (rate / 100.0) * Math.max(0.25, months);
                }

                const total = amount + totalInterest;
                const instAmount = total / count;

                return {
                    capital: amount,
                    interest: Math.round(totalInterest * 100) / 100,
                    total: Math.round(total * 100) / 100,
                    installment: Math.round(instAmount * 100) / 100
                };
            },

            async saveLoan() {
                if (!this.loanForm.client_id) {
                    alert("Por favor seleccione un cliente para otorgar el préstamo.");
                    return;
                }
                if (!this.loanForm.amount || parseFloat(this.loanForm.amount) <= 0) {
                    alert("Por favor ingrese un monto de préstamo válido mayor a $0.");
                    return;
                }
                if (!this.loanForm.installments_count || parseInt(this.loanForm.installments_count) < 1) {
                    alert("El número de cuotas debe ser al menos 1.");
                    return;
                }

                try {
                    if (this.loanForm.has_guarantor && this.loanForm.guarantor_name) {
                        await fetch(`/api/clients/${this.loanForm.client_id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                has_guarantor: true,
                                guarantor_name: this.loanForm.guarantor_name,
                                guarantor_dni: this.loanForm.guarantor_dni || '',
                                guarantor_phone: this.loanForm.guarantor_phone || '',
                                guarantor_address: this.loanForm.guarantor_address || ''
                            })
                        }).catch(() => {});
                    }

                    const res = await fetch('/api/loans', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.loanForm)
                    });
                    if (res.ok) {
                        const newLoan = await res.json();
                        this.activeModal = null;
                        await this.loadAllData();
                        this.openLoanCreatedSuccessModal(newLoan);
                    } else {
                        const errData = await res.json().catch(() => ({}));
                        alert(errData.error || "Error al registrar el préstamo.");
                    }
                } catch (err) {
                    console.error("saveLoan error:", err);
                    alert("Error de conexión al registrar préstamo.");
                }
            },

            // Settings & Audit Methods
            // Settings & Audit Methods (Apertura Instantánea 0ms & Unificada)
            openSettingsModal() {
                this.settingsTab = 'empresa';
                this.settingsForm = {
                    // 1. Empresa & Cobranzas
                    company_name: this.settings.company_name || 'Prestamos & Finanzas Familia Andrada',
                    company_cuit: this.settings.company_cuit || '20-33445566-9',
                    alias_cbu: this.settings.alias_cbu || 'FAMILIA.ANDRADA.MP',
                    company_cbu: this.settings.company_cbu || '0000003100045678912345',
                    company_bank: this.settings.company_bank || 'Mercado Pago / Banco Santander',
                    company_titular: this.settings.company_titular || 'Eduardo Andrada',
                    company_phone: this.settings.company_phone || '+54 9 11 3344-5566',
                    company_address: this.settings.company_address || 'Av. Corrientes 1234, CABA',
                    company_email: this.settings.company_email || 'contacto@prestamosandrada.com',
                    company_logo_data: this.settings.company_logo_data || '',
                    qr_text: this.settings.qr_text || '',

                    // 2. Parámetros Financieros & Préstamos
                    default_interest_rate: this.settings.default_interest_rate || '20',
                    default_modality: this.settings.default_modality || 'mensual',
                    default_installments_count: this.settings.default_installments_count || '4',
                    default_grace_days: this.settings.default_grace_days || '3',
                    default_late_fee: this.settings.default_late_fee || '1.0',
                    ant_expense_threshold: this.settings.ant_expense_threshold || '2500',
                    default_max_loan_limit: this.settings.default_max_loan_limit || '150000',
                    overdue_alert_days: this.settings.overdue_alert_days || '3',
                    currency_symbol: this.settings.currency_symbol || '$',
                    guarantor_required_threshold: this.settings.guarantor_required_threshold || '200000',

                    // 3. Marquee & Noticias de Catamarca
                    marquee_enabled: this.settings.marquee_enabled !== undefined ? String(this.settings.marquee_enabled) : '1',
                    marquee_speed: this.settings.marquee_speed || 'normal',
                    marquee_speed_seconds: this.settings.marquee_speed_seconds || 38,
                    marquee_show_news: this.settings.marquee_show_news !== undefined ? String(this.settings.marquee_show_news) : '1',
                    marquee_show_pizarra: this.settings.marquee_show_pizarra !== undefined ? String(this.settings.marquee_show_pizarra) : '1',
                    marquee_show_weather: this.settings.marquee_show_weather !== undefined ? String(this.settings.marquee_show_weather) : '1',
                    marquee_show_datetime: this.settings.marquee_show_datetime !== undefined ? String(this.settings.marquee_show_datetime) : '1',
                    marquee_show_calendar: this.settings.marquee_show_calendar !== undefined ? String(this.settings.marquee_show_calendar) : '1',
                    news_source_esquiu: this.settings.news_source_esquiu !== undefined ? String(this.settings.news_source_esquiu) : '1',
                    news_source_ancasti: this.settings.news_source_ancasti !== undefined ? String(this.settings.news_source_ancasti) : '1',
                    news_source_catamarca_actual: this.settings.news_source_catamarca_actual !== undefined ? String(this.settings.news_source_catamarca_actual) : '1',
                    news_source_la_union: this.settings.news_source_la_union !== undefined ? String(this.settings.news_source_la_union) : '1',
                    custom_marquee_text: this.settings.custom_marquee_text || '',
                    custom_rss_sources: this.settings.custom_rss_sources || '',
                    marquee_keywords: this.settings.marquee_keywords || 'Catamarca, Policiales, Elecciones, Política, Economía, País, Sueldos',

                    // 4. WhatsApp, IA & Notificaciones
                    whatsapp_prefix: this.settings.whatsapp_prefix || '549',
                    whatsapp_template_loan: this.settings.whatsapp_template_loan || '¡Hola {nombre}! Tu préstamo por {monto} ha sido otorgado con éxito.',
                    whatsapp_template_payment: this.settings.whatsapp_template_payment || '¡Hola {nombre}! Te recordamos el vencimiento de tu cuota N° {cuota} por {monto}. Recordá enviar foto/captura del comprobante de transferencia al abonar.',
                    biometric_sign_title: this.settings.biometric_sign_title || 'Firma Digital Biométrica 2026',
                    whatsapp_auto_include_cbu: this.settings.whatsapp_auto_include_cbu !== undefined ? String(this.settings.whatsapp_auto_include_cbu) : '1',
                    auto_generate_pagare: this.settings.auto_generate_pagare !== undefined ? String(this.settings.auto_generate_pagare) : '1',

                    // 5. Sueldos Familiares
                    user_salary_eduardo: this.settings.user_salary_eduardo || '550000',
                    user_salary_maira: this.settings.user_salary_maira || '450000',

                    // 6. Base de Datos & Sistema
                    auto_backup_enabled: this.settings.auto_backup_enabled !== undefined ? String(this.settings.auto_backup_enabled) : '1'
                };
                this.activeModal = 'settingsModal';
                this.fetchSettings().catch(() => {});
            },

            downloadBackupFile() {
                window.location.href = '/api/backup/download';
            },

            async handleRestoreBackup(event) {
                const file = event.target.files[0];
                if (!file) return;
                if (!confirm("⚠️ ATENCIÓN: Esta acción reemplazará los datos actuales por los del archivo de respaldo seleccionado. ¿Desea continuar?")) {
                    event.target.value = '';
                    return;
                }
                const formData = new FormData();
                formData.append('file', file);
                try {
                    const res = await fetch('/api/backup/restore', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok && data.success !== false) {
                        alert("✅ Copia de seguridad restaurada exitosamente.");
                        window.location.reload();
                    } else {
                        alert("❌ Error al restaurar respaldo: " + (data.error || "Formato de archivo inválido"));
                    }
                } catch (e) {
                    alert("❌ Error de red al subir archivo de respaldo.");
                } finally {
                    event.target.value = '';
                }
            },

            onLogoSelected(event) {
                const file = event.target.files[0];
                if (!file) return;
                if (file.size > 1024 * 1024) {
                    alert("El logo no debe superar 1MB de tamaño.");
                    event.target.value = '';
                    return;
                }
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.settingsForm.company_logo_data = e.target.result;
                };
                reader.readAsDataURL(file);
            },

            openDocumentTemplatesModal() {
                this.activeModal = 'documentTemplatesModal';
            },

            onSelectExistingGuarantor(event) {
                const cid = event.target.value;
                if (!cid) return;
                const client = this.clients.find(c => c.id == cid);
                if (client) {
                    this.loanForm.guarantor_name = client.name;
                    this.loanForm.guarantor_dni = client.dni || '';
                    this.loanForm.guarantor_phone = client.whatsapp || '';
                    this.loanForm.guarantor_address = client.address || '';
                }
            },

            async saveSettings() {
                try {
                    const res = await fetch('/api/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.settingsForm)
                    });
                    if (res.ok) {
                        await this.fetchSettings();
                        await this.fetchNews();
                        this.showToast("✅ Ajustes guardados correctamente.", "success");
                        alert("✅ Ajustes del sistema guardados correctamente.");
                    } else {
                        alert("Error al guardar ajustes.");
                    }
                } catch (e) {
                    alert("Error de conexión al guardar ajustes.");
                }
            },

            async loadGlobalVault() {
                try {
                    const type = this.globalVaultDocTypeFilter || 'todos';
                    const res = await fetch(`/api/documents/all?doc_type=${type}`);
                    const data = await res.json();
                    if (data.success) {
                        this.globalVaultDocs = data.documents || [];
                    }
                } catch (e) {
                    console.error("Error al cargar Bóveda Global:", e);
                }
            },

            filteredGlobalVaultDocs() {
                if (!this.globalVaultDocs) return [];
                if (!this.globalVaultSearch || !this.globalVaultSearch.trim()) {
                    return this.globalVaultDocs;
                }
                const q = this.globalVaultSearch.trim().toLowerCase();
                return this.globalVaultDocs.filter(d => 
                    (d.client_name && d.client_name.toLowerCase().includes(q)) ||
                    (d.title && d.title.toLowerCase().includes(q)) ||
                    (d.doc_type && d.doc_type.toLowerCase().includes(q))
                );
            },

            async openClientQrRequestsModal(client) {
                if (!client) return;
                try {
                    const res = await fetch(`/api/biometric_requests?client_id=${client.id}`);
                    const data = await res.json();
                    this.clientQrRequests = Array.isArray(data) ? data : [];
                    this.activeModal = 'clientQrRequestsModal';
                } catch (e) {
                    console.error("Error al obtener solicitudes QR del cliente:", e);
                    alert("No se pudieron cargar las solicitudes QR del cliente.");
                }
            },

            async openClientVaultModal(client) {
                if (!client) return;
                this.globalVaultSearch = client.name || '';
                this.globalVaultDocTypeFilter = 'todos';
                this.settingsTab = 'boveda';
                this.activeModal = 'settingsModal';
                await this.loadGlobalVault();
            },

            async approveBiometricRequest(req) {
                if (!req) return;
                const token = req.token || '';
                const loanId = req.loan_id || req.id || (req.loan ? req.loan.id : null);
                const clientName = req.client_name || (req.client ? req.client.name : 'Cliente');
                const amount = req.amount || 0;

                if (!confirm(`¿Confirmas la APROBACIÓN y ACTIVACIÓN del préstamo por $${amount.toLocaleString('es-AR')} para ${clientName}?`)) {
                    return;
                }
                try {
                    let url = '';
                    if (token) {
                        url = `/api/biometric_requests/${token}/approve`;
                    } else if (loanId) {
                        url = `/api/loans/${loanId}/approve`;
                    } else {
                        return alert("No se especificó la solicitud o ID del préstamo a aprobar.");
                    }

                    const res = await fetch(url, {
                        method: 'POST',
                        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
                    });
                    
                    const contentType = res.headers.get('content-type') || '';
                    if (!contentType.includes('application/json')) {
                        const errText = await res.text();
                        console.error("Server returned non-JSON error:", errText);
                        return alert(`Error del servidor (${res.status}): No se pudo completar la aprobación.`);
                    }

                    const data = await res.json();
                    if (data.success) {
                        alert("✅ Solicitud APROBADA y Préstamo ACTIVADO exitosamente.");
                        if (data.wa_url) {
                            window.open(data.wa_url, '_blank');
                        }
                        if (req.client_id) {
                            await this.fetchClientQrRequests(req.client_id);
                        }
                        await this.fetchLoans();
                        await this.fetchClients();
                        if (this.fetchArqueoCaja) await this.fetchArqueoCaja();
                    } else {
                        alert(data.error || "Error al aprobar la solicitud.");
                    }
                } catch(e) {
                    alert("Error al conectar con el servidor: " + e.message);
                }
            },

            async deleteBiometricRequest(req) {
                if (!req || !req.token) return;
                if (!confirm("¿Seguro que deseas eliminar/rechazar esta solicitud Pagaré Express QR?")) return;
                try {
                    const res = await fetch(`/api/biometric_requests/${req.token}`, { method: 'DELETE' });
                    const data = await res.json();
                    if (data.success) {
                        alert("🗑️ Solicitud eliminada correctamente.");
                        if (req.client_id) {
                            await this.openClientQrRequestsModal({ id: req.client_id });
                        }
                    } else {
                        alert(data.error || "Error al eliminar la solicitud.");
                    }
                } catch (e) {
                    console.error("Error al eliminar solicitud:", e);
                }
            },

            async fetchAuditLogs() {
                this.isAuditLoading = true;
                try {
                    const res = await fetch('/api/audit_logs');
                    if (res.ok) {
                        this.auditLogs = await res.json();
                    }
                } catch (e) {
                    console.error("Error fetching audit logs:", e);
                } finally {
                    this.isAuditLoading = false;
                }
            },

            get filteredAuditLogs() {
                if (!this.auditSearch || !this.auditSearch.trim()) return this.auditLogs;
                const q = this.auditSearch.toLowerCase().trim();
                return this.auditLogs.filter(l => 
                    (l.title && l.title.toLowerCase().includes(q)) ||
                    (l.description && l.description.toLowerCase().includes(q)) ||
                    (l.date && l.date.includes(q))
                );
            },

            // Loan Granted Message & WhatsApp / PDF Helpers
            getLoanWhatsAppMessage(loan) {
                if (!loan) return '';
                const clientName = loan.client_name || (this.clients.find(c => c.id == loan.client_id) || {}).name || 'Cliente';
                const total = loan.total_amount || (loan.amount * 1.15);
                const count = loan.installments_count || 1;
                const instVal = loan.installment_amount || (total / count);
                const startDate = loan.start_date || new Date().toISOString().split('T')[0];

                return `🏛️ *COMPROBANTE DE PRÉSTAMO OTORGADO* 🏛️\n` +
                       `-----------------------------------------\n` +
                       `👤 *Cliente:* ${clientName}\n` +
                       `💵 *Monto Otorgado:* $${Number(loan.amount).toLocaleString('es-AR', {minimumFractionDigits: 2})}\n` +
                       `📊 *Plan de Pagos:* ${count} cuota(s) ${loan.modality || 'mensual'} de $${Number(instVal).toLocaleString('es-AR', {minimumFractionDigits: 2})}\n` +
                       `💰 *Total a Devolver:* $${Number(total).toLocaleString('es-AR', {minimumFractionDigits: 2})}\n` +
                       `📅 *Fecha de Primera Cuota:* ${startDate}\n\n` +
                       `💳 *DATOS PARA TRANSFERENCIA / PAGO:*\n` +
                       `• *Alias CBU/CVU:* ${this.settings.alias_cbu || 'FAMILIA.ANDRADA.MP'}\n` +
                       `• *N° CBU/CVU:* ${this.settings.company_cbu || '0000003100045678912345'}\n` +
                       `• *Titular:* ${this.settings.company_titular || 'Eduardo Andrada'}\n` +
                       `• *Banco/Billetera:* ${this.settings.company_bank || 'Mercado Pago'}\n` +
                       `• *CUIT/CUIL:* ${this.settings.company_cuit || '20-33445566-9'}\n\n` +
                       `🤝 ¡Muchas gracias por su confianza! Quedamos a su disposición.`;
            },

            sendLoanWhatsApp(loan) {
                if (!loan) return;
                const client = this.clients.find(c => c.id == loan.client_id);
                let phone = loan.whatsapp || (client ? client.whatsapp : '');
                if (phone) phone = phone.replace(/\D/g, '');
                const msg = encodeURIComponent(this.getLoanWhatsAppMessage(loan));
                if (phone) {
                    window.open(`https://wa.me/${phone}?text=${msg}`, '_blank');
                } else {
                    window.open(`https://wa.me/?text=${msg}`, '_blank');
                }
            },

            copyToClipboard(text) {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        this.showToast("📋 ¡Mensaje copiado al portapapeles!", "success");
                        alert("📋 ¡Mensaje copiado al portapapeles!");
                    });
                } else {
                    const ta = document.createElement('textarea');
                    ta.value = text;
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                    alert("📋 ¡Mensaje copiado al portapapeles!");
                }
            },

            openLoanCreatedSuccessModal(loan) {
                const client = this.clients.find(c => c.id === loan.client_id) || { name: loan.client_name || 'Cliente', whatsapp: '', has_guarantor: false };
                const totalAmount = (loan.installments || []).reduce((sum, i) => sum + i.amount, 0) || loan.amount;
                const instVal = (loan.installments && loan.installments.length > 0) ? loan.installments[0].amount : Math.round(totalAmount / (loan.installments_count || 1));
                
                let scheduleText = "";
                if (loan.installments && loan.installments.length > 0) {
                    scheduleText = loan.installments.map(i => `  • Cuota #${i.installment_number}: $${i.amount.toLocaleString('es-AR')} (Vence: ${i.due_date})`).join('\n');
                } else {
                    scheduleText = `  • Plan de ${loan.installments_count} cuota(s) ${loan.modality}es de $${instVal.toLocaleString('es-AR')}`;
                }

                let msg = `🏦 *NOTIFICACIÓN DE PRÉSTAMO OTORGADO*\n` +
                          `Estimado/a *${client.name}*:\n\n` +
                          `Nos complace informarle que su solicitud de crédito *#${loan.id}* ha sido *APROBADA Y ACTIVADA* con éxito.\n\n` +
                          `📋 *DETALLES DEL PRÉSTAMO:*\n` +
                          `• Capital Otorgado: *$${loan.amount.toLocaleString('es-AR')}*\n` +
                          `• Modalidad: ${loan.installments_count} cuota(s) ${loan.modality}es\n` +
                          `• Valor por Cuota: *$${Math.round(instVal).toLocaleString('es-AR')}*\n` +
                          `• Total a Reintegrar: *$${Math.round(totalAmount).toLocaleString('es-AR')}*\n` +
                          `• Tasa: ${loan.interest_rate}% ${loan.rate_type}\n\n` +
                          `📅 *CRONOGRAMA DE PAGOS Y VENCIMIENTOS:*\n${scheduleText}\n\n` +
                          `💳 *MEDIOS OFICIALES DE CANCELACIÓN:*\n` +
                          `• Alias CBU: *${this.settings.alias_cbu || 'FAMILIA.ANDRADA.MP'}*\n` +
                          `• CBU: ${this.settings.company_cbu || '0000003100045678912345'}\n` +
                          `• Titular: ${this.settings.company_titular || 'Eduardo Andrada'}\n` +
                          `• Entidad: ${this.settings.company_bank || 'Mercado Pago'}\n\n` +
                          `_Recuerde remitir su comprobante de transferencia por este canal tras realizar cada pago para su debida imputación. ¡Muchas gracias por su confianza!_`;

                // Auto-downloads based on user selected checkboxes in loanForm
                if (this.loanForm && this.loanForm.download_pdf) {
                    this.downloadLoanIAPDF(loan.id);
                }
                if (this.loanForm && this.loanForm.download_pagare_pdf) {
                    this.downloadPagarePDF(loan.id);
                }
                if (this.loanForm && this.loanForm.download_ficha_pdf) {
                    this.downloadClientFichaPDF(loan.client_id);
                }

                this.createdLoanSuccess = {
                    ...loan,
                    client: client,
                    preview_message: msg,
                    whatsapp_target: 'titular',
                    custom_phone: '',
                    additional_contacts: [],
                    new_contact_name: '',
                    new_contact_phone: ''
                };
                this.activeModal = 'loanCreatedSuccess';
            },

            sendLoanWhatsApp(phone, message) {
                if (!phone) {
                    alert("Debe especificar un número de teléfono o WhatsApp válido.");
                    return;
                }
                let clean = String(phone).replace(/[^0-9]/g, '');
                if (clean.length === 10) clean = '549' + clean;
                else if (clean.length === 11 && clean.startsWith('15')) clean = '549' + clean.slice(2);
                else if (clean.length === 12 && clean.startsWith('54') && !clean.startsWith('549')) clean = '549' + clean.slice(2);

                const waUrl = `https://wa.me/${clean}?text=${encodeURIComponent(message || '')}`;
                window.open(waUrl, '_blank');
            },

            downloadLoanIAPDF(loanId) {
                if (!loanId) return;
                window.open(`/api/loans/${loanId}/resumen_ia_pdf`, '_blank');
            },

            downloadPagarePDF(loanId) {
                if (!loanId) return;
                window.open(`/api/loans/${loanId}/pagare_pdf`, '_blank');
            },

            addLoanExtraContact() {
                if (!this.createdLoanSuccess) return;
                const name = (this.createdLoanSuccess.new_contact_name || '').trim();
                const phone = (this.createdLoanSuccess.new_contact_phone || '').trim();
                if (!phone) {
                    alert("Por favor ingrese un número de teléfono para el contacto adicional.");
                    return;
                }
                this.createdLoanSuccess.additional_contacts.push({
                    name: name || 'Contacto Extra',
                    phone: phone
                });
                this.createdLoanSuccess.new_contact_name = '';
                this.createdLoanSuccess.new_contact_phone = '';
            },

            removeLoanExtraContact(idx) {
                if (this.createdLoanSuccess && this.createdLoanSuccess.additional_contacts) {
                    this.createdLoanSuccess.additional_contacts.splice(idx, 1);
                }
            },

            viewLoan(loan) {
                this.selectedLoan = loan;
                this.activeModal = 'viewLoan';
            },

            async deleteLoan(id) {
                if (!confirm("¿Desea eliminar este préstamo y sus cuotas?")) return;
                try {
                    const res = await fetch(`/api/loans/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        this.activeModal = null;
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al eliminar el préstamo.");
                }
            },

            // Loan Bulk Selection
            toggleSelectAllLoans() {
                if (this.selectAllLoans) {
                    this.selectedLoanIds = this.filteredLoans.map(l => l.id);
                } else {
                    this.selectedLoanIds = [];
                }
            },

            toggleSelectLoan(loanId) {
                const idx = this.selectedLoanIds.indexOf(loanId);
                if (idx > -1) {
                    this.selectedLoanIds.splice(idx, 1);
                } else {
                    this.selectedLoanIds.push(loanId);
                }
                this.selectAllLoans = this.selectedLoanIds.length === this.filteredLoans.length && this.filteredLoans.length > 0;
            },

            isLoanSelected(loanId) {
                return this.selectedLoanIds.includes(loanId);
            },

            async deleteSelectedLoans() {
                if (this.selectedLoanIds.length === 0) return;
                if (!confirm(`¿Estás seguro de eliminar los ${this.selectedLoanIds.length} préstamos seleccionados y sus cuotas correspondientes? Esta acción es irreversible.`)) return;
                try {
                    const items = this.selectedLoanIds.map(id => ({ raw_type: 'Loan', id }));
                    const res = await fetch('/api/history/bulk_delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ items })
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert(`Se eliminaron ${data.deleted_count} préstamos.`);
                        this.selectedLoanIds = [];
                        this.selectAllLoans = false;
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al eliminar los préstamos seleccionados.");
                }
            },

            openEditLoanModal(loan) {
                this.editLoanForm = {
                    id: loan.id,
                    notes: loan.notes || '',
                    grace_days: loan.grace_days !== undefined ? loan.grace_days : 3,
                    late_fee_type: loan.late_fee_type || 'porcentaje',
                    late_fee_value: loan.late_fee_value !== undefined ? loan.late_fee_value : 1.0,
                    status: loan.status || 'activo'
                };
                this.activeModal = 'editLoan';
            },

            async saveEditedLoan() {
                try {
                    const res = await fetch(`/api/loans/${this.editLoanForm.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.editLoanForm)
                    });
                    if (res.ok) {
                        this.activeModal = null;
                        await this.loadAllData();
                        alert("Préstamo actualizado correctamente.");
                    } else {
                        alert("Error al actualizar el préstamo.");
                    }
                } catch (err) {
                    console.error(err);
                    alert("Error de conexión al actualizar el préstamo.");
                }
            },

            // Payment & Digital Receipt
            openPayInstallmentModal(inst) {
                this.selectedInstallment = inst;
                this.paymentForm = {
                    installment_id: inst.id,
                    amount: inst.total_due,
                    payment_method: 'Transferencia',
                    notes: `Pago cuota #${inst.number}`
                };
                this.activeModal = 'payInstallment';
            },

            async submitPayment() {
                if (!this.paymentForm.amount || this.paymentForm.amount <= 0) {
                    alert("Ingrese un monto válido.");
                    return;
                }
                try {
                    const res = await fetch(`/api/installments/${this.selectedInstallment.id}/pay`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.paymentForm)
                    });
                    const data = await res.json();
                    if (data.success) {
                        this.activeReceipt = data.receipt_details;
                        this.activeModal = 'receipt';
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al procesar el pago.");
                }
            },

            printReceipt() {
                window.print();
            },

            getQRCodeUrl(text) {
                if (!text) text = "CBU/Alias no configurado";
                return `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(text)}`;
            },

            // WhatsApp Messaging Engine with Configurable Tone & Social Lending Neutral Collector
            openWhatsAppModal(type, item, tone = 'neutral') {
                let phone = item.whatsapp || item.client_whatsapp || '';
                phone = phone.replace(/[^0-9]/g, '');
                const clientName = item.client || item.client_name || 'Cliente';
                const amount = item.amount || item.total_due || 0;
                const instNum = item.number ? `Cuota #${item.number}` : 'Cuota pendiente';
                const formattedAmount = `$${amount.toLocaleString('es-AR', {minimumFractionDigits: 2})}`;
                const aliasStr = this.settings.alias_cbu ? `\n\n💳 *Datos de Pago Directo:*\n• Alias/CBU: *${this.settings.alias_cbu}*` : '';

                let msg = '';
                
                if (tone === 'neutral') {
                    // Cobrador neutral automatizado P2P
                    msg = `🤖 *SISTEMA AUTOMÁTICO DE RECORDATORIOS P2P*\n*${this.settings.company_name}*\n\nEstimado/a ${clientName}, le enviamos esta notificación neutral automática sobre el vencimiento de su cuota (${instNum}) por el valor de *${formattedAmount}*.${aliasStr}\n\n📌 Para confirmar su pago, puede responder adjuntando la captura del comprobante. ¡Muchas gracias!`;
                } else if (tone === 'cordial') {
                    // Recordatorio amigable
                    msg = `😊 *Hola ${clientName}!*\nTe enviamos un saludo cordial de parte de *${this.settings.company_name}*. Te recordamos que se aproxima el vencimiento de tu cuota (${instNum}) por *${formattedAmount}*.${aliasStr}\n\nQuedamos atentos a tu mensaje. ¡Que tengas un excelente día!`;
                } else if (tone === 'formal') {
                    // Notificación formal
                    msg = `📋 *AVISO FORMAL DE VENCIMIENTO*\n*${this.settings.company_name}*\n\nEstimado/a ${clientName}, mediante el presente aviso formal le notificamos la cuota asignada (${instNum}) por la suma de *${formattedAmount}*.${aliasStr}\n\nLe solicitamos realizar la transferencia y remitir la constancia correspondiente.`;
                } else {
                    // Alerta de mora
                    msg = `🚨 *NOTIFICACIÓN DE REGULARIZACIÓN Y MORA*\n*${this.settings.company_name}*\n\nEstimado/a ${clientName}, le notificamos que registra un saldo pendiente con recargos actualizados por *${formattedAmount}*.${aliasStr}\n\nPor favor regularice su pago hoy para evitar la acumulación de mayores punitorios.`;
                }

                const encodedMsg = encodeURIComponent(msg);
                const waUrl = `https://wa.me/${phone}?text=${encodedMsg}`;

                this.activeWhatsapp = {
                    phone: phone,
                    message: msg,
                    clientName: clientName,
                    currentType: type,
                    currentTone: tone,
                    item: item,
                    url: waUrl
                };
                this.activeModal = 'whatsapp';
            },

            // ----------------------------------------------------
            // MOTOR INTELIGENTE DE PRESUPUESTOS (MULTI-CANAL)
            // ----------------------------------------------------
            openQuoteModal(data = null) {
                if (data) {
                    this.quoteForm.amount = data.amount || this.sim.amount;
                    this.quoteForm.installments_count = data.installments || data.installments_count || this.sim.installments;
                    this.quoteForm.interest_rate = data.interestRate || data.interest_rate || this.sim.interestRate;
                    this.quoteForm.rate_type = data.rateType || data.rate_type || this.sim.rateType;
                    this.quoteForm.modality = data.modality || this.sim.modality;
                    
                    if (data.client_id) {
                        this.quoteForm.client_id = data.client_id;
                        this.onQuoteClientChange();
                    } else if (data.name) {
                        this.quoteForm.client_name = data.name;
                        this.quoteForm.whatsapp = data.whatsapp || '';
                        this.quoteForm.email = data.email || '';
                    }
                } else {
                    this.quoteForm.amount = this.sim.amount;
                    this.quoteForm.installments_count = this.sim.installments;
                    this.quoteForm.interest_rate = this.sim.interestRate;
                    this.quoteForm.rate_type = this.sim.rateType;
                    this.quoteForm.modality = this.sim.modality;
                }

                this.activeModal = 'quoteModal';
            },

            onQuoteClientChange() {
                if (!this.quoteForm.client_id) return;
                const c = this.clients.find(item => item.id == this.quoteForm.client_id);
                if (c) {
                    this.quoteForm.client_name = c.name;
                    this.quoteForm.whatsapp = c.whatsapp;
                    this.quoteForm.email = c.email || '';
                }
            },

            get quoteCalculations() {
                const amount = parseFloat(this.quoteForm.amount) || 0;
                const rate = parseFloat(this.quoteForm.interest_rate) || 0;
                const instCount = parseInt(this.quoteForm.installments_count) || 1;
                
                let months = instCount;
                if (this.quoteForm.modality === 'semanal') months = instCount / 4.0;
                if (this.quoteForm.modality === 'quincenal') months = instCount / 2.0;
                if (this.quoteForm.modality === 'pago_unico') months = 1.0;

                let totalInterest = 0;
                if (this.quoteForm.rate_type === 'directo') {
                    totalInterest = amount * (rate / 100.0);
                } else {
                    totalInterest = amount * (rate / 100.0) * Math.max(0.25, months);
                }

                const totalToPay = amount + totalInterest;
                const installmentValue = totalToPay / instCount;

                return {
                    amount: amount,
                    totalInterest: totalInterest,
                    totalToPay: totalToPay,
                    installmentValue: installmentValue
                };
            },

            get generatedQuoteText() {
                const name = this.quoteForm.client_name || 'Cliente Estimado/a';
                const c = this.quoteCalculations;
                const comp = 'Mutuo con Interés';
                const aliasStr = this.settings.alias_cbu ? `\n💳 *Datos de Transferencia:* Alias/CBU *${this.settings.alias_cbu}*` : '';

                if (this.quoteForm.channel === 'whatsapp') {
                    return `📋 *PRESUPUESTO DE MUTUO CON INTERÉS*\n*${comp}*\n\nEstimado/a *${name}*, le enviamos la propuesta personalizada solicitada:\n\n💵 *Monto Solicitado:* $${c.amount.toLocaleString('es-AR')}\n🔢 *Plan de Pago:* ${this.quoteForm.installments_count} cuota(s) ${this.quoteForm.modality}s\n📊 *Tasa de Interés:* ${this.quoteForm.interest_rate}% (${this.quoteForm.rate_type})\n💰 *Valor por Cuota:* *$${c.installmentValue.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}*\n🏁 *Monto Total a Devolver:* $${c.totalToPay.toLocaleString('es-AR', {minimumFractionDigits: 2})}${aliasStr}\n\n📌 *Validez:* 7 días. Quedamos atentos para activar su mutuo y suscribir el contrato o Pagaré. ¡Muchas gracias!`;
                } else if (this.quoteForm.channel === 'email') {
                    return `Estimado/a ${name},\n\nLe hacemos llegar la propuesta formal de mutuo con interés solicitado a ${comp}:\n\n- Monto Solicitado: $${c.amount.toLocaleString('es-AR')}\n- Plan de Pago: ${this.quoteForm.installments_count} cuota(s) ${this.quoteForm.modality}s\n- Tasa de Interés: ${this.quoteForm.interest_rate}% (${this.quoteForm.rate_type})\n- Valor estimado por Cuota: $${c.installmentValue.toLocaleString('es-AR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}\n- Monto Total a Devolver: $${c.totalToPay.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n\nDatos de Transferencia Directa:\nAlias/CBU: ${this.settings.alias_cbu || 'Consultar'}\n\nPara confirmar y suscribir el contrato/pagaré, por favor responda a este correo o contáctenos vía WhatsApp.\n\nAtentamente,\n${comp}`;
                } else {
                    // SMS / Mensaje Común
                    return `Presupuesto ${comp} p/ ${name}: Monto $${c.amount.toLocaleString('es-AR')} en ${this.quoteForm.installments_count} cuotas de $${c.installmentValue.toFixed(2)} (${this.quoteForm.modality}s). Total: $${c.totalToPay.toFixed(2)}. Alias: ${this.settings.alias_cbu || ''}. Responda OK p/ confirmar.`;
                }
            },

            dispatchQuote() {
                let phone = (this.quoteForm.whatsapp || '').replace(/[^0-9]/g, '');
                const email = (this.quoteForm.email || '').trim();
                const text = this.generatedQuoteText;

                if (this.quoteForm.channel === 'whatsapp') {
                    if (!phone) {
                        alert("Ingrese un número de teléfono de WhatsApp válido.");
                        return;
                    }
                    const waUrl = `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
                    window.open(waUrl, '_blank');
                } else if (this.quoteForm.channel === 'email') {
                    if (!email) {
                        alert("Ingrese una dirección de email válida.");
                        return;
                    }
                    const subject = encodeURIComponent(`Presupuesto de Préstamo - ${this.settings.company_name || 'Familia Andrada'}`);
                    const mailtoUrl = `mailto:${email}?subject=${subject}&body=${encodeURIComponent(text)}`;
                    window.open(mailtoUrl, '_blank');
                } else if (this.quoteForm.channel === 'sms') {
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(text);
                        alert("📱 Texto del SMS copiado al portapapeles. ¡Listo para pegar en tu aplicación de mensajes!");
                    } else if (phone) {
                        window.open(`sms:${phone}?body=${encodeURIComponent(text)}`, '_blank');
                    } else {
                        alert("Texto del presupuesto listo.");
                    }
                }
            },

            openQuotePDF() {
                const params = new URLSearchParams({
                    client_name: this.quoteForm.client_name || 'Cliente Estimado/a',
                    whatsapp: this.quoteForm.whatsapp || '',
                    amount: this.quoteForm.amount,
                    installments: this.quoteForm.installments_count,
                    interest_rate: this.quoteForm.interest_rate,
                    rate_type: this.quoteForm.rate_type,
                    modality: this.quoteForm.modality
                });
                window.open(`/api/quote/pdf?${params.toString()}`, '_blank');
            },

            changeWhatsAppTone(newTone) {
                if (!this.activeWhatsapp || !this.activeWhatsapp.item) return;
                this.openWhatsAppModal(this.activeWhatsapp.currentType, this.activeWhatsapp.item, newTone);
            },

            sendWhatsApp() {
                window.open(this.activeWhatsapp.url, '_blank');
            },

            // Calendar & Exports
            addToGoogleCalendar(inst) {
                const dateStr = inst.due_date.replace(/-/g, '');
                const title = encodeURIComponent(`Cobro Cuota #${inst.number} - ${inst.client_name}`);
                const details = encodeURIComponent(`Cobrar cuota por valor de $${inst.amount}. Cliente: ${inst.client_name}`);
                const gcalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dateStr}/${dateStr}&details=${details}`;
                window.open(gcalUrl, '_blank');
            },

            exportCalendarICS() {
                window.location.href = '/api/calendar/ics';
            },

            downloadBackup() {
                window.location.href = '/api/backup/download';
            },

            async restoreBackup(event) {
                const file = event.target.files[0];
                if (!file) return;

                if (!confirm("⚠️ ¿Estás seguro de restaurar este archivo de respaldo?\n\nEsta operación reemplazará los datos actuales por los registrados en la copia de seguridad seleccionada.")) {
                    event.target.value = '';
                    return;
                }

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch('/api/backup/restore', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        alert(`✅ ¡Copia de seguridad restaurada correctamente!\n\nClientes: ${data.restored.clients}\nPréstamos: ${data.restored.loans}\nCobranzas: ${data.restored.payments}\nGastos: ${data.restored.expenses}`);
                        await this.loadAllData();
                    } else {
                        alert(`❌ Error al restaurar respaldo: ${data.error || 'Archivo inválido'}`);
                    }
                } catch (err) {
                    console.error(err);
                    alert("Error de conexión al subir la copia de seguridad.");
                } finally {
                    event.target.value = '';
                }
            },

            exportReportCSV() {
                window.location.href = '/api/reports/csv';
            },

            // Express Pagaré Virtual & QR Methods
            async openExpressPagareModal(presetClient = null) {
                if (!this.clients || this.clients.length === 0) {
                    await this.fetchClients();
                }

                if (!this.clients || this.clients.length === 0) {
                    alert("No hay clientes registrados en el sistema. Redirigiendo a registro de cliente...");
                    this.openNewClientModal();
                    return;
                }

                let clientId = '';
                let clientName = '';
                if (presetClient && presetClient.id) {
                    clientId = presetClient.id;
                    clientName = presetClient.name;
                } else if (this.clients.length > 0) {
                    clientId = this.clients[0].id;
                    clientName = this.clients[0].name;
                }

                const nextMonth = new Date();
                nextMonth.setMonth(nextMonth.getMonth() + 1);
                const returnDateStr = nextMonth.toISOString().split('T')[0];

                this.expressPagare = {
                    client_id: clientId,
                    client_name: clientName,
                    amount: 50000,
                    installments_count: 4,
                    interest_rate: 15,
                    modality: 'mensual',
                    return_date: returnDateStr,
                    notes: '',
                    token: '',
                    qr_img_url: '',
                    sign_url: '',
                    wa_url: ''
                };
                this.activeModal = 'expressPagareModal';

                if (clientId) {
                    this.$nextTick(async () => {
                        await this.createExpressPagareRequest();
                    });
                }
            },

            async createExpressPagareRequest() {
                if (!this.clients || this.clients.length === 0) return;
                
                if (!this.expressPagare.client_id && this.clients.length > 0) {
                    this.expressPagare.client_id = this.clients[0].id;
                }
                
                if (!this.expressPagare.amount || this.expressPagare.amount <= 0) {
                    this.expressPagare.amount = 50000;
                }

                const clientObj = this.clients.find(c => c.id == this.expressPagare.client_id) || this.clients[0];
                if (clientObj) {
                    this.expressPagare.client_name = clientObj.name;
                    this.expressPagare.client_id = clientObj.id;
                }

                try {
                    const res = await fetch('/api/biometric_requests', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            client_id: parseInt(this.expressPagare.client_id),
                            amount: parseFloat(this.expressPagare.amount),
                            installments_count: parseInt(this.expressPagare.installments_count || 4),
                            interest_rate: parseFloat(this.expressPagare.interest_rate || 15),
                            modality: this.expressPagare.modality || 'mensual',
                            return_date: this.expressPagare.return_date,
                            notes: this.expressPagare.notes
                        })
                    });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        this.expressPagare.token = data.token;
                        this.expressPagare.qr_img_url = data.qr_img_url;
                        this.expressPagare.sign_url = data.sign_url;
                        this.expressPagare.wa_url = data.wa_url;
                    } else {
                        console.error("Biometric request error:", data);
                    }
                } catch (err) {
                    console.error("Error creating biometric request:", err);
                }
            },

            copyBiometricLink() {
                if (!this.expressPagare.sign_url) return;
                navigator.clipboard.writeText(this.expressPagare.sign_url).then(() => {
                    alert("¡Enlace de firma y selfie copiado al portapapeles!");
                }).catch(() => {
                    prompt("Copia este enlace para enviarlo:", this.expressPagare.sign_url);
                });
            },

            installPwa() {
                if (this.deferredPwaPrompt) {
                    this.deferredPwaPrompt.prompt();
                    this.deferredPwaPrompt.userChoice.then((choiceResult) => {
                        if (choiceResult.outcome === 'accepted') {
                            this.isPwaInstalled = true;
                        }
                        this.deferredPwaPrompt = null;
                    });
                } else {
                    alert("Instalación PWA:\n• Android / Chrome: Toca el menú (⋮) y selecciona 'Instalar aplicación' o 'Agregar a la pantalla principal'.\n• iPhone / Safari: Toca el botón Compartir (⎋) y selecciona 'Agregar a inicio'.");
                }
            },

            // Expense Methods
            openNewExpenseModal() {
                this.expenseForm = {
                    category: 'Fijo',
                    description: '',
                    amount: '',
                    date: new Date().toISOString().split('T')[0],
                    is_ant_expense: false
                };
                this.activeModal = 'newExpense';
            },

            async saveExpense() {
                if (!this.expenseForm.description || !this.expenseForm.amount || this.expenseForm.amount <= 0) {
                    alert("Ingrese descripción y monto de gasto válido.");
                    return;
                }
                try {
                    const res = await fetch('/api/expenses', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.expenseForm)
                    });
                    if (res.ok) {
                        this.activeModal = null;
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al guardar gasto.");
                }
            },

            async deleteExpense(id) {
                const expenseId = typeof id === 'object' ? id.id : id;
                if (!expenseId) {
                    alert("Error: ID de gasto no válido.");
                    return;
                }
                if (!confirm("¿Confirma eliminar este gasto de la lista?")) return;
                try {
                    const res = await fetch(`/api/expenses/${expenseId}`, { method: 'DELETE' });
                    if (res.ok) {
                        this.expenses = (this.expenses || []).filter(e => e.id !== expenseId);
                        this.selectedExpenseIds = (this.selectedExpenseIds || []).filter(eid => eid !== expenseId);
                        await this.fetchExpenses();
                        await this.fetchStats();
                    } else {
                        const errData = await res.json().catch(() => ({}));
                        alert(errData.error || "Error al eliminar gasto del servidor.");
                    }
                } catch (err) {
                    console.error("deleteExpense error:", err);
                    alert("Error de conexión al eliminar el gasto.");
                }
            },

            // Expenses Bulk Selection & Delete
            toggleSelectAllExpenses() {
                if (this.selectAllExpenses) {
                    this.selectedExpenseIds = this.filteredExpenses.map(e => e.id);
                } else {
                    this.selectedExpenseIds = [];
                }
            },

            toggleSelectExpense(expId) {
                const idx = this.selectedExpenseIds.indexOf(expId);
                if (idx > -1) {
                    this.selectedExpenseIds.splice(idx, 1);
                } else {
                    this.selectedExpenseIds.push(expId);
                }
                this.selectAllExpenses = this.selectedExpenseIds.length === this.filteredExpenses.length && this.filteredExpenses.length > 0;
            },

            isExpenseSelected(expId) {
                return this.selectedExpenseIds.includes(expId);
            },

            async deleteSelectedExpenses() {
                if (this.selectedExpenseIds.length === 0) return;
                if (!confirm(`¿Estás seguro de eliminar los ${this.selectedExpenseIds.length} gastos seleccionados? Esta acción es irreversible.`)) return;
                try {
                    const items = this.selectedExpenseIds.map(id => ({ raw_type: 'Expense', id }));
                    const res = await fetch('/api/history/bulk_delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ items })
                    });
                    const data = await res.json();
                    if (data.success) {
                        this.expenses = (this.expenses || []).filter(e => !this.selectedExpenseIds.includes(e.id));
                        this.selectedExpenseIds = [];
                        this.selectAllExpenses = false;
                        await this.fetchExpenses();
                        await this.fetchStats();
                        alert(`Se eliminaron ${data.deleted_count} gastos.`);
                    }
                } catch (err) {
                    alert("Error al eliminar los gastos seleccionados.");
                }
            },

            async saveSettings() {
                try {
                    const res = await fetch('/api/settings', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.settings)
                    });
                    if (res.ok) {
                        alert("Ajustes guardados correctamente.");
                        await this.fetchSettings();
                        await this.fetchStats();
                    } else {
                        alert("Error al guardar los ajustes.");
                    }
                } catch (err) {
                    console.error("Error saving settings:", err);
                    alert("Error de conexión al guardar los ajustes.");
                }
            },

            // Personal Accounts & AI Tips Methods
            async fetchPersonalAccounts() {
                try {
                    const res = await fetch(`/api/personal_accounts?month=${this.selectedAccountMonth}&year=${this.selectedAccountYear}`);
                    const data = await res.json();
                    this.personalBills = data.bills || [];
                    if (!this.isEditingSalaries) {
                        this.salaryEduardo = data.salary_eduardo;
                        this.salaryMaira = data.salary_maira;
                    }
                    this.personalAccountsMetrics = data.metrics;
                    await this.fetchAiTips();
                    await this.fetchDolarRates();
                } catch (err) {
                    console.error("Error fetching personal accounts:", err);
                }
            },

            // Dollar Rates & Real-Time Calculator Methods
            async fetchDolarRates(force = false) {
                this.dolarLoading = true;
                try {
                    const res = await fetch(`/api/dolar-rates${force ? '?force=true' : ''}`);
                    const data = await res.json();
                    if (data.success && data.rates) {
                        this.dolarRates = data.rates;
                        this.dolarLastUpdated = data.last_updated;
                    }
                } catch (err) {
                    console.error("Error fetching dollar rates:", err);
                } finally {
                    this.dolarLoading = false;
                }
            },

            getSelectedDolarRate() {
                if (!this.dolarRates) return 1420;
                const type = this.selectedDolarType || 'oficial';
                const rateObj = this.dolarRates[type] || this.dolarRates['oficial'];
                if (!rateObj) return 1420;
                return rateObj.venta || rateObj.promedio || 1400;
            },

            get convertedArsAmount() {
                const usd = parseFloat(this.usdInput) || 0;
                const rate = this.getSelectedDolarRate();
                return Math.round(usd * rate);
            },

            get usdSalaryImpact() {
                const totalSalary = (parseFloat(this.salaryEduardo || 0) + parseFloat(this.salaryMaira || 0)) || 1;
                const totalArs = this.convertedArsAmount;
                return ((totalArs / totalSalary) * 100).toFixed(1);
            },

            quickSetUsd(amount) {
                this.usdInput = amount;
            },

            async addUsdAsBill() {
                const usd = parseFloat(this.usdInput) || 0;
                if (usd <= 0) return alert("Por favor ingresa un monto en dólares válido.");
                const rate = this.getSelectedDolarRate();
                const totalArs = Math.round(usd * rate);
                const rateName = this.dolarRates && this.dolarRates[this.selectedDolarType] ? this.dolarRates[this.selectedDolarType].nombre : 'Oficial BNA';
                
                this.billForm = {
                    id: null,
                    name: `Gasto en Dólares ($${usd} USD)`,
                    category: 'tarjeta',
                    owner: 'Compartido',
                    amount: totalArs,
                    due_day: 10,
                    status: 'pendiente',
                    notes: `Convertido de internet: $${usd} USD x $${rate} (${rateName})`,
                    month: this.selectedAccountMonth,
                    year: this.selectedAccountYear,
                    installments_count: 1,
                    current_installment: 1,
                    is_recurring: false
                };
                this.activeModal = 'billModal';
            },

            async changeAccountMonth(delta) {
                let m = this.selectedAccountMonth + delta;
                let y = this.selectedAccountYear;
                if (m < 1) {
                    m = 12;
                    y -= 1;
                } else if (m > 12) {
                    m = 1;
                    y += 1;
                }
                this.selectedAccountMonth = m;
                this.selectedAccountYear = y;
                await this.fetchPersonalAccounts();
            },

            async setAccountMonthYear(m, y) {
                this.selectedAccountMonth = parseInt(m);
                this.selectedAccountYear = parseInt(y);
                await this.fetchPersonalAccounts();
            },

            async fetchAiTips() {
                try {
                    const res = await fetch(`/api/personal_accounts/ai_analysis?month=${this.selectedAccountMonth}&year=${this.selectedAccountYear}`);
                    const data = await res.json();
                    this.aiTips = data.tips || [];
                    if (this.aiTips.length > 0 && this.currentAiTipIndex >= this.aiTips.length) {
                        this.currentAiTipIndex = 0;
                    }
                } catch (err) {
                    console.error("Error fetching AI tips:", err);
                }
            },

            nextAiTip() {
                if (!this.aiTips || this.aiTips.length === 0) return;
                this.currentAiTipIndex = (this.currentAiTipIndex + 1) % this.aiTips.length;
            },

            async askAiAdvisor(presetQuery) {
                const query = presetQuery || this.aiAdvisorQuery;
                if (!query || !query.trim()) return;
                this.isAiAdvisorLoading = true;
                this.aiAdvisorQuery = query;
                try {
                    const res = await fetch('/api/personal_accounts/ai_advisor_chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query: query,
                            month: this.selectedAccountMonth,
                            year: this.selectedAccountYear
                        })
                    });
                    const data = await res.json();
                    this.aiAdvisorResponse = data.reply;
                } catch (err) {
                    this.aiAdvisorResponse = "Error al consultar el Asesor IA. Por favor reintenta.";
                } finally {
                    this.isAiAdvisorLoading = false;
                }
            },

            async fetchHistorySummary() {
                try {
                    const res = await fetch('/api/personal_accounts/history_summary');
                    const data = await res.json();
                    this.historySummary = data.history || [];
                } catch (err) {
                    console.error("Error fetching history summary:", err);
                }
            },

            async clearPastHistory() {
                if (!confirm(`¿Seguro que deseas eliminar todas las cuentas registradas de meses pasados anteriores a ${this.monthNames[this.selectedAccountMonth]} ${this.selectedAccountYear}?`)) return;
                try {
                    const res = await fetch('/api/personal_accounts/clear_history', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            month: this.selectedAccountMonth,
                            year: this.selectedAccountYear
                        })
                    });
                    const data = await res.json();
                    alert(data.message || "Historial pasado eliminado correctamente.");
                    await this.fetchPersonalAccounts();
                    await this.fetchHistorySummary();
                } catch (err) {
                    alert("Error al borrar el historial de meses pasados.");
                }
            },

            async saveCoupleSalaries() {
                try {
                    const res = await fetch('/api/personal_accounts/salaries', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            salary_eduardo: parseFloat(this.salaryEduardo || 0),
                            salary_maira: parseFloat(this.salaryMaira || 0)
                        })
                    });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        this.isEditingSalaries = false;
                        this.salaryEduardo = data.salary_eduardo;
                        this.salaryMaira = data.salary_maira;
                        this.salarySavedMessage = "✅ ¡Sueldos del hogar guardados correctamente!";
                        setTimeout(() => { this.salarySavedMessage = ''; }, 3500);
                        await this.fetchPersonalAccounts();
                    } else {
                        alert("No se pudo guardar la configuración de sueldos.");
                    }
                } catch (err) {
                    alert("Error de conexión al actualizar los sueldos de la pareja.");
                }
            },

            openNewBillModal() {
                this.billForm = { 
                    id: null, 
                    name: '', 
                    category: 'tarjeta', 
                    owner: 'Compartido', 
                    amount: '', 
                    due_day: 10, 
                    status: 'pendiente', 
                    notes: '',
                    month: this.selectedAccountMonth,
                    year: this.selectedAccountYear,
                    installments_count: 1,
                    is_recurring: true
                };
                this.activeModal = 'newBill';
            },

            openEditBillModal(bill) {
                this.billForm = { 
                    owner: 'Compartido', 
                    month: this.selectedAccountMonth,
                    year: this.selectedAccountYear,
                    installments_count: 1,
                    is_recurring: true,
                    update_all: false,
                    ...bill 
                };
                this.activeModal = 'editBill';
            },

            async saveBill() {
                try {
                    const method = this.billForm.id ? 'PUT' : 'POST';
                    const url = this.billForm.id ? `/api/personal_accounts/${this.billForm.id}` : '/api/personal_accounts';
                    const res = await fetch(url, {
                        method: method,
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.billForm)
                    });
                    if (res.ok) {
                        this.activeModal = null;
                        await this.fetchPersonalAccounts();
                    } else {
                        const errData = await res.json().catch(() => ({}));
                        alert(errData.error || errData.message || "Error al guardar la cuenta.");
                    }
                } catch (err) {
                    alert("Error al conectar con el servidor.");
                }
            },

            async deleteBill(bill) {
                const id = typeof bill === 'object' ? bill.id : bill;
                const billObj = typeof bill === 'object' ? bill : (this.personalBills || []).find(b => b.id === id);
                const billName = billObj ? billObj.name : 'esta cuenta';

                let deleteAll = false;
                if (confirm(`¿Deseas eliminar "${billName}" de TODOS los meses registrados?\n\n• ACEPTAR: Eliminar la cuenta por completo de todos los meses.\n• CANCELAR: Ver opción para eliminar solo este mes.`)) {
                    deleteAll = true;
                } else if (confirm(`¿Deseas eliminar "${billName}" SOLO del mes actual (${this.monthNames[this.selectedAccountMonth]} ${this.selectedAccountYear})?`)) {
                    deleteAll = false;
                } else {
                    return; // Cancelled
                }

                try {
                    const res = await fetch(`/api/personal_accounts/${id}?delete_all=${deleteAll}`, { method: 'DELETE' });
                    if (res.ok) {
                        await this.fetchPersonalAccounts();
                    } else {
                        alert("Error al eliminar la cuenta.");
                    }
                } catch (err) {
                    alert("Error al conectar con el servidor.");
                }
            },

            async toggleBillPaid(billId) {
                try {
                    const res = await fetch(`/api/personal_accounts/${billId}/toggle_paid`, { method: 'POST' });
                    if (res.ok) {
                        await this.fetchPersonalAccounts();
                    }
                } catch (err) {
                    console.error("Error toggling bill status:", err);
                }
            },

            get filteredBills() {
                let list = this.personalBills;
                if (this.billOwnerFilter !== 'todos') {
                    list = list.filter(b => b.owner === this.billOwnerFilter);
                }
                if (this.billCategoryFilter === 'todos') return list;
                if (this.billCategoryFilter === 'pendientes') return list.filter(b => b.status === 'pendiente');
                if (this.billCategoryFilter === 'pagados') return list.filter(b => b.status === 'pagado');
                return list.filter(b => b.category === this.billCategoryFilter);
            },

            // Reactive Cashflow Computation
            get cashflowStats() {
                const totalInterest = this.stats.total_interest_collected || 0;
                const totalCapitalRec = this.stats.total_capital_recovered || 0;
                const totalExpenses = this.stats.total_expenses || 0;

                const projectedCollections = this.loans.reduce((acc, l) => acc + l.remaining_balance, 0);
                const netCashBalance = (totalInterest + totalCapitalRec) - totalExpenses;

                return {
                    netCashBalance: roundVal(netCashBalance),
                    projectedCollections: roundVal(projectedCollections),
                    projectedNetBalance: roundVal(netCashBalance + projectedCollections)
                };
            },

            async openCashflowDetailModal() {
                await this.fetchCashflowDetail();
                this.activeModal = 'cashflowDetail';
            },

            async fetchCashflowDetail() {
                try {
                    let url = '/api/cashflow/detail';
                    const params = new URLSearchParams();
                    if (this.selectedMonthFilter && this.selectedMonthFilter !== 'todos') {
                        params.append('month', this.selectedMonthFilter);
                    }
                    if (this.selectedYearFilter && this.selectedYearFilter !== 'todos') {
                        params.append('year', this.selectedYearFilter);
                    }
                    if (params.toString()) url += `?${params.toString()}`;

                    const res = await fetch(url);
                    if (res.ok) {
                        this.cashflowDetailData = await res.json();
                    }
                } catch (err) {
                    console.error("Error fetching cashflow detail:", err);
                }
            },

            // Reactive Simulator Computations
            get simCalculations() {
                const amount = parseFloat(this.sim.amount) || 0;
                const rate = parseFloat(this.sim.interestRate) || 0;
                const instCount = parseInt(this.sim.installments) || 1;
                
                let months = instCount;
                if (this.sim.modality === 'semanal') months = instCount / 4.0;
                if (this.sim.modality === 'quincenal') months = instCount / 2.0;
                if (this.sim.modality === 'pago_unico') months = 1.0;

                let totalInterest = 0;
                if (this.sim.rateType === 'directo') {
                    totalInterest = amount * (rate / 100.0);
                } else {
                    totalInterest = amount * (rate / 100.0) * Math.max(0.25, months);
                }

                const totalToPay = amount + totalInterest;
                const installmentValue = totalToPay / instCount;

                let daysInterval = 30;
                if (this.sim.modality === 'semanal') daysInterval = 7;
                if (this.sim.modality === 'quincenal') daysInterval = 15;

                const instsToBreakEven = Math.ceil(amount / Math.max(1, installmentValue));
                const totalDaysToBreakEven = instsToBreakEven * daysInterval;
                
                const breakEvenDateObj = new Date();
                breakEvenDateObj.setDate(breakEvenDateObj.getDate() + totalDaysToBreakEven);
                
                const roi = amount > 0 ? (totalInterest / amount) * 100.0 : 0;

                return {
                    totalInterest: totalInterest,
                    totalToPay: totalToPay,
                    installmentValue: installmentValue,
                    netGain: totalInterest,
                    breakEvenDate: breakEvenDateObj.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }),
                    breakEvenDays: totalDaysToBreakEven,
                    roi: roi.toFixed(1)
                };
            },

            // Quote Engine Computations
            get quoteCalculations() {
                const amount = parseFloat(this.quoteForm.amount) || 0;
                const rate = parseFloat(this.quoteForm.interest_rate) || 0;
                const instCount = parseInt(this.quoteForm.installments_count) || 1;
                
                let months = instCount;
                if (this.quoteForm.modality === 'semanal') months = instCount / 4.0;
                if (this.quoteForm.modality === 'quincenal') months = instCount / 2.0;
                if (this.quoteForm.modality === 'pago_unico') months = 1.0;

                let totalInterest = 0;
                if (this.quoteForm.rate_type === 'directo') {
                    totalInterest = amount * (rate / 100.0);
                } else {
                    totalInterest = amount * (rate / 100.0) * Math.max(0.25, months);
                }

                const totalToPay = amount + totalInterest;
                const installmentValue = instCount > 0 ? totalToPay / instCount : totalToPay;

                return {
                    amount: amount,
                    totalInterest: roundVal(totalInterest),
                    totalToPay: roundVal(totalToPay),
                    installmentValue: roundVal(installmentValue)
                };
            },

            get generatedQuoteText() {
                const c = this.quoteCalculations;
                const company = this.settings.company_name || 'Prestamos & Finanzas Familia Andrada';
                const alias = this.settings.alias_cbu || 'FAMILIA.ANDRADA.MP';
                const clientName = this.quoteForm.client_name || 'Cliente Estimado/a';
                const modalityLabel = this.quoteForm.modality === 'semanal' ? 'semanales' : (this.quoteForm.modality === 'quincenal' ? 'quincenales' : 'mensuales');

                if (this.quoteForm.channel === 'email') {
                    return `Estimado/a ${clientName},\n\n` +
                        `Le enviamos la cotización y propuesta de préstamo personalizada solicitada a través de ${company}:\n\n` +
                        `• Monto Solicitado: $${c.amount.toLocaleString('es-AR')}\n` +
                        `• Plan de Pago: ${this.quoteForm.installments_count} cuota(s) ${modalityLabel}\n` +
                        `• Tasa de Interés: ${this.quoteForm.interest_rate}% (${this.quoteForm.rate_type})\n` +
                        `• Valor Estimado por Cuota: $${c.installmentValue.toLocaleString('es-AR')}\n` +
                        `• Monto Total a Devolver: $${c.totalToPay.toLocaleString('es-AR')}\n\n` +
                        `Datos para transferencias / depósito:\n` +
                        `CBU / Alias: ${alias}\n\n` +
                        `Quedamos a su entera disposición para gestionar el desembolso.\n\n` +
                        `Saludos cordiales,\n${company}`;
                }

                if (this.quoteForm.channel === 'sms') {
                    return `PRESUPUESTO: ${company}. Solicitud $${c.amount.toLocaleString('es-AR')} en ${this.quoteForm.installments_count} cuotas de $${c.installmentValue.toLocaleString('es-AR')}. Total $${c.totalToPay.toLocaleString('es-AR')}. Alias: ${alias}`;
                }

                // Default WhatsApp Format
                return `📲 *PRESUPUESTO DE PRÉSTAMO PERSONAL*\n` +
                    `*${company}*\n` +
                    `----------------------------------------\n` +
                    `Hola *${clientName}*! A continuación te compartimos los detalles de tu propuesta de financiación personalizada:\n\n` +
                    `💵 *Monto Solicitado:* $${c.amount.toLocaleString('es-AR')}\n` +
                    `🗓️ *Plan de Pago:* ${this.quoteForm.installments_count} cuota(s) ${modalityLabel}\n` +
                    `📈 *Tasa de Interés:* ${this.quoteForm.interest_rate}% (${this.quoteForm.rate_type})\n` +
                    `💰 *Cuotas de:* *$${c.installmentValue.toLocaleString('es-AR')}*\n` +
                    `🏁 *Monto Total a Devolver:* $${c.totalToPay.toLocaleString('es-AR')}\n\n` +
                    `📌 *Alias/CBU para Transferencias:* ${alias}\n\n` +
                    `Quedamos a tu entera disposición para resolver cualquier duda o confirmar el otorgamiento inmediato. ¡Gracias por confiar en nosotros!`;
            },

            openQuoteModal(data = {}) {
                this.quoteForm = {
                    client_id: data.client_id || '',
                    client_name: data.client_name || 'Cliente Estimado/a',
                    whatsapp: data.whatsapp || '',
                    email: data.email || '',
                    channel: 'whatsapp',
                    amount: data.amount !== undefined ? data.amount : (this.sim.amount || 50000),
                    installments_count: data.installments !== undefined ? data.installments : (this.sim.installments || 4),
                    interest_rate: data.interestRate !== undefined ? data.interestRate : (this.sim.interestRate || 15),
                    rate_type: data.rateType || this.sim.rateType || 'mensual',
                    modality: data.modality || this.sim.modality || 'mensual'
                };
                this.activeModal = 'quoteModal';
            },

            onQuoteClientChange() {
                if (!this.quoteForm.client_id) {
                    this.quoteForm.client_name = 'Cliente Estimado/a';
                    this.quoteForm.whatsapp = '';
                    this.quoteForm.email = '';
                    return;
                }
                const found = this.clients.find(c => c.id == this.quoteForm.client_id);
                if (found) {
                    this.quoteForm.client_name = found.name;
                    this.quoteForm.whatsapp = found.whatsapp;
                    this.quoteForm.email = found.email || '';
                }
            },

            dispatchQuote() {
                const text = this.generatedQuoteText;
                const cleanPhone = (this.quoteForm.whatsapp || '').replace(/\D/g, '');

                if (this.quoteForm.channel === 'whatsapp') {
                    const phoneToUse = cleanPhone || '';
                    const url = phoneToUse ? `https://wa.me/${phoneToUse}?text=${encodeURIComponent(text)}` : `https://wa.me/?text=${encodeURIComponent(text)}`;
                    window.open(url, '_blank');
                    return;
                }

                if (this.quoteForm.channel === 'email') {
                    const targetEmail = this.quoteForm.email || '';
                    const subject = encodeURIComponent(`Presupuesto de Préstamo Personal - ${this.settings.company_name || 'Prestamos Familia Andrada'}`);
                    const body = encodeURIComponent(text);
                    window.open(`mailto:${targetEmail}?subject=${subject}&body=${body}`, '_self');
                    return;
                }

                if (this.quoteForm.channel === 'sms') {
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(text);
                        alert("Textos del presupuesto copiados al portapapeles para envío SMS.");
                    }
                    const phoneToUse = cleanPhone || '';
                    const smsUrl = phoneToUse ? `sms:${phoneToUse}?body=${encodeURIComponent(text)}` : `sms:?body=${encodeURIComponent(text)}`;
                    window.open(smsUrl, '_self');
                    return;
                }
            },

            // --------------------------------------------------
            // CAJAS DETAILS, PDF & WHATSAPP
            // --------------------------------------------------
            async openCajaDetailModal(cajaId) {
                try {
                    const res = await fetch(`/api/cajas/detail/${cajaId}`);
                    this.activeCajaDetail = await res.json();
                    this.activeModal = 'cajaDetail';
                } catch (err) {
                    console.error("Error fetching caja detail:", err);
                }
            },

            downloadCajaPdf(cajaId) {
                window.open(`/api/cajas/pdf/${cajaId}`, '_blank');
            },

            shareCajaWhatsapp(cajaId) {
                const comp = this.settings.company_name || 'Gestión Préstamos';
                let msg = "";
                if (cajaId === 1) {
                    msg = `📊 *RESUMEN CAJA 1: CAPITAL EN CALLE*\n🏢 ${comp}\n💰 *Capital Activo Pendiente:* $${this.stats.capital_en_calle.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n📌 Préstamos activos en cobro.\n🗓️ Fecha: ${new Date().toLocaleDateString()}`;
                } else if (cajaId === 2) {
                    msg = `📈 *RESUMEN CAJA 2: INTERESES & GANANCIAS*\n🏢 ${comp}\n💵 *Interés Cobrado:* $${this.stats.total_interest_collected.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n⏳ *Interés Pendiente a Cobrar:* $${this.stats.intereses_a_cobrar.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n🗓️ Fecha: ${new Date().toLocaleDateString()}`;
                } else {
                    const net = this.stats.ganancia_liquida_mes - this.stats.total_expenses;
                    msg = `🏦 *RESUMEN CAJA 3: GANANCIA LÍQUIDA Y BALANCE DEL MES*\n🏢 ${comp}\n💵 *Cobros de Interés del Mes:* $${this.stats.ganancia_liquida_mes.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n💸 *Gastos del Mes:* $${this.stats.total_expenses.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n📊 *Ganancia Neta Real:* $${net.toLocaleString('es-AR', {minimumFractionDigits: 2})}\n🗓️ Fecha: ${new Date().toLocaleDateString()}`;
                }
                const url = `https://wa.me/?text=${encodeURIComponent(msg)}`;
                window.open(url, '_blank');
            },

            // --------------------------------------------------
            // GENERAL DETAILED HISTORY & BULK DELETE
            // --------------------------------------------------
            async openGeneralHistoryModal() {
                await this.fetchGeneralHistory();
                this.activeModal = 'generalHistoryModal';
            },

            async fetchGeneralHistory() {
                try {
                    const params = new URLSearchParams();
                    if (this.historyMonthFilter && this.historyMonthFilter !== 'todos') params.append('month', this.historyMonthFilter);
                    if (this.historyYearFilter && this.historyYearFilter !== 'todos') params.append('year', this.historyYearFilter);
                    if (this.historyTypeFilter && this.historyTypeFilter !== 'todos') params.append('type', this.historyTypeFilter);

                    const res = await fetch(`/api/history/general?${params.toString()}`);
                    this.generalHistory = await res.json();
                    this.selectedHistoryItems = [];
                    this.selectAllHistory = false;
                } catch (err) {
                    console.error("Error fetching general history:", err);
                }
            },

            toggleSelectAllHistory() {
                if (this.selectAllHistory) {
                    this.selectedHistoryItems = this.generalHistory.map(item => ({ raw_type: item.raw_type, id: item.id, unique_key: item.unique_key }));
                } else {
                    this.selectedHistoryItems = [];
                }
            },

            toggleSelectHistoryItem(item) {
                const idx = this.selectedHistoryItems.findIndex(i => i.unique_key === item.unique_key);
                if (idx > -1) {
                    this.selectedHistoryItems.splice(idx, 1);
                } else {
                    this.selectedHistoryItems.push({ raw_type: item.raw_type, id: item.id, unique_key: item.unique_key });
                }
                this.selectAllHistory = this.selectedHistoryItems.length === this.generalHistory.length && this.generalHistory.length > 0;
            },

            isHistoryItemSelected(uniqueKey) {
                return this.selectedHistoryItems.some(i => i.unique_key === uniqueKey);
            },

            async deleteSelectedHistoryItems() {
                if (this.selectedHistoryItems.length === 0) {
                    alert("Por favor selecciona al menos un registro para eliminar.");
                    return;
                }
                if (!confirm(`¿Estás seguro de eliminar los ${this.selectedHistoryItems.length} registros seleccionados? Esta acción es irreversible.`)) {
                    return;
                }
                try {
                    const res = await fetch('/api/history/bulk_delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ items: this.selectedHistoryItems })
                    });
                    const data = await res.json();
                    if (data.success) {
                        alert(`Se eliminaron ${data.deleted_count} registros correctamente.`);
                        await this.loadAllData();
                        await this.fetchGeneralHistory();
                    }
                } catch (err) {
                    console.error("Error in bulk delete:", err);
                    alert("Ocurrió un error al eliminar los registros.");
                }
            },

            // --------------------------------------------------
            // SMART AI FINANCIAL ADVISOR BOT
            // --------------------------------------------------
            async openAiAdvisorModal() {
                await this.fetchAiAdvisorData();
                this.activeModal = 'aiAdvisorModal';
            },

            async fetchAiAdvisorData() {
                try {
                    const res = await fetch('/api/ai_financial_advisor');
                    const data = await res.json();
                    this.aiAdvisor = { ...this.aiAdvisor, ...data };
                } catch (err) {
                    console.error("Error fetching AI advisor data:", err);
                }
            },

            sendAiAdvisorQuestion(presetText = null) {
                const text = (presetText || this.aiAdvisor.userPrompt || '').trim();
                if (!text) return;

                this.aiAdvisor.chatMessages.push({ role: 'user', text });
                this.aiAdvisor.userPrompt = '';

                setTimeout(() => {
                    let reply = "";
                    const q = text.toLowerCase();

                    if (q.includes('no tocar') || q.includes('dinero') || q.includes('cuanto tocar') || q.includes('retirar')) {
                        reply = `🛡️ **Diagnóstico de Capital en Tiempo Real:**\n- **Capital INVIOLABLE (No tocar):** $${this.aiAdvisor.capital_inviolable.toLocaleString('es-AR', {minimumFractionDigits: 2})} (incluye capital en calle + 10% fondo de protección).\n- **Disponible para Retiro:** $${this.aiAdvisor.safe_withdrawable_amount.toLocaleString('es-AR', {minimumFractionDigits: 2})} (descontando 30% para reinversión).\n- **Reinversión aconsejada:** $${this.aiAdvisor.reinvestment_portion.toLocaleString('es-AR', {minimumFractionDigits: 2})}.`;
                    } else if (q.includes('gasto') || q.includes('hormiga') || q.includes('fuga')) {
                        reply = `🚨 **Radar de Gastos Hormiga:**\nTus gastos hormiga acumulados este mes suman **$${this.aiAdvisor.ant_expenses_month.toLocaleString('es-AR', {minimumFractionDigits: 2})}**.\n💡 *Consejo:* Configura alertas para compras menores a $2.500 y exige recibo para cada egreso extraordinario.`;
                    } else if (q.includes('invertir') || q.includes('prestamo') || q.includes('cliente')) {
                        if (this.aiAdvisor.mora_percentage > 10) {
                            reply = `⚠️ **Atención:** Tu tasa de mora actual es de ${this.aiAdvisor.mora_percentage}%. No es el momento de otorgar créditos riesgosos. Prioriza el cobro y recupero de cuotas vencidas.`;
                        } else {
                            reply = `📈 **Estrategia de Inversión:** Tu mora es baja (${this.aiAdvisor.mora_percentage}%). Se recomienda colocar créditos en modalidad quincenal con tasa mensual directa del 15% al 20% a clientes con Scoring 5 estrellas.`;
                        }
                    } else {
                        reply = `🤖 **Respuesta Financiera Personalizada:**\nBasado en tus métricas actuales (Ganancia Neta del mes: $${this.aiAdvisor.net_liquid_profit.toLocaleString('es-AR', {minimumFractionDigits: 2})}, Mora: ${this.aiAdvisor.mora_percentage}%):\n${this.aiAdvisor.recommendations.join('\n')}`;
                    }

                    this.aiAdvisor.chatMessages.push({ role: 'assistant', text: reply });
                }, 600);
            },

            // Filtered Collections
            get filteredClients() {
                if (!this.clientSearch) return this.clients;
                const q = this.clientSearch.toLowerCase();
                return this.clients.filter(c => 
                    c.name.toLowerCase().includes(q) || 
                    c.whatsapp.includes(q) || 
                    (c.email && c.email.toLowerCase().includes(q))
                );
            },

            get filteredLoans() {
                return this.loans.filter(l => {
                    const matchSearch = !this.loanSearch || 
                        l.client_name.toLowerCase().includes(this.loanSearch.toLowerCase()) || 
                        l.id.toString().includes(this.loanSearch);
                    const matchStatus = this.loanStatusFilter === 'todos' || l.status === this.loanStatusFilter;
                    
                    const lDate = new Date(l.start_date);
                    const matchMonth = this.selectedMonthFilter === 'todos' || (lDate.getMonth() + 1).toString() === this.selectedMonthFilter;
                    const matchYear = this.selectedYearFilter === 'todos' || lDate.getFullYear().toString() === this.selectedYearFilter;

                    return matchSearch && matchStatus && matchMonth && matchYear;
                });
            },

            // Reactive Filtered Expenses & Dynamic Net Profit
            get filteredExpenses() {
                return this.expenses.filter(e => {
                    const eDate = new Date(e.date);
                    const matchMonth = this.selectedExpenseMonthFilter === 'todos' || (eDate.getMonth() + 1).toString() === this.selectedExpenseMonthFilter;
                    const matchYear = this.selectedExpenseYearFilter === 'todos' || eDate.getFullYear().toString() === this.selectedExpenseYearFilter;
                    let matchCat = true;
                    if (this.selectedExpenseCategoryFilter === 'hormiga') {
                        matchCat = e.is_ant_expense;
                    } else if (this.selectedExpenseCategoryFilter !== 'todos') {
                        matchCat = e.category === this.selectedExpenseCategoryFilter;
                    }
                    return matchMonth && matchYear && matchCat;
                });
            },

            get filteredExpensesTotal() {
                return this.filteredExpenses.reduce((acc, e) => acc + (parseFloat(e.amount) || 0), 0);
            },

            get filteredExpensesNetProfit() {
                const interest = this.stats.ganancia_liquida_mes || 0;
                return interest - this.filteredExpensesTotal;
            },

            // Current Month Realtime Expenses for Dashboard
            get currentMonthExpenses() {
                const now = new Date();
                const m = now.getMonth() + 1;
                const y = now.getFullYear();
                return this.expenses.filter(e => {
                    const d = new Date(e.date);
                    return (d.getMonth() + 1) === m && d.getFullYear() === y;
                });
            },

            get currentMonthExpensesTotal() {
                return this.currentMonthExpenses.reduce((acc, e) => acc + (parseFloat(e.amount) || 0), 0);
            },

            get currentMonthAntExpensesTotal() {
                return this.currentMonthExpenses.filter(e => e.is_ant_expense).reduce((acc, e) => acc + (parseFloat(e.amount) || 0), 0);
            },

            get currentMonthNetProfit() {
                return (this.stats.ganancia_liquida_mes || 0) - this.currentMonthExpensesTotal;
            },

            // Pagaré Express QR & Biometric Request Methods
            async openExpressPagareModal(presetClientId = null) {
                if (!this.clients || this.clients.length === 0) {
                    await this.fetchClients();
                }

                const today = new Date();
                today.setMonth(today.getMonth() + 1);
                const defaultReturnDate = today.toISOString().split('T')[0];

                let targetClientId = presetClientId;
                if (!targetClientId && this.clients && this.clients.length > 0) {
                    targetClientId = this.clients[0].id;
                }

                this.expressPagare = {
                    client_id: targetClientId || '',
                    client_name: '',
                    amount: 50000,
                    installments_count: 4,
                    interest_rate: 15,
                    modality: 'mensual',
                    return_date: defaultReturnDate,
                    notes: '',
                    token: '',
                    qr_img_url: '',
                    sign_url: '',
                    wa_url: ''
                };

                this.activeModal = 'expressPagareModal';

                if (targetClientId) {
                    await this.createExpressPagareRequest();
                }
            },

            async createExpressPagareRequest() {
                if (!this.expressPagare.client_id) {
                    if (this.clients && this.clients.length > 0) {
                        this.expressPagare.client_id = this.clients[0].id;
                    } else {
                        return;
                    }
                }

                const selectedClient = this.clients.find(c => String(c.id) === String(this.expressPagare.client_id));
                if (selectedClient) {
                    this.expressPagare.client_name = selectedClient.name;
                }

                try {
                    const resp = await fetch('/api/biometric/request/create', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            client_id: this.expressPagare.client_id,
                            amount: this.expressPagare.amount || 50000,
                            installments_count: this.expressPagare.installments_count || 4,
                            interest_rate: this.expressPagare.interest_rate || 15,
                            return_date: this.expressPagare.return_date || ''
                        })
                    });
                    const data = await resp.json();
                    if (data.status === 'success') {
                        this.expressPagare.token = data.token;
                        this.expressPagare.sign_url = data.sign_url;
                        this.expressPagare.qr_img_url = data.qr_img_url;

                        const waText = encodeURIComponent(
                            `⚡ *Pagaré Virtual Express & Solicitud de Préstamo*\n\n` +
                            `Hola ${data.client_name},\n` +
                            `Ingresa al siguiente enlace para completar tu Firma Digital Biométrica (Firma en pantalla y Selfie):\n\n` +
                            `👉 ${data.sign_url}\n\n` +
                            `*Detalles:* $${Number(this.expressPagare.amount).toLocaleString('es-AR')} en ${this.expressPagare.installments_count} cuotas.\n` +
                            `_Este link expira automáticamente en 30 minutos por seguridad._`
                        );
                        const waPhone = selectedClient && selectedClient.whatsapp ? selectedClient.whatsapp.replace(/[^0-9]/g, '') : '';
                        this.expressPagare.wa_url = waPhone ? `https://wa.me/${waPhone}?text=${waText}` : `https://wa.me/?text=${waText}`;
                    }
                } catch (e) {
                    console.error("Error al crear solicitud de pagaré express:", e);
                }
            },

            copyBiometricLink() {
                if (!this.expressPagare.sign_url) return;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(this.expressPagare.sign_url).then(() => {
                        alert("¡Enlace de Firma Biométrica copiado al portapapeles! 📋");
                    }).catch(() => {
                        this.fallbackCopyText(this.expressPagare.sign_url);
                    });
                } else {
                    this.fallbackCopyText(this.expressPagare.sign_url);
                }
            },

            fallbackCopyText(text) {
                const input = document.createElement('input');
                input.value = text;
                document.body.appendChild(input);
                input.select();
                document.execCommand('copy');
                document.body.removeChild(input);
                alert("¡Enlace copiado al portapapeles! 📋");
            },

            // ============================================================
            // WEB AUDIO API SYNTHESIZER (2026 TENSION & FANFARE SOUNDS)
            // ============================================================
            playTensionSound() {
                try {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(60, ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 2.5);
                    gain.gain.setValueAtTime(0.15, ctx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 2.5);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 2.5);
                } catch(e) {}
            },

            playDrumroll() {
                try {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    let now = ctx.currentTime;
                    for (let i = 0; i < 20; i++) {
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'triangle';
                        osc.frequency.value = 120 + Math.random() * 40;
                        gain.gain.setValueAtTime(0.1, now);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.start(now);
                        osc.stop(now + 0.05);
                        now += 0.08 - (i * 0.003);
                    }
                } catch(e) {}
            },

            playFanfare() {
                try {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99]; // C E G C E G
                    notes.forEach((freq, idx) => {
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.value = freq;
                        const startTime = ctx.currentTime + idx * 0.12;
                        gain.gain.setValueAtTime(0.2, startTime);
                        gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.6);
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.start(startTime);
                        osc.stop(startTime + 0.6);
                    });
                } catch(e) {}
            },

            playScratchSound() {
                try {
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'square';
                    osc.frequency.value = 400 + Math.random() * 800;
                    gain.gain.setValueAtTime(0.05, ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.08);
                } catch(e) {}
            },

            triggerConfetti() {
                try {
                    const canvas = document.createElement('canvas');
                    canvas.style.position = 'fixed';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100vw';
                    canvas.style.height = '100vh';
                    canvas.style.pointerEvents = 'none';
                    canvas.style.zIndex = '9999';
                    document.body.appendChild(canvas);
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                    const ctx = canvas.getContext('2d');
                    const particles = Array.from({length: 80}, () => ({
                        x: canvas.width / 2,
                        y: canvas.height / 2,
                        vx: (Math.random() - 0.5) * 16,
                        vy: (Math.random() - 0.8) * 16,
                        color: ['#F59E0B', '#EF4444', '#10B981', '#6366F1', '#EC4899'][Math.floor(Math.random() * 5)],
                        size: Math.random() * 8 + 4
                    }));
                    let frame = 0;
                    const anim = () => {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        particles.forEach(p => {
                            p.x += p.vx;
                            p.y += p.vy;
                            p.vy += 0.3;
                            ctx.fillStyle = p.color;
                            ctx.beginPath();
                            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                            ctx.fill();
                        });
                        frame++;
                        if (frame < 75) requestAnimationFrame(anim);
                        else if (canvas.parentNode) document.body.removeChild(canvas);
                    };
                    anim();
                } catch(e) {}
            },

            // ============================================================
            // SORTEOS EXPRESS & RIFAS METHODS
            // ============================================================
            async fetchRaffles() {
                try {
                    const res = await fetch('/api/raffles');
                    const data = await res.json();
                    this.raffles = data.raffles || (Array.isArray(data) ? data : []);
                } catch(err) {
                    console.error("Error fetching raffles:", err);
                }
            },

            addPrizeToForm() {
                const nextRank = this.raffleForm.prizes.length + 1;
                this.raffleForm.prizes.push({ rank: nextRank, title: `${nextRank}° Premio` });
            },

            removePrizeFromForm(idx) {
                if (this.raffleForm.prizes.length > 1) {
                    this.raffleForm.prizes.splice(idx, 1);
                    this.raffleForm.prizes.forEach((p, i) => p.rank = i + 1);
                }
            },

            async createRaffle() {
                if (!this.raffleForm.title) {
                    alert("Ingrese un título para el sorteo.");
                    return;
                }
                try {
                    const payload = {
                        title: this.raffleForm.title,
                        motive: this.raffleForm.description || '',
                        description: this.raffleForm.description || '',
                        mode: this.raffleForm.mode || 'numbers',
                        range_min: Number(this.raffleForm.range_min || 1),
                        range_max: Number(this.raffleForm.range_max || 100),
                        number_min: Number(this.raffleForm.range_min || 1),
                        number_max: Number(this.raffleForm.range_max || 100),
                        names_list: this.raffleForm.names_list || '',
                        ticket_price: Number(this.raffleForm.ticket_price || 0),
                        prizes: this.raffleForm.prizes || []
                    };
                    const res = await fetch('/api/raffles', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        await this.fetchRaffles();
                        this.raffleForm = {
                            title: '', description: '', mode: 'numbers', range_min: 1, range_max: 100, custom_numbers: '', names_list: '', ticket_price: 1000, prizes: [{ rank: 1, title: '1° Premio: Asado Completo' }]
                        };
                        alert("¡Sorteo creado exitosamente! 🎉");
                    }
                } catch(err) {
                    alert("Error al crear sorteo");
                }
            },

            async deleteRaffle(id) {
                if (!confirm("¿Desea eliminar este sorteo?")) return;
                try {
                    await fetch(`/api/raffles/${id}`, { method: 'DELETE' });
                    await this.fetchRaffles();
                } catch(err) {
                    alert("Error al eliminar sorteo");
                }
            },

            async drawRaffle(raffle) {
                this.playTensionSound();
                this.playDrumroll();
                try {
                    const res = await fetch(`/api/raffles/${raffle.id}/draw`, { method: 'POST' });
                    const data = await res.json();
                    if (data.success || data.status === 'success') {
                        setTimeout(() => {
                            this.playFanfare();
                            this.triggerConfetti();
                            const winnerObj = (data.winners && data.winners[0]) || {};
                            this.goldenTicketModal = {
                                hash: winnerObj.verification_hash || winnerObj.hash || 'VERIFIED-HASH',
                                ticket_code: winnerObj.ticket_code || '001',
                                winner_name: winnerObj.winner_name || winnerObj.winner || 'Ganador',
                                raffle_title: raffle.title,
                                prize_title: winnerObj.prize_title || winnerObj.prize || '1° Premio'
                            };
                            this.fetchRaffles();
                        }, 2200);
                    }
                } catch(err) {
                    alert("Error al realizar sorteo");
                }
            },

            runSlotMachine(raffle) {
                if (this.slotState.spinning) return;
                this.slotState.spinning = true;
                this.playTensionSound();
                this.playDrumroll();

                const participants = raffle.mode === 'names'
                    ? (raffle.names_list ? raffle.names_list.split('\n').filter(n => n.trim()) : ['Ana', 'Carlos', 'Eduardo', 'Maira'])
                    : Array.from({length: Math.min(50, (raffle.range_max || raffle.number_max || 100) - (raffle.range_min || raffle.number_min || 1) + 1)}, (_, i) => String((raffle.range_min || raffle.number_min || 1) + i).padStart(2, '0'));

                let count = 0;
                const interval = setInterval(() => {
                    this.slotState.reels = [
                        participants[Math.floor(Math.random() * participants.length)],
                        participants[Math.floor(Math.random() * participants.length)],
                        participants[Math.floor(Math.random() * participants.length)]
                    ];
                    count++;
                    if (count > 25) {
                        clearInterval(interval);
                        this.drawRaffle(raffle);
                        this.slotState.spinning = false;
                    }
                }, 80);
            },

            initScratchCanvas(raffle) {
                this.$nextTick(() => {
                    const canvas = document.getElementById(`scratchCanvas_${raffle.id}`);
                    if (!canvas) return;
                    const ctx = canvas.getContext('2d');
                    canvas.width = 300;
                    canvas.height = 300;

                    ctx.fillStyle = '#94A3B8';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = '#1E293B';
                    ctx.font = 'bold 16px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('¡RASPA AQUÍ!', 150, 150);

                    let isDrawing = false;
                    const scratch = (x, y) => {
                        ctx.globalCompositeOperation = 'destination-out';
                        ctx.beginPath();
                        ctx.arc(x, y, 22, 0, Math.PI * 2);
                        ctx.fill();
                        this.playScratchSound();
                    };

                    canvas.onmousedown = (e) => { isDrawing = true; const r = canvas.getBoundingClientRect(); scratch(e.clientX - r.left, e.clientY - r.top); };
                    canvas.onmousemove = (e) => { if (isDrawing) { const r = canvas.getBoundingClientRect(); scratch(e.clientX - r.left, e.clientY - r.top); } };
                    canvas.onmouseup = () => { isDrawing = false; };
                    canvas.ontouchstart = (e) => { isDrawing = true; const r = canvas.getBoundingClientRect(); const t = e.touches[0]; scratch(t.clientX - r.left, t.clientY - r.top); };
                    canvas.ontouchmove = (e) => { if (isDrawing) { const r = canvas.getBoundingClientRect(); const t = e.touches[0]; scratch(t.clientX - r.left, t.clientY - r.top); } };
                    canvas.ontouchend = () => { isDrawing = false; };
                });
            },

            async openFlyerModal(raffle, useAi = false) {
                const aiParam = useAi ? '&use_ai=1' : '';
                const seed = Math.floor(Math.random() * 1000000);
                this.flyerModal = { open: true, imgUrl: `/api/generar-flyer?raffle_id=${raffle.id}${aiParam}&seed=${seed}&style=random`, raffleTitle: raffle.title };
            },

            randomizeFlyerStyle() {
                if (!this.flyerModal || !this.flyerModal.imgUrl) return;
                const seed = Math.floor(Math.random() * 1000000);
                const baseUrl = this.flyerModal.imgUrl.split('&seed=')[0];
                this.flyerModal.imgUrl = `${baseUrl}&seed=${seed}&style=random`;
            },

            generateBingoCardsPdf(raffle) {
                const seed = Math.floor(Math.random() * 1000000);
                const url = `/api/generar-cartones-bingo?title=${encodeURIComponent(raffle.title)}&mode=${raffle.mode === 'bingo' ? '75' : '90'}&count=4&seed=${seed}&style=random`;
                window.open(url, '_blank');
            },

            generateQuickBingoPdf(mode = '75') {
                const title = prompt("Título para los Cartones de Bingo (Canva / Pinterest):", "GRAN BINGO FAMILIAR 2026");
                if (!title) return;
                const seed = Math.floor(Math.random() * 1000000);
                const url = `/api/generar-cartones-bingo?title=${encodeURIComponent(title)}&mode=${mode}&count=4&seed=${seed}&style=random`;
                window.open(url, '_blank');
            },

            generateQuickFlyer() {
                const title = prompt("Título para el Flyer Promocional (Canva / Pinterest):", "GRAN SORTEO Y RIFA FAMILIAR");
                if (!title) return;
                const seed = Math.floor(Math.random() * 1000000);
                this.flyerModal = {
                    open: true,
                    imgUrl: `/api/generar-flyer?title=${encodeURIComponent(title)}&motive=Beneficio+Familiar+2026&ticket_price=1500&number_min=1&number_max=100&seed=${seed}&style=random`,
                    raffleTitle: title
                };
            },

            addIngredientToForm() {
                if (!this.comidasForm.bought_items) this.comidasForm.bought_items = [];
                this.comidasForm.bought_items.push({ name: '', cost: 0 });
            },

            removeIngredientFromForm(idx) {
                if (this.comidasForm.bought_items && this.comidasForm.bought_items.length > 0) {
                    this.comidasForm.bought_items.splice(idx, 1);
                }
            },

            async calculateComidas() {
                try {
                    const res = await fetch('/api/comidas/calculate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.comidasForm)
                    });
                    const data = await res.json();
                    if (data.status === 'success' || data.success) {
                        this.comidasResult = data.data || data.calculation;
                        this.asadoResult = data.data || data.calculation;
                    }
                } catch(err) {
                    alert("Error al calcular menú gastronómico");
                }
            },

            async calculateAsado() {
                return this.calculateComidas();
            },

            copyComidasWhatsapp() {
                const text = this.comidasResult?.wa_share_string || this.asadoResult?.wa_share_string;
                if (!text) return;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        alert("¡Resumen de Juntada IA copiado para WhatsApp! 🍽️📲");
                    }).catch(() => {
                        this.fallbackCopyText(text);
                    });
                } else {
                    this.fallbackCopyText(text);
                }
            },

            copyAsadoWhatsapp() {
                return this.copyComidasWhatsapp();
            },

            downloadComidasPdf() {
                if (!this.comidasResult) {
                    alert("Primero realiza el cálculo de comensales.");
                    return;
                }
                const query = new URLSearchParams({
                    people: this.comidasResult.people || 10,
                    total_cost: this.comidasResult.total_cost || 0,
                    per_person_cost: this.comidasResult.per_person_cost || 0,
                    menu_name: this.comidasResult.menu_name || "Evento Gastronómico"
                }).toString();
                window.open(`/api/comidas/pdf?${query}`, '_blank');
            },

            // ============================================================
            // GESTIÓN DE COMPRAS & HOGAR METHODS
            // ============================================================
            async fetchShoppingItems() {
                try {
                    const res = await fetch('/api/shopping');
                    const data = await res.json();
                    this.shoppingItems = data.items || (Array.isArray(data) ? data : []);
                } catch(err) {
                    console.error("Error fetching shopping items:", err);
                }
            },

            async createShoppingItem() {
                if (!this.shoppingForm.name) {
                    alert("Ingrese un nombre de producto.");
                    return;
                }
                try {
                    const res = await fetch('/api/shopping', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            store_category: (this.shoppingForm.category || 'supermercado').toLowerCase(),
                            item_name: this.shoppingForm.name,
                            quantity: this.shoppingForm.quantity || '1',
                            is_checked: false
                        })
                    });
                    if (res.ok) {
                        this.shoppingForm.name = '';
                        this.shoppingForm.quantity = '1';
                        await this.fetchShoppingItems();
                    }
                } catch(err) {
                    alert("Error al agregar ítem");
                }
            },

            async toggleShoppingItem(id) {
                try {
                    await fetch(`/api/shopping/${id}/toggle`, { method: 'POST' });
                    await this.fetchShoppingItems();
                } catch(err) {
                    alert("Error al actualizar ítem");
                }
            },

            async deleteShoppingItem(id) {
                try {
                    await fetch(`/api/shopping/${id}`, { method: 'DELETE' });
                    await this.fetchShoppingItems();
                } catch(err) {
                    alert("Error al eliminar ítem");
                }
            },

            async fetchNotices() {
                try {
                    const res = await fetch('/api/noticeboard');
                    const data = await res.json();
                    this.noticeItems = data.notices || (Array.isArray(data) ? data : []);
                } catch(err) {
                    console.error("Error fetching notices:", err);
                }
            },

            async createNotice() {
                if (!this.noticeForm.title && !this.noticeForm.content) {
                    alert("Ingrese título o contenido para la nota.");
                    return;
                }
                try {
                    const res = await fetch('/api/noticeboard', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            author: this.noticeForm.title || 'Familia',
                            message: this.noticeForm.content || this.noticeForm.title || '',
                            is_pinned: Boolean(this.noticeForm.is_pinned)
                        })
                    });
                    if (res.ok) {
                        this.noticeForm = { title: '', content: '', color: 'yellow', is_pinned: false };
                        await this.fetchNotices();
                    }
                } catch(err) {
                    alert("Error al crear nota");
                }
            },

            async deleteNotice(id) {
                try {
                    await fetch(`/api/noticeboard/${id}`, { method: 'DELETE' });
                    await this.fetchNotices();
                } catch(err) {
                    alert("Error al eliminar nota");
                }
            },

            async fetchCalendarEvents() {
                try {
                    const res = await fetch('/api/home-calendar');
                    const data = await res.json();
                    this.calendarItems = data.events || (Array.isArray(data) ? data : []);
                } catch(err) {
                    console.error("Error fetching calendar events:", err);
                }
            },

            async createCalendarEvent() {
                if (!this.calendarForm.title || !this.calendarForm.event_date) {
                    alert("Ingrese título y fecha del evento.");
                    return;
                }
                try {
                    const res = await fetch('/api/home-calendar', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: this.calendarForm.title,
                            category: this.calendarForm.category || 'servicios',
                            due_date: this.calendarForm.event_date
                        })
                    });
                    if (res.ok) {
                        this.calendarForm = { event_date: new Date().toISOString().split('T')[0], title: '', category: 'servicios', notes: '' };
                        await this.fetchCalendarEvents();
                    }
                } catch(err) {
                    alert("Error al crear evento de calendario");
                }
            },

            async deleteCalendarEvent(id) {
                try {
                    await fetch(`/api/home-calendar/${id}`, { method: 'DELETE' });
                    await this.fetchCalendarEvents();
                } catch(err) {
                    alert("Error al eliminar evento");
                }
            },

            async fetchCatamarcaWeather() {
                try {
                    const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=-28.4696&longitude=-65.7852&current_weather=true');
                    const data = await res.json();
                    if (data && data.current_weather) {
                        const temp = Math.round(data.current_weather.temperature);
                        const code = data.current_weather.weathercode;
                        let cond = 'Despejado';
                        let icon = '☀️';
                        if (code >= 1 && code <= 3) { cond = 'Parcialmente Nublado'; icon = '⛅'; }
                        else if (code >= 45 && code <= 48) { cond = 'Niebla'; icon = '🌫️'; }
                        else if (code >= 51 && code <= 82) { cond = 'Lluvia'; icon = '🌧️'; }
                        else if (code >= 95) { cond = 'Tormenta'; icon = '⛈️'; }
                        this.catamarcaWeather = {
                            temp: `${temp}°C`,
                            condition: cond,
                            icon: icon
                        };
                    }
                } catch(err) {
                    this.catamarcaWeather = { temp: '24°C', condition: 'Catamarca (Despejado)', icon: '☀️' };
                }
            },

            startMarqueeClock() {
                const updateStr = () => {
                    const now = new Date();
                    const optionsDate = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
                    let dateStr = now.toLocaleDateString('es-AR', optionsDate);
                    dateStr = dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
                    const timeStr = now.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' hs';
                    this.currentDateStr = dateStr;
                    this.currentTimeStr = timeStr;
                    this.currentDateTimeStr = `${dateStr} | 🕒 ${timeStr}`;
                };
                updateStr();
                setInterval(updateStr, 1000);
            },

            async parseZeroUiAudio() {
                if (!this.zeroUiText.trim()) return;
                this.isZeroUiProcessing = true;
                try {
                    const res = await fetch('/api/hogar/parse-audio', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ audio_text: this.zeroUiText, raw_text: this.zeroUiText })
                    });
                    const data = await res.json();
                    if (data.status === 'success' || data.success) {
                        this.zeroUiResult = data.result || data.created_items;
                        this.zeroUiText = '';
                        await Promise.all([
                            this.fetchShoppingItems(),
                            this.fetchNotices(),
                            this.fetchCalendarEvents()
                        ]);
                    }
                } catch(err) {
                    alert("Error procesando audio/texto");
                } finally {
                    this.isZeroUiProcessing = false;
                }
            },

            addIngredientToForm(category = 'alimentos') {
                if (!this.comidasForm.bought_items) this.comidasForm.bought_items = [];
                this.comidasForm.bought_items.push({ name: '', price: 0, category: category });
            },

            removeIngredientFromForm(index) {
                if (this.comidasForm.bought_items) {
                    this.comidasForm.bought_items.splice(index, 1);
                    this.calculateComidas();
                }
            },

            handleTicketPhotoUpload(event) {
                const files = event.target.files;
                if (!files || !files.length) return;
                if (!this.comidasForm.ticket_images) this.comidasForm.ticket_images = [];
                
                Array.from(files).forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            this.comidasForm.ticket_images.push(e.target.result);
                        };
                        reader.readAsDataURL(file);
                    }
                });
            },

            removeTicketPhoto(index) {
                if (this.comidasForm.ticket_images) {
                    this.comidasForm.ticket_images.splice(index, 1);
                }
            },

            async calculateComidas() {
                try {
                    const payload = {
                        ...this.comidasForm,
                        menu_type: this.comidasForm.menu_type || this.comidasForm.event_type || 'asado',
                        bought_items: this.comidasForm.bought_items || []
                    };
                    const res = await fetch('/api/comidas/calculate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    if (data.status === 'success' || data.success) {
                        const resData = data.data || data.calculation || {};
                        this.comidasResult = {
                            ...resData,
                            menu_name: resData.menu_name || 'Juntada Gastronómica',
                            people: resData.people || this.comidasForm.people,
                            total_expense: resData.total_cost || resData.total_expense || 0,
                            cost_per_person: resData.per_person_cost || resData.estimated_cost_per_person || 0,
                            ingredients: resData.ingredients || [],
                            whatsapp_message: resData.wa_share_string || resData.whatsapp_text || ''
                        };
                    }
                } catch(err) {
                    console.error("Error calculando comidas", err);
                }
            },

            copyComidasWhatsapp() {
                const msg = this.comidasResult?.whatsapp_message || this.comidasResult?.wa_share_string;
                if (!msg) return;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(msg).then(() => {
                        alert("¡Mensaje IA copiado para WhatsApp! 📲");
                    }).catch(() => {
                        this.fallbackCopyText(msg);
                    });
                } else {
                    this.fallbackCopyText(msg);
                }
            },

            async downloadComidasPdf() {
                try {
                    const payload = {
                        people: this.comidasResult?.people || this.comidasForm.people,
                        total_cost: this.comidasResult?.total_expense || this.comidasResult?.total_cost || 0,
                        per_person_cost: this.comidasResult?.cost_per_person || this.comidasResult?.per_person_cost || 0,
                        menu_name: this.comidasResult?.menu_name || 'Comprobante de Juntada',
                        bought_items: this.comidasForm.bought_items || [],
                        ticket_images: this.comidasForm.ticket_images || []
                    };
                    const res = await fetch('/api/comidas/pdf', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `comprobante_juntada_${Date.now()}.png`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        window.URL.revokeObjectURL(url);
                    } else {
                        alert("Error al generar comprobante PDF/PNG");
                    }
                } catch(err) {
                    alert("Error descargando comprobante: " + err);
                }
            },

            async calculateAsado() {
                return this.calculateComidas();
            },

            copyAsadoWhatsapp() {
                return this.copyComidasWhatsapp();
            },

            // Universal Converter Methods (Mobile-First 2026)
            selectConverterCategory(cat) {
                this.converterCategory = cat;
                if (cat === 'doc') this.converterForm.targetFormat = 'docx';
                else if (cat === 'spreadsheet') this.converterForm.targetFormat = 'xlsx';
                else if (cat === 'image') this.converterForm.targetFormat = 'png';
                else if (cat === 'audio') this.converterForm.targetFormat = 'txt';
                else if (cat === 'archive') this.converterForm.targetFormat = 'zip';
            },

            async startAudioRecording() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.converterForm.mediaRecorder = new MediaRecorder(stream);
                    this.converterForm.audioChunks = [];
                    this.converterForm.isRecording = true;
                    this.converterForm.recordingTime = 0;
                    this.converterForm.statusText = 'Grabando micrófono nativo...';

                    this.converterForm.recordingTimer = setInterval(() => {
                        this.converterForm.recordingTime++;
                    }, 1000);

                    this.converterForm.mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) this.converterForm.audioChunks.push(e.data);
                    };

                    this.converterForm.mediaRecorder.onstop = () => {
                        clearInterval(this.converterForm.recordingTimer);
                        this.converterForm.audioBlob = new Blob(this.converterForm.audioChunks, { type: 'audio/wav' });
                        this.converterForm.isRecording = false;
                        this.converterForm.statusText = `Audio grabado (${this.converterForm.recordingTime}s). Listo para transcribir.`;
                        stream.getTracks().forEach(track => track.stop());
                    };

                    this.converterForm.mediaRecorder.start();
                } catch (err) {
                    alert("No se pudo acceder al micrófono: " + err.message);
                }
            },

            stopAudioRecording() {
                if (this.converterForm.mediaRecorder && this.converterForm.isRecording) {
                    this.converterForm.mediaRecorder.stop();
                }
            },

            async submitConversion(fileInputId = 'converterFileInput') {
                const fileInput = document.getElementById(fileInputId);
                let files = fileInput ? Array.from(fileInput.files) : [];
                
                if (this.converterCategory === 'audio' && this.converterForm.audioBlob) {
                    const recordedFile = new File([this.converterForm.audioBlob], `dictado_voz_${Date.now()}.wav`, { type: 'audio/wav' });
                    files = [recordedFile];
                }

                if (files.length === 0) {
                    alert("Por favor selecciona un archivo, toma una foto o graba un audio.");
                    return;
                }

                this.converterForm.isConverting = true;
                this.converterForm.statusText = 'Procesando conversión en RAM...';

                const formData = new FormData();
                files.forEach(f => formData.append('files', f));
                formData.append('file', files[0]);
                formData.append('target_format', this.converterForm.targetFormat);
                formData.append('is_ocr', this.converterForm.isOcr ? 'true' : 'false');

                let endpoint = '/api/convert/doc';
                if (this.converterCategory === 'spreadsheet') endpoint = '/api/convert/spreadsheet';
                else if (this.converterCategory === 'image') endpoint = '/api/convert/image';
                else if (this.converterCategory === 'audio') endpoint = '/api/convert/audio';
                else if (this.converterCategory === 'archive') endpoint = '/api/convert/archive';

                try {
                    const res = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });

                    if (res.ok) {
                        const blob = await res.blob();
                        const disposition = res.headers.get('Content-Disposition');
                        let filename = 'convertido';
                        if (disposition && disposition.includes('filename=')) {
                            filename = disposition.split('filename=')[1].replace(/"/g, '').trim();
                        }
                        
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        window.URL.revokeObjectURL(url);
                        
                        this.converterForm.statusText = '¡Conversión exitosa y descargada!';
                    } else {
                        const errJson = await res.json().catch(() => ({}));
                        alert("Error en conversión: " + (errJson.message || 'Fallo de procesamiento'));
                        this.converterForm.statusText = 'Error en la conversión.';
                    }
                } catch (err) {
                    alert("Error enviando conversión: " + err);
                    this.converterForm.statusText = 'Error de conexión.';
                } finally {
                    this.converterForm.isConverting = false;
                }
            },

            triggerCameraOcr() {
                this.selectConverterCategory('image');
                this.converterForm.targetFormat = 'docx';
                this.converterForm.isOcr = true;
                const camInput = document.getElementById('cameraOcrInput');
                if (camInput) camInput.click();
            },

            triggerDictaphone() {
                this.selectConverterCategory('audio');
                this.converterForm.targetFormat = 'docx';
                this.startAudioRecording();
            },

            triggerHeicConverter() {
                this.selectConverterCategory('image');
                this.converterForm.targetFormat = 'jpg';
                this.converterForm.isOcr = false;
                const imgInput = document.getElementById('converterFileInput');
                if (imgInput) imgInput.click();
            },

            triggerPdfMerger() {
                this.selectConverterCategory('image');
                this.converterForm.targetFormat = 'pdf';
                this.converterForm.isOcr = false;
                const imgInput = document.getElementById('converterFileInput');
                if (imgInput) imgInput.click();
            },


            // Chart.js Rendering
            renderCharts() {
                if (typeof Chart === 'undefined') return;
                const isDark = document.documentElement.classList.contains('dark');
                const textColor = isDark ? '#F3F4F6' : '#1F2937';

                // Expenses Doughnut Chart
                const expCtx = document.getElementById('expenseDoughnutChart');
                if (expCtx) {
                    if (this.expenseChart) this.expenseChart.destroy();
                    this.expenseChart = new Chart(expCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Fijo', 'Variable', 'Extraordinario'],
                            datasets: [{
                                data: [
                                    this.stats.expenses_by_cat.Fijo || 0,
                                    this.stats.expenses_by_cat.Variable || 0,
                                    this.stats.expenses_by_cat.Extraordinario || 0
                                ],
                                backgroundColor: ['#6366F1', '#3B82F6', '#EC4899'],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom', labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 11 } } }
                            }
                        }
                    });
                }

                // Capital Recovery Bar Chart
                const recCtx = document.getElementById('recoveryBarChart');
                if (recCtx) {
                    if (this.recoveryChart) this.recoveryChart.destroy();
                    this.recoveryChart = new Chart(recCtx, {
                        type: 'bar',
                        data: {
                            labels: ['En Calle', 'Recuperado', 'Interés Netos'],
                            datasets: [{
                                label: 'Monto ($)',
                                data: [
                                    this.stats.deployed_capital,
                                    this.stats.total_capital_recovered,
                                    this.stats.total_interest_collected
                                ],
                                backgroundColor: ['#F59E0B', '#10B981', '#6366F1'],
                                borderRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { display: false }
                            },
                            scales: {
                                x: { ticks: { color: textColor, font: { size: 10 } } },
                                y: { ticks: { color: textColor, font: { size: 10 } } }
                            }
                        }
                    });
                }
            },

            // ==========================================
            // REGISTRO REMOTO DE CLIENTES QR
            // ==========================================
            clientRegistrationRequests: [],
            clientRegistrationQrData: null,
            showClientQrRegistrationModal: false,
            activeClientSubTab: 'lista',
            clientRegistrationCopied: false,

            async generateClientRegistrationQr() {
                this.showClientQrRegistrationModal = true;
                this.clientRegistrationQrData = null;
                this.clientRegistrationCopied = false;
                try {
                    const res = await fetch('/api/client_registration_requests', { method: 'POST' });
                    if (!res.ok) {
                        let errDetail = `Error HTTP ${res.status}`;
                        try {
                            const errJson = await res.json();
                            if (errJson.error) errDetail = errJson.error;
                        } catch(e) {
                            if (res.status === 404) {
                                errDetail = "Servicio no disponible (404). Por favor reinicia el servidor local para activar las nuevas rutas.";
                            }
                        }
                        alert("Error al generar QR de registro: " + errDetail);
                        this.showClientQrRegistrationModal = false;
                        return;
                    }
                    const data = await res.json();
                    if (data.success) {
                        this.clientRegistrationQrData = data;
                        await this.fetchClientRegistrationRequests();
                    } else {
                        alert("Error al generar QR de registro: " + (data.error || "No se pudo generar"));
                        this.showClientQrRegistrationModal = false;
                    }
                } catch(e) {
                    alert("Error al generar QR de registro: " + e.message);
                    this.showClientQrRegistrationModal = false;
                }
            },

            copyClientRegistrationUrl() {
                if (!this.clientRegistrationQrData || !this.clientRegistrationQrData.sign_url) return;
                const text = this.clientRegistrationQrData.sign_url;
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        this.clientRegistrationCopied = true;
                        setTimeout(() => { this.clientRegistrationCopied = false; }, 2500);
                    }).catch(() => {
                        prompt("Copia este enlace de registro:", text);
                    });
                } else {
                    prompt("Copia este enlace de registro:", text);
                }
            },

            closeClientQrRegistrationModal() {
                this.showClientQrRegistrationModal = false;
                this.clientRegistrationQrData = null;
                this.clientRegistrationCopied = false;
            },

            async fetchClientRegistrationRequests() {
                try {
                    const res = await fetch('/api/client_registration_requests');
                    if (res.ok) {
                        this.clientRegistrationRequests = await res.json();
                    }
                } catch(e) {
                    console.error("Error al obtener solicitudes de registro:", e);
                }
            },

            async approveClientRegistration(req) {
                if (!req || !req.token) return;
                if (!confirm(`¿Confirmas la APROBACIÓN del registro del cliente ${req.name}?`)) return;
                try {
                    const res = await fetch(`/api/client_registration_requests/${req.token}/approve`, { method: 'POST' });
                    const data = await res.json();
                    if (data.success) {
                        alert("✅ Cliente APROBADO y REGISTRADO exitosamente.");
                        if (data.wa_url) {
                            window.open(data.wa_url, '_blank');
                        }
                        await this.fetchClientRegistrationRequests();
                        await this.fetchClients();
                    } else {
                        alert(data.error || "Error al aprobar el registro.");
                    }
                } catch(e) {
                    alert("Error al conectar con el servidor: " + e.message);
                }
            },

            async deleteClientRegistrationRequest(req) {
                if (!req || !req.token) return;
                if (!confirm("¿Eliminar/Rechazar esta solicitud de registro de cliente?")) return;
                try {
                    await fetch(`/api/client_registration_requests/${req.token}`, { method: 'DELETE' });
                    await this.fetchClientRegistrationRequests();
                } catch(e) {
                    alert("Error al eliminar solicitud: " + e.message);
                }
            },

            // ==========================================
            // CONTADOR VIRTUAL IA & ARQUEO DE CAJA
            // ==========================================
            showAiContadorModal: false,
            aiContadorTab: 'balance',
            aiContadorData: null,
            aiContadorQuery: '',
            aiContadorMessages: [],
            selectedAiContadorClient: null,

            async openAiContadorModal(clientObj = null) {
                this.showAiContadorModal = true;
                this.aiContadorTab = 'balance';
                this.selectedAiContadorClient = clientObj;
                try {
                    const res = await fetch('/api/ai_financial_advisor');
                    if (res.ok) {
                        this.aiContadorData = await res.json();
                    }
                } catch(e) {
                    console.error("Error al obtener datos del Contador IA:", e);
                }

                if (clientObj) {
                    this.aiContadorTab = 'chat';
                    await this.sendAiContadorQuery(`Informe contable y saldo de ${clientObj.name}`, clientObj.id);
                }
            },

            closeAiContadorModal() {
                this.showAiContadorModal = false;
                this.selectedAiContadorClient = null;
            },

            async sendAiContadorQuery(overrideQuery = null, overrideClientId = null) {
                const queryText = (overrideQuery || this.aiContadorQuery || '').trim();
                const clientId = overrideClientId || (this.selectedAiContadorClient ? this.selectedAiContadorClient.id : null);
                if (!queryText) return;

                this.aiContadorMessages.push({ role: 'user', text: queryText });
                if (!overrideQuery) this.aiContadorQuery = '';

                try {
                    const res = await fetch('/api/ai_financial_advisor/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: queryText, client_id: clientId })
                    });
                    const data = await res.json();
                    if (data.success) {
                        this.aiContadorMessages.push({
                            role: 'assistant',
                            text: data.reply,
                            title: data.title,
                            pdf_export_available: data.pdf_export_available
                        });
                    } else {
                        this.aiContadorMessages.push({ role: 'assistant', text: "⚠️ " + (data.error || "No se pudo procesar la consulta.") });
                    }
                } catch(e) {
                    this.aiContadorMessages.push({ role: 'assistant', text: "Error de conexión: " + e.message });
                }
            },

            async downloadAiContadorPdf(title = 'Informe Contable IA', textBody = '') {
                try {
                    const res = await fetch('/api/ai_financial_advisor/export_pdf', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ title: title, text_body: textBody })
                    });
                    if (res.ok) {
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    } else {
                        alert("Error al exportar PDF.");
                    }
                } catch(e) {
                    alert("Error al descargar PDF: " + e.message);
                }
            },

            showArqueoModal: false,
            async openArqueoModal() { await this.fetchArqueoCaja(); this.showArqueoModal = true; },
            closeArqueoModal() { this.showArqueoModal = false; }
        }));
    }
}

function roundVal(v) {
    return Math.round((v + Number.EPSILON) * 100) / 100;
}

// Register both on alpine:init event and immediately if Alpine is already present
document.addEventListener('alpine:init', registerPrestamosApp);
if (window.Alpine) {
    registerPrestamosApp();
}
