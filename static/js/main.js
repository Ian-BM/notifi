/* Notifi — global JS utilities */

document.addEventListener('DOMContentLoaded', function () {
  initMobileDrawer();
  initAlertDismiss();
  initConfirmDialogs();
  initModalTriggers();
  initHints();
});

function initMobileDrawer() {
  var drawer = document.getElementById('mobile-drawer');
  var overlay = document.getElementById('mobile-drawer-overlay');
  var moreToggle = document.getElementById('mobile-more-toggle');
  var menuToggle = document.querySelector('.mobile-menu-toggle');
  if (!drawer || !overlay) return;

  function openDrawer() {
    drawer.classList.add('open');
    overlay.classList.add('open');
  }
  function closeDrawer() {
    drawer.classList.remove('open');
    overlay.classList.remove('open');
  }

  if (moreToggle) moreToggle.addEventListener('click', openDrawer);
  if (menuToggle) menuToggle.addEventListener('click', openDrawer);
  overlay.addEventListener('click', closeDrawer);
}

function dismissHint(id) {
  var el = document.getElementById(id);
  if (el) {
    el.style.display = 'none';
    localStorage.setItem('hint_' + id + '_dismissed', '1');
  }
}

function initHints() {
  document.querySelectorAll('.page-hint').forEach(function (hint) {
    var id = hint.id;
    if (localStorage.getItem('hint_' + id + '_dismissed') === '1') {
      hint.style.display = 'none';
    }
  });
}

function initAlertDismiss() {
  document.querySelectorAll('.alert[data-autodismiss]').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.3s';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 300);
    }, 5000);
  });
}

function initConfirmDialogs() {
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-confirm]');
    if (!el) return;
    var msg = el.getAttribute('data-confirm') || 'Are you sure?';
    if (!window.confirm(msg)) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
}

function initModalTriggers() {
  document.querySelectorAll('[data-modal-open]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var modal = document.getElementById(btn.getAttribute('data-modal-open'));
      if (modal) modal.classList.add('active');
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var modal = btn.closest('.modal-overlay');
      if (modal) modal.classList.remove('active');
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) overlay.classList.remove('active');
    });
  });
}

function getCookie(name) {
  var value = '; ' + document.cookie;
  var parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

var CSRF_TOKEN = getCookie('csrftoken');

function showToast(message, type) {
  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  var toast = document.createElement('div');
  toast.className = 'toast ' + (type || '');
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(function () {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(function () { toast.remove(); }, 300);
  }, 3000);
}
