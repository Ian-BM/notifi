/* Notifi — contacts page logic */

function formatTzPhone(raw) {
  var digits = (raw || '').replace(/\D/g, '');
  if (digits.startsWith('255')) return digits;
  if (digits.startsWith('0')) return '255' + digits.slice(1);
  if (digits.length === 9) return '255' + digits;
  return digits;
}

document.addEventListener('DOMContentLoaded', function () {
  initPhoneAutoFormat();
  initAddContactForm();
  initDeleteContacts();
  initCsvPreview();
  initContactSearch();
});

function formatPhone(input) {
  var val = input.value.trim().replace(/\s+/g, '');
  if (val.startsWith('+255')) val = val.substring(1);
  if (val.startsWith('0')) val = '255' + val.substring(1);
  if (val && !val.startsWith('255')) val = '255' + val;
  input.value = val;

  if (val && !/^255[67]\d{8}$/.test(val)) {
    input.setCustomValidity('Namba si sahihi. Mfano: 255712345678');
    input.reportValidity();
  } else {
    input.setCustomValidity('');
  }
}

function initPhoneAutoFormat() {
  var phoneInput = document.getElementById('contact-phone');
  if (!phoneInput) return;
  phoneInput.addEventListener('blur', function () {
    formatPhone(phoneInput);
  });
  phoneInput.addEventListener('input', function () {
    phoneInput.setCustomValidity('');
  });
}

function initAddContactForm() {
  var form = document.getElementById('add-contact-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var formData = new FormData(form);
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    fetch(form.action, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: formData,
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (submitBtn) submitBtn.disabled = false;
        if (!data.success) {
          showToast(data.error || 'Could not add contact.', 'error');
          return;
        }
        addContactRow(data.contact);
        form.reset();
        var modal = form.closest('.modal-overlay');
        if (modal) modal.classList.remove('active');
        showToast('Contact added.', 'success');
      })
      .catch(function () {
        if (submitBtn) submitBtn.disabled = false;
        showToast('Network error. Please try again.', 'error');
      });
  });
}

function addContactRow(contact) {
  var emptyState = document.getElementById('contacts-empty-state');
  var table = document.getElementById('contacts-table');
  if (emptyState && table) {
    emptyState.style.display = 'none';
    table.style.display = '';
    table.className = 'data-table stack-on-mobile';
    if (!table.querySelector('thead')) {
      table.innerHTML =
        '<thead><tr><th>Name</th><th>Phone</th><th>Group</th><th>Date Added</th><th></th></tr></thead>' +
        '<tbody></tbody>';
    }
  }

  var tbody = document.querySelector('#contacts-table tbody');
  if (!tbody) return;
  var row = document.createElement('tr');
  row.setAttribute('data-contact-id', contact.id);
  row.innerHTML =
    '<td data-label="Name">' + escapeHtml(contact.name) + '</td>' +
    '<td data-label="Phone">' + escapeHtml(contact.phone) + '</td>' +
    '<td data-label="Group">' + (contact.group ? '<span class="badge badge-blue">' + escapeHtml(contact.group) + '</span>' : '<span class="text-muted">—</span>') + '</td>' +
    '<td data-label="Date Added">' + escapeHtml(contact.created_at) + '</td>' +
    '<td data-label=""><button class="btn btn-sm btn-outline delete-contact-btn" data-id="' + contact.id + '">Delete</button></td>';
  tbody.prepend(row);
}

function escapeHtml(str) {
  var div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function initDeleteContacts() {
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.delete-contact-btn');
    if (!btn) return;
    if (!window.confirm('Delete this contact?')) return;

    var id = btn.getAttribute('data-id');
    fetch('/contacts/delete/' + id + '/', {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.success) {
          var row = document.querySelector('tr[data-contact-id="' + id + '"]');
          if (row) row.remove();
          showToast('Contact deleted.', 'success');
        } else {
          showToast('Could not delete contact.', 'error');
        }
      })
      .catch(function () {
        showToast('Network error. Please try again.', 'error');
      });
  });
}

function initCsvPreview() {
  var fileInput = document.getElementById('csv-file-input');
  var dropZone = document.getElementById('csv-drop-zone');
  var previewTable = document.getElementById('csv-preview-table');
  var nameSelect = document.getElementById('id_name_column');
  var phoneSelect = document.getElementById('id_phone_column');
  if (!fileInput || !dropZone) return;

  dropZone.addEventListener('click', function () { fileInput.click(); });
  dropZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', function () {
    dropZone.classList.remove('dragover');
  });
  dropZone.addEventListener('drop', function (e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      handleCsvFile(fileInput.files[0]);
    }
  });
  fileInput.addEventListener('change', function () {
    if (fileInput.files.length) handleCsvFile(fileInput.files[0]);
  });

  function handleCsvFile(file) {
    dropZone.querySelector('.upload-zone-text').textContent = file.name;
    var reader = new FileReader();
    reader.onload = function (evt) {
      var lines = evt.target.result.split(/\r?\n/).filter(Boolean).slice(0, 6);
      if (!lines.length) return;
      var rows = lines.map(function (line) { return line.split(','); });
      var headers = rows[0];

      if (nameSelect && phoneSelect) {
        [nameSelect, phoneSelect].forEach(function (sel) {
          sel.innerHTML = '';
          headers.forEach(function (h) {
            var opt = document.createElement('option');
            opt.value = h.trim();
            opt.textContent = h.trim();
            sel.appendChild(opt);
          });
        });
      }

      if (previewTable) {
        var html = '<table class="data-table"><thead><tr>';
        headers.forEach(function (h) { html += '<th>' + escapeHtml(h) + '</th>'; });
        html += '</tr></thead><tbody>';
        rows.slice(1, 6).forEach(function (row) {
          html += '<tr>';
          row.forEach(function (cell) { html += '<td>' + escapeHtml(cell) + '</td>'; });
          html += '</tr>';
        });
        html += '</tbody></table>';
        previewTable.innerHTML = html;
        previewTable.style.display = 'block';
      }

      var importBtn = document.getElementById('csv-import-submit');
      if (importBtn) importBtn.disabled = false;
    };
    reader.readAsText(file);
  }
}

function initContactSearch() {
  var input = document.getElementById('contact-search');
  if (!input) return;
  var timer;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var url = new URL(window.location.href);
      url.searchParams.set('q', input.value);
      window.location.href = url.toString();
    }, 600);
  });
}
