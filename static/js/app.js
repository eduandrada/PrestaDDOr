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
                company_cuit: '',
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

            // Forms State
            clientForm: { id: null, name: '', whatsapp: '', email: '', address: '', notes: '' },
            loanForm: { client_id: '', amount: 50000, interest_rate: 15, rate_type: 'mensual', modality: 'mensual', installments_count: 4, start_date: new Date().toISOString().split('T')[0], grace_days: 3, late_fee_type: 'porcentaje', late_fee_value: 1.0, notes: '' },
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
                audioBlob: null,
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
                this.fetchDolarRates();

                window.addEventListener('beforeinstallprompt', (e) => {
                    e.preventDefault();
                    this.deferredPwaPrompt = e;
                });
                window.addEventListener('appinstalled', () => {
                    this.isPwaInstalled = true;
                    this.deferredPwaPrompt = null;
                });
                
                // Real-time synchronization polling (syncs stats live across devices every 4 sec)
                setInterval(() => {
                    this.fetchStats();
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
                    this.fetchCalendarEvents()
                ]);
                this.$nextTick(() => this.renderCharts());
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

            // Client Methods
            openNewClientModal() {
                this.clientForm = { id: null, name: '', whatsapp: '', email: '', address: '', notes: '' };
                this.activeModal = 'newClient';
            },

            openEditClientModal(client) {
                this.clientForm = { ...client };
                this.activeModal = 'editClient';
            },

            async viewClientHistory(client) {
                try {
                    const res = await fetch(`/api/clients/${client.id}/history`);
                    this.selectedClientHistory = await res.json();
                    this.activeModal = 'clientHistory';
                } catch (err) {
                    alert("Error al cargar historial del cliente.");
                }
            },

            async saveClient() {
                if (!this.clientForm.name || !this.clientForm.whatsapp) {
                    alert("Ingrese nombre completo y teléfono de WhatsApp.");
                    return;
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
                        this.activeModal = null;
                        await this.fetchClients();
                        await this.fetchStats();
                    }
                } catch (err) {
                    alert("Error al guardar cliente");
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
                    interest_rate: 15,
                    rate_type: 'mensual',
                    modality: 'mensual',
                    installments_count: 4,
                    start_date: new Date().toISOString().split('T')[0],
                    grace_days: parseInt(this.settings.default_grace_days || '3'),
                    late_fee_type: 'porcentaje',
                    late_fee_value: parseFloat(this.settings.default_late_fee || '1.0'),
                    notes: '',
                    signature_data: ''
                };
                this.activeModal = 'newLoan';
                this.initSignaturePad();
            },

            get selectedLoanClient() {
                if (!this.loanForm.client_id) return null;
                return this.clients.find(c => c.id == this.loanForm.client_id) || null;
            },

            async saveLoan() {
                if (!this.loanForm.client_id || !this.loanForm.amount || this.loanForm.amount <= 0) {
                    alert("Seleccione un cliente y especifique un monto válido.");
                    return;
                }
                try {
                    const res = await fetch('/api/loans', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.loanForm)
                    });
                    if (res.ok) {
                        this.activeModal = null;
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al registrar el préstamo.");
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
                if (!confirm("¿Eliminar este gasto?")) return;
                try {
                    const res = await fetch(`/api/expenses/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        await this.loadAllData();
                    }
                } catch (err) {
                    alert("Error al eliminar gasto.");
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
                        alert(`Se eliminaron ${data.deleted_count} gastos.`);
                        this.selectedExpenseIds = [];
                        this.selectAllExpenses = false;
                        await this.loadAllData();
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
            }
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
