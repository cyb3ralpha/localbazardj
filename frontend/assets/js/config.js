const CONFIG = {
  get API_BASE() {
    // Same-origin when Django serves both frontend + backend
    if (window.location.port && !['5500','5501','8080','3000'].includes(window.location.port)) {
      return window.location.origin + '/api';
    }
    return 'http://127.0.0.1:8000/api';
  }
};

const Auth = {
  getToken: () => localStorage.getItem('lb_token'),
  getUser: () => JSON.parse(localStorage.getItem('lb_user') || 'null'),
  setAuth: (token, refresh, user) => {
    localStorage.setItem('lb_token', token);
    localStorage.setItem('lb_refresh', refresh);
    localStorage.setItem('lb_user', JSON.stringify(user));
  },
  logout: () => {
    localStorage.removeItem('lb_token');
    localStorage.removeItem('lb_refresh');
    localStorage.removeItem('lb_user');
    window.location.href = '/pages/login.html';
  },
  isLoggedIn: () => !!localStorage.getItem('lb_token'),
  hasRole: (roles) => {
    const user = Auth.getUser();
    return user && roles.includes(user.role);
  },
};

async function apiCall(endpoint, method = 'GET', data = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = Auth.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const opts = { method, headers };
  if (data) opts.body = JSON.stringify(data);
  try {
    const res = await fetch(CONFIG.API_BASE + endpoint, opts);
    if (res.status === 401) { Auth.logout(); return null; }
    const json = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data: json };
  } catch (e) {
    console.error('API Error:', e);
    return { ok: false, data: { detail: 'Cannot connect to server. Is Django running on port 8000?' } };
  }
}

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `lb-toast lb-toast-${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 3200);
}

const formatPrice = (p) => '₨\u00a0' + Number(p).toLocaleString('en-PK');
const formatDist  = (d) => !d ? '' : d < 1 ? `${Math.round(d * 1000)}m away` : `${d.toFixed(1)}km away`;

function timeSince(date) {
  const s = Math.floor((new Date() - new Date(date)) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}
