/* ═══════════════════════════════════════════════════════════
    MediBook — main.js  (single unified file)
    Covers: Navbar · Sidebar · Dark Mode · Language · Clock
            Accessibility · Password · Strength · Modals · Slots
            Tabs · Table Filter · Profile Pic · AJAX · Toast
            Greeting · OTP · Alerts · Flash · AI Assistant
═══════════════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────────────────
    1. NAVBAR
───────────────────────────────────────────────────────── */
function toggleNav() {
    document.getElementById('navLinks')?.classList.toggle('open');
}

/* ─────────────────────────────────────────────────────────
    2. SIDEBAR
───────────────────────────────────────────────────────── */
function toggleSidebar() {
    document.getElementById('sideSidebar')?.classList.toggle('open');
    document.getElementById('sidebarOverlay')?.classList.toggle('show');
}

/* ─────────────────────────────────────────────────────────
    3. DARK / LIGHT MODE
───────────────────────────────────────────────────────── */
function applyTheme(theme) {
    document.body.classList.toggle('dark-mode', theme === 'dark');
    const icon  = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    if (icon)  icon.className    = theme === 'dark' ? 'fas fa-sun'  : 'fas fa-moon';
    if (label) label.textContent = theme === 'dark' ? 'Light'       : 'Dark';
    localStorage.setItem('site_theme', theme);
}

function toggleTheme() {
    applyTheme(document.body.classList.contains('dark-mode') ? 'light' : 'dark');
}

// Apply theme ASAP to avoid flash
(function () {
    const saved = localStorage.getItem('site_theme')
        || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    if (saved === 'dark') document.body.classList.add('dark-mode');
})();

/* ─────────────────────────────────────────────────────────
    4. LANGUAGE SWITCHER (Google Translate)
───────────────────────────────────────────────────────── */
function googleTranslateElementInit() {
    new google.translate.TranslateElement(
        { pageLanguage: 'en', includedLanguages: 'en,ar', autoDisplay: false },
        'google_translate_element'
    );
}

function setSiteLanguage(langCode) {
    if (langCode === 'en') {
        document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        window.location.reload();
        return;
    }
    const combo = document.querySelector('select.goog-te-combo');
    if (!combo) { setTimeout(() => setSiteLanguage(langCode), 500); return; }
    combo.value = langCode;
    combo.dispatchEvent(new Event('change'));
    const labels = { en: 'EN', ar: 'AR'};
    const label = document.getElementById('langBtnLabel');
    if (label) label.textContent = labels[langCode] || 'EN';
    document.getElementById('langDropdown')?.classList.remove('open');
}

function toggleLangDropdown() {
    document.getElementById('langDropdown')?.classList.toggle('open');
}

/* ─────────────────────────────────────────────────────────
    5. LIVE WORLD CLOCK
───────────────────────────────────────────────────────── */
const COUNTRY_TIMEZONES = {
    JO: { label: '🇯🇴 Jordan (Amman)',        zone: 'Asia/Amman' },
    US: { label: '🇺🇸 USA (New York)',         zone: 'America/New_York' },
    GB: { label: '🇬🇧 UK (London)',            zone: 'Europe/London' },
    AE: { label: '🇦🇪 UAE (Dubai)',            zone: 'Asia/Dubai' },
    SA: { label: '🇸🇦 Saudi Arabia (Riyadh)',  zone: 'Asia/Riyadh' },
    EG: { label: '🇪🇬 Egypt (Cairo)',          zone: 'Africa/Cairo' },
    IL: { label: '🇮🇱 Israel (Jerusalem)',     zone: 'Asia/Jerusalem' },
    FR: { label: '🇫🇷 France (Paris)',         zone: 'Europe/Paris' },
    JP: { label: '🇯🇵 Japan (Tokyo)',          zone: 'Asia/Tokyo' },
    IN: { label: '🇮🇳 India (New Delhi)',      zone: 'Asia/Kolkata' },
};

function populateCountrySelect() {
    const select = document.getElementById('clockCountrySelect');
    if (!select) return;
    Object.entries(COUNTRY_TIMEZONES).forEach(([code, { label }]) => {
        const opt = document.createElement('option');
        opt.value = code;
        opt.textContent = label;
        select.appendChild(opt);
    });
    select.value = localStorage.getItem('clock_country') || 'JO';
    select.addEventListener('change', () => {
        localStorage.setItem('clock_country', select.value);
        updateClock();
        updateGreeting();
    });
}

