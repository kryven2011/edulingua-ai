// EduLingua AI Admin Panel Frontend Logic

const TOKEN_KEY = 'edulingua_admin_token';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('loginError');

  errorDiv.style.display = 'none';

  try {
    const res = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Ошибка авторизации');
    }

    const data = await res.json();
    setToken(data.access_token);
    window.location.href = '/admin';
  } catch (err) {
    errorDiv.textContent = err.message;
    errorDiv.style.display = 'block';
  }
}

function handleLogout() {
  clearToken();
  window.location.href = '/admin/login';
}

function switchTab(tabName) {
  document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const sec = document.getElementById(`section-${tabName}`);
  if (sec) sec.classList.add('active');

  const nav = document.querySelector(`.nav-item[href="#${tabName}"]`);
  if (nav) nav.classList.add('active');

  if (tabName === 'users') loadUsers();
  if (tabName === 'overview') loadMetrics();
}

async function authFetch(url, options = {}) {
  const token = getToken();
  if (!token) {
    window.location.href = '/admin/login';
    return;
  }

  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };

  const res = await fetch(url, options);
  if (res.status === 401) {
    clearToken();
    window.location.href = '/admin/login';
    return;
  }
  return res;
}

async function loadMetrics() {
  const res = await authFetch('/api/admin/dashboard');
  if (!res) return;
  const data = await res.json();

  document.getElementById('metric-users').textContent = data.total_users || 0;
  document.getElementById('metric-pro').textContent = data.active_subscriptions?.pro || 0;
  document.getElementById('metric-ultimate').textContent = data.active_subscriptions?.ultimate || 0;
  document.getElementById('metric-revenue').textContent = `$${data.total_revenue_usd || 0.00}`;
}

async function loadUsers() {
  const res = await authFetch('/api/admin/users?limit=50');
  if (!res) return;
  const data = await res.json();

  const tbody = document.getElementById('usersTableBody');
  if (!data.users || data.users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center">Пользователей пока нет</td></tr>';
    return;
  }

  tbody.innerHTML = data.users.map(u => `
    <tr>
      <td><code>${u.telegram_id}</code></td>
      <td><b>${u.name || '—'}</b></td>
      <td>${u.username ? '@' + u.username : '—'}</td>
      <td>${(u.language || 'ru').toUpperCase()}</td>
      <td>
        <span class="badge ${u.is_blocked ? 'badge-danger' : 'badge-success'}">
          ${u.is_blocked ? 'Заблокирован' : 'Активен'}
        </span>
      </td>
      <td>
        ${u.is_blocked
          ? `<button onclick="unblockUser('${u.id}')" class="btn btn-sm btn-outline">Разблокировать</button>`
          : `<button onclick="blockUser('${u.id}')" class="btn btn-sm btn-danger">Блокировать</button>`}
      </td>
    </tr>
  `).join('');
}

async function blockUser(userId) {
  if (!confirm('Заблокировать пользователя?')) return;
  await authFetch(`/api/admin/users/${userId}/block`, { method: 'POST' });
  loadUsers();
}

async function unblockUser(userId) {
  await authFetch(`/api/admin/users/${userId}/unblock`, { method: 'POST' });
  loadUsers();
}

async function handleBroadcast(e) {
  e.preventDefault();
  const text = document.getElementById('broadcastText').value;
  const statusDiv = document.getElementById('broadcastStatus');

  statusDiv.style.display = 'none';

  const res = await authFetch('/api/admin/broadcast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });

  if (res && res.ok) {
    const data = await res.json();
    statusDiv.textContent = `✅ Рассылка завершена: отправлено ${data.sent} из ${data.total}`;
    statusDiv.style.display = 'block';
  }
}

// Initial check on dashboard load
if (document.body.classList.contains('dashboard-body')) {
  if (!getToken()) {
    window.location.href = '/admin/login';
  } else {
    loadMetrics();
  }
}
