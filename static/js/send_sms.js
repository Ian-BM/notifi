/* Notifi — Send SMS compose logic */

document.addEventListener('DOMContentLoaded', function () {
  var textarea = document.getElementById('message-content');
  var counter = document.getElementById('char-counter');
  var groupSelect = document.getElementById('group-select');
  var recipientCountEl = document.getElementById('recipient-count');
  var creditsNeededEl = document.getElementById('credits-needed');
  var balanceAfterEl = document.getElementById('balance-after');
  var sendBtn = document.getElementById('send-sms-btn');
  var form = document.getElementById('send-sms-form');
  var previewContent = document.getElementById('preview-content');

  if (!textarea) return;

  var currentBalance = parseInt(sendBtn ? sendBtn.getAttribute('data-balance') : '0', 10) || 0;
  var groupCounts = {};
  document.querySelectorAll('#group-select option').forEach(function (opt) {
    groupCounts[opt.value] = parseInt(opt.getAttribute('data-count') || '0', 10);
  });

  function smsSegments(len) {
    if (len === 0) return 0;
    if (len <= 160) return 1;
    if (len <= 306) return 2;
    return 3;
  }

  function updateCounter() {
    var len = textarea.value.length;
    var segments = smsSegments(len);
    counter.textContent = len + ' chars' + (segments > 1 ? ' (' + segments + ' SMS parts)' : '');
    counter.classList.remove('ok', 'warning', 'over');
    if (len <= 140) counter.classList.add('ok');
    else if (len <= 160) counter.classList.add('warning');
    else counter.classList.add('over');

    if (previewContent) previewContent.textContent = textarea.value || 'Your message preview will appear here...';
    updateSummary(segments);
  }

  function updateSummary(segments) {
    var groupVal = groupSelect ? groupSelect.value : '';
    var count = groupCounts[groupVal] || 0;
    var credits = segments * count;
    var after = currentBalance - credits;

    if (recipientCountEl) recipientCountEl.textContent = count;
    if (creditsNeededEl) creditsNeededEl.textContent = credits;
    if (balanceAfterEl) balanceAfterEl.textContent = after >= 0 ? after : '—';

    if (sendBtn) {
      var insufficient = credits > 0 && after < 0;
      var noRecipients = count === 0;
      var noMessage = textarea.value.trim().length === 0;
      sendBtn.disabled = insufficient || noRecipients || noMessage;
      var warningEl = document.getElementById('insufficient-warning');
      if (warningEl) warningEl.style.display = insufficient ? 'flex' : 'none';
    }
  }

  textarea.addEventListener('input', updateCounter);
  if (groupSelect) groupSelect.addEventListener('change', updateCounter);

  document.querySelectorAll('.template-pill').forEach(function (pill) {
    pill.addEventListener('click', function () {
      textarea.value = pill.getAttribute('data-content') || '';
      updateCounter();
      textarea.focus();
    });
  });

  if (form) {
    form.addEventListener('submit', function (e) {
      var groupVal = groupSelect ? groupSelect.value : '';
      var count = groupCounts[groupVal] || 0;
      var segments = smsSegments(textarea.value.length);
      var creditsNeeded = segments * count;

      if (count > 100) {
        var ok = window.confirm(
          'Unataka kutuma SMS kwa watu ' + count + '?\n' +
          'Hii itatumia salio la SMS ' + creditsNeeded + '.\n\n' +
          'Bonyeza OK kuthibitisha.'
        );
        if (!ok) {
          e.preventDefault();
          return;
        }
      }
      if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span class="spinner"></span> Inatuma...';
      }
    });
  }

  var previewCard = document.getElementById('preview-card');
  if (previewCard) {
    previewCard.addEventListener('click', function () {
      previewCard.classList.toggle('expanded');
    });
  }

  updateCounter();
});