function updateClock() {
    const select = document.getElementById('clockCountrySelect');
    const timeEl = document.getElementById('clockTime');
    const dateEl = document.getElementById('clockDate');
    if (!select || !timeEl) return;
    const zone = COUNTRY_TIMEZONES[select.value]?.zone || 'Asia/Amman';
    const now  = new Date();
    timeEl.textContent = new Intl.DateTimeFormat('en-GB', {
        timeZone: zone, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    }).format(now);
    if (dateEl) dateEl.textContent = new Intl.DateTimeFormat('en-GB', {
        timeZone: zone, weekday: 'short', year: 'numeric', month: 'short', day: '2-digit'
    }).format(now);
}

/* ─────────────────────────────────────────────────────────
    6. GREETING
───────────────────────────────────────────────────────── */
function updateGreeting() {
    const select     = document.getElementById('clockCountrySelect');
    const greetingEl = document.getElementById('greetingText');
    if (!select || !greetingEl) return;
    const zone = COUNTRY_TIMEZONES[select.value]?.zone || 'Asia/Amman';
    const hour = parseInt(
        new Intl.DateTimeFormat('en-US', { hour: 'numeric', hour12: false, timeZone: zone }).format(new Date())
    );
    let greeting = 'Good evening';
    if (hour >= 5  && hour < 12) greeting = 'Good morning';
    else if (hour >= 12 && hour < 18) greeting = 'Good afternoon';
    greetingEl.textContent = `${greeting}, ${greetingEl.dataset.username || ''}!`;
}

/* ─────────────────────────────────────────────────────────
    7. ACCESSIBILITY PANEL
───────────────────────────────────────────────────────── */
let currentFontStep = 0;

function toggleAccessPanel() {
    document.getElementById('accessPanel')?.classList.toggle('open');
}

function changeFontSize(step) {
    currentFontStep = Math.max(-2, Math.min(4, currentFontStep + step));
    document.documentElement.style.fontSize = (100 + currentFontStep * 10) + '%';
    localStorage.setItem('accessFontStep', currentFontStep);
}

function resetFontSize() {
    currentFontStep = 0;
    document.documentElement.style.fontSize = '100%';
    localStorage.setItem('accessFontStep', 0);
}

function toggleContrast() {
    const on = document.getElementById('contrastToggle')?.checked;
    document.body.classList.toggle('high-contrast', on);
    localStorage.setItem('highContrast', on ? 'true' : 'false');
}

function toggleUnderlineLinks() {
    const on = document.getElementById('underlineToggle')?.checked;
    document.body.classList.toggle('underline-links', on);
    localStorage.setItem('underlineLinks', on ? 'true' : 'false');
}

function resetAccessibility() {
    resetFontSize();
    document.body.classList.remove('high-contrast', 'underline-links');
    const ct = document.getElementById('contrastToggle');
    const ul = document.getElementById('underlineToggle');
    if (ct) ct.checked = false;
    if (ul) ul.checked = false;
    localStorage.removeItem('highContrast');
    localStorage.removeItem('underlineLinks');
}

function applyAccessibility() {
    currentFontStep = parseInt(localStorage.getItem('accessFontStep')) || 0;
    document.documentElement.style.fontSize = (100 + currentFontStep * 10) + '%';
    if (localStorage.getItem('highContrast') === 'true') {
        document.body.classList.add('high-contrast');
        const ct = document.getElementById('contrastToggle');
        if (ct) ct.checked = true;
    }
    if (localStorage.getItem('underlineLinks') === 'true') {
        document.body.classList.add('underline-links');
        const ul = document.getElementById('underlineToggle');
        if (ul) ul.checked = true;
    }
}

/* ─────────────────────────────────────────────────────────
    8. PASSWORD TOGGLE
───────────────────────────────────────────────────────── */
function togglePassword(fieldId, iconId) {
    const field = document.getElementById(fieldId);
    const icon  = document.getElementById(iconId);
    if (!field || !icon) return;
    const isPass = field.type === 'password';
    field.type = isPass ? 'text' : 'password';
    icon.classList.toggle('fa-eye',       !isPass);
    icon.classList.toggle('fa-eye-slash',  isPass);
}

/* ─────────────────────────────────────────────────────────
    9. PASSWORD STRENGTH METER
───────────────────────────────────────────────────────── */
function checkPasswordStrength(val) {
    const bar  = document.getElementById('strengthBar');
    const text = document.getElementById('strengthText');
    if (!bar || !text) return;

    if (!val) { bar.style.width = '0%'; text.textContent = ''; return; }

    let score = 0;
    if (val.length >= 8)           score++;
    if (/[A-Z]/.test(val))        score++;
    if (/[0-9]/.test(val))        score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
        { width: '0%',   color: '#E2E8F0', label: '' },
        { width: '25%',  color: '#DC2626', label: 'Weak' },
        { width: '50%',  color: '#D97706', label: 'Fair' },
        { width: '75%',  color: '#1A6B9A', label: 'Good' },
        { width: '100%', color: '#16A34A', label: 'Strong' },
    ];
    const level = levels[score];
    bar.style.width      = level.width;
    bar.style.background = level.color;
    text.textContent     = level.label;
    text.style.color     = level.color;
}

/* ─────────────────────────────────────────────────────────
    10. MODALS
───────────────────────────────────────────────────────── */
function openModal(id) {
    document.getElementById(id)?.classList.add('active');
}

function closeModal(id) {
    document.getElementById(id)?.classList.remove('active');
}

/* ─────────────────────────────────────────────────────────
    11. TIME SLOTS
───────────────────────────────────────────────────────── */
function loadAvailableSlots() {
    const doctorId  = document.querySelector('[name="doctor_id"]')?.value;
    const date      = document.getElementById('apptDate')?.value;
    const container = document.getElementById('timeSlotsContainer');
    if (!container) return;
    if (!doctorId || !date) {
        container.innerHTML = '<p class="slots-placeholder">Select a doctor and date first</p>';
        const si = document.getElementById('selectedTime');
        if (si) si.value = '';
        return;
    }
    container.innerHTML = '<p class="slots-placeholder">Loading...</p>';
    fetch(`/agent-dashboard/available-slots/?doctor_id=${doctorId}&date=${date}`)
        .then(r => r.json())
        .then(data => {
            if (data.slots?.length) {
                container.innerHTML = data.slots.map(slot => `
                    <button type="button" class="slot-btn"
                        onclick="selectSlot('${slot}')"
                        id="slot-${slot.replace(':', '-')}">${slot}</button>
                `).join('');
            } else {
                container.innerHTML = '<p class="slot-error">No available slots for this date</p>';
            }
        })
        .catch(() => {
            container.innerHTML = '<p class="slot-error">Error loading slots</p>';
        });
}

function selectSlot(time) {
    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('slot-' + time.replace(':', '-'))?.classList.add('selected');
    const si = document.getElementById('selectedTime');
    if (si) si.value = time;
}

/* ─────────────────────────────────────────────────────────
    12. TABS
───────────────────────────────────────────────────────── */
function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId)?.classList.add('active');
    btn.classList.add('active');
}

/* ─────────────────────────────────────────────────────────
    13. TABLE SEARCH FILTER
───────────────────────────────────────────────────────── */
function filterTable(inputId, tableId) {
    const query = document.getElementById(inputId)?.value.toLowerCase() || '';
    document.querySelectorAll(`#${tableId} tbody tr`).forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
    });
}

/* ─────────────────────────────────────────────────────────
    14. PROFILE PICTURE PREVIEW
───────────────────────────────────────────────────────── */
document.addEventListener('change', (e) => {
    if (e.target.name !== 'profile_picture') return;
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
        const wrapper = document.querySelector('.profile-pic-wrapper');
        if (wrapper) wrapper.innerHTML = `<img src="${ev.target.result}" alt="Preview">`;
    };
    reader.readAsDataURL(file);
});

/* ─────────────────────────────────────────────────────────
    15. AJAX — Status Update, Mark Paid, Message Count
───────────────────────────────────────────────────────── */
function getCookie(name) {
    return document.cookie.split(';')
        .map(c => c.trim())
        .find(c => c.startsWith(name + '='))
        ?.split('=')[1] || '';
}

function updateStatus(select, appointmentId) {
    fetch(`/agent/appointments/${appointmentId}/update-status/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ status: select.value }),
    })
        .then(r => r.json())
        .then(d => showToast(d.success ? 'Status updated ✓' : 'Update failed', d.success ? 'success' : 'error'))
        .catch(() => showToast('Network error', 'error'));
}

function markPaid(btn, billId) {
    if (!confirm('Mark this bill as paid?')) return;
    fetch(`/agent/bills/${billId}/mark-paid/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                btn.outerHTML = '<span class="paid-label"><i class="fas fa-check-circle"></i> Paid</span>';
                showToast('Marked as paid ✓', 'success');
            }
        })
        .catch(() => showToast('Network error', 'error'));
}

function loadMessageCount() {
    const el = document.getElementById('msgCount');
    if (!el) return;
    fetch('/api/message-count/')
        .then(r => r.json())
        .then(d => { el.textContent = d.count || 0; })
        .catch(() => { el.textContent = 0; });
}

/* ─────────────────────────────────────────────────────────
    16. TOAST NOTIFICATION
───────────────────────────────────────────────────────── */
function showToast(message, type = 'success') {
    document.getElementById('mb-toast')?.remove();
    const toast = document.createElement('div');
    toast.id = 'mb-toast';
    toast.textContent = message;
    Object.assign(toast.style, {
        position: 'fixed', bottom: '32px', right: '24px',
        background: type === 'success' ? '#16A34A' : '#DC2626',
        color: '#fff', padding: '12px 20px', borderRadius: '10px',
        fontSize: '0.9rem', fontWeight: '600', zIndex: '99999',
        boxShadow: '0 4px 16px rgba(0,0,0,0.2)', opacity: '1', transition: 'opacity 0.4s',
    });
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; }, 2800);
    setTimeout(() => toast.remove(), 3300);
}

/* ─────────────────────────────────────────────────────────
    17. OTP COUNTDOWN TIMER
───────────────────────────────────────────────────────── */
function initTimer() {
    const timerEl   = document.getElementById('countdown');
    const verifyBtn = document.getElementById('verifyBtn');
    const resendEl  = document.getElementById('resendLink');
    if (!timerEl) return;
    if (resendEl) resendEl.style.display = 'none';
    let seconds = 10 * 60;
    const iv = setInterval(() => {
        seconds--;
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        if (seconds <= 0) {
            clearInterval(iv);
            timerEl.textContent = 'Expired';
            timerEl.closest('.timer')?.classList.add('expired');
            if (verifyBtn) {
                verifyBtn.disabled = true;
                verifyBtn.style.opacity = '0.5';
                verifyBtn.textContent = 'Code Expired — Resend';
            }
            if (resendEl) resendEl.style.display = '';
        }
    }, 1000);
}

/* ─────────────────────────────────────────────────────────
    18. OTP CODE INPUT — auto-submit on 6 digits
───────────────────────────────────────────────────────── */
function initCodeInput() {
    const codeInput = document.getElementById('codeInput');
    if (!codeInput) return;
    codeInput.focus();
    codeInput.addEventListener('input', function () {
        this.value = this.value.replace(/[^0-9]/g, '');
        if (this.value.length === 6) {
            setTimeout(() => this.closest('form')?.submit(), 300);
        }
    });
}

/* ─────────────────────────────────────────────────────────
    19. CONFIRM PASSWORD MATCH
───────────────────────────────────────────────────────── */
function initConfirmMatch() {
    const confirmField  = document.getElementById('confirmField');
    const passwordField = document.getElementById('passwordField');
    if (!confirmField || !passwordField) return;
    confirmField.addEventListener('input', function () {
        this.style.borderColor = (this.value && this.value !== passwordField.value) ? '#DC2626' : '';
    });
}

/* ─────────────────────────────────────────────────────────
    20. AUTO-DISMISS ALERTS
───────────────────────────────────────────────────────── */
function autoDismissAlerts() {
    document.querySelectorAll('.alert-error, .alert-success, .alert-dismissible').forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 500);
        }, 4000);
    });
}

/* ─────────────────────────────────────────────────────────
    21. ?success= FLASH MESSAGE
───────────────────────────────────────────────────────── */
function checkSuccessParam() {
    if (!new URLSearchParams(window.location.search).get('success')) return;
    showToast('Changes saved successfully ✓', 'success');
}

/* ─────────────────────────────────────────────────────────
    22. AI ASSISTANT PANEL
───────────────────────────────────────────────────────── */
window.toggleAiPanel = function () {
    const panel = document.getElementById('aiPanel');
    if (!panel) return;
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) {
        document.getElementById('aiChatInput')?.focus();
    }
};


window.sendAiMessage = async function () {
    const input    = document.getElementById('aiChatInput');
    const messages = document.getElementById('aiMessages');
    const sendBtn  = document.getElementById('aiSendBtn');
    const text     = input?.value.trim();
    if (!text || !messages) return;

    // رسالة المستخدم
    const userDiv = document.createElement('div');
    userDiv.className   = 'ai-msg-user';
    userDiv.textContent = text;
    messages.appendChild(userDiv);
    input.value = '';
    if (sendBtn) sendBtn.disabled = true;

    // Typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className   = 'ai-msg-typing';
    typingDiv.textContent = 'Thinking...';
    messages.appendChild(typingDiv);
    messages.scrollTop = messages.scrollHeight;

    try {
        const res = await fetch('/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        typingDiv.remove();

        const botDiv = document.createElement('div');
        botDiv.className   = 'ai-msg-bot';
        botDiv.textContent = data.reply || 'Sorry, no response.';
        messages.appendChild(botDiv);

    } catch {
        typingDiv.remove();
        const errDiv = document.createElement('div');
        errDiv.className   = 'ai-msg-bot';
        errDiv.textContent = 'Connection error. Please try again.';
        messages.appendChild(errDiv);
    }

    if (sendBtn) sendBtn.disabled = false;
    messages.scrollTop = messages.scrollHeight;
};

/* ─────────────────────────────────────────────────────────
    GLOBAL EVENT LISTENERS
───────────────────────────────────────────────────────── */

// Close lang dropdown when clicking outside
document.addEventListener('click', (e) => {
    const switcher = document.querySelector('.lang-switcher');
    if (switcher && !switcher.contains(e.target))
        document.getElementById('langDropdown')?.classList.remove('open');
});

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay'))
        e.target.classList.remove('active');
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape')
        document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
});

// Cancel confirmation via data-confirm
document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-confirm]');
    if (!link) return;
    if (!confirm(link.dataset.confirm || 'Are you sure?')) e.preventDefault();
});

// Status select loading indicator
document.addEventListener('change', (e) => {
    if (!e.target.classList.contains('select-sm')) return;
    const row = e.target.closest('tr');
    if (row) { row.style.opacity = '0.5'; row.style.pointerEvents = 'none'; }
});

// Send AI message on Enter
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement?.id === 'aiChatInput')
        sendAiMessage();
});

/* ─────────────────────────────────────────────────────────
    INIT
───────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

    // Theme
    applyTheme(localStorage.getItem('site_theme') || 'light');

    // Language — reset on fresh load
    document.cookie = 'googtrans=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
    document.cookie = 'googtrans=; path=/; domain=.' + location.hostname + '; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
    const langLabel = document.getElementById('langBtnLabel');
    if (langLabel) langLabel.textContent = 'EN';

    // Clock & greeting
    populateCountrySelect();
    updateClock();
    updateGreeting();
    setInterval(() => { updateClock(); updateGreeting(); }, 1000);

    // Accessibility
    applyAccessibility();

    // Password toggles — data-target pattern (login, register, reset)
    document.querySelectorAll('[data-target]').forEach(btn => {
        btn.addEventListener('click', () => togglePassword(btn.dataset.target, btn.dataset.icon));
    });
    // Legacy IDs fallback
    document.getElementById('toggleBtn')?.addEventListener('click', () => togglePassword('passwordField', 'eyeIcon1'));
    document.getElementById('togglePassword')?.addEventListener('click', () => togglePassword('passwordField', 'eyeIcon1'));
    document.getElementById('toggleConfirm')?.addEventListener('click', () => togglePassword('confirmField', 'eyeIcon2'));

    // Password strength
    document.getElementById('passwordField')?.addEventListener('input', function () {
        checkPasswordStrength(this.value);
    });

    // Confirm password match
    initConfirmMatch();

    // OTP
    initCodeInput();
    initTimer();

    // Prevent past dates in date inputs
    const dateInput = document.querySelector('input[name="date"]');
    if (dateInput) dateInput.setAttribute('min', new Date().toISOString().split('T')[0]);

    // Register form: password match on submit
    document.getElementById('registerForm')?.addEventListener('submit', (e) => {
        const p = document.getElementById('passwordField')?.value;
        const c = document.getElementById('confirmField')?.value;
        if (p && c && p !== c) {
            e.preventDefault();
            showToast('Passwords do not match!', 'error');
            document.getElementById('confirmField')?.focus();
        }
    });

    // Message form validation
    document.getElementById('messageForm')?.addEventListener('submit', (e) => {
        const subject = document.querySelector('[name="subject"]')?.value.trim();
        const body    = document.querySelector('[name="body"]')?.value.trim();
        if (!subject || !body) {
            e.preventDefault();
            showToast('Please fill in Subject and Message', 'error');
        }
    });

    // AJAX
    loadMessageCount();

    // Alerts & flash
    autoDismissAlerts();
    checkSuccessParam();
});
// greeting
    const hour = new Date().getHours();
    let g = "Good evening";
    if (hour < 12) g = "Good morning";
    else if (hour < 17) g = "Good afternoon";
    document.getElementById("greeting").textContent = g;
