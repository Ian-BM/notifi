/* Notifi — lightweight vanilla canvas charts for dashboards */

function drawBarChart(canvasId, labels, values, color) {
  var canvas = document.getElementById(canvasId);
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var dpr = window.devicePixelRatio || 1;
  var width = canvas.clientWidth;
  var height = canvas.clientHeight;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  var max = Math.max.apply(null, values.concat([1]));
  var padding = 28;
  var chartHeight = height - padding * 2;
  var barWidth = (width - padding * 2) / values.length * 0.6;
  var gap = (width - padding * 2) / values.length;

  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  values.forEach(function (val, i) {
    var barHeight = (val / max) * chartHeight;
    var x = padding + i * gap + (gap - barWidth) / 2;
    var y = height - padding - barHeight;

    ctx.fillStyle = color || '#1a56db';
    roundRect(ctx, x, y, barWidth, barHeight, 4);
    ctx.fill();

    ctx.fillStyle = '#64748b';
    ctx.font = '11px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(labels[i], x + barWidth / 2, height - padding + 16);

    if (val > 0) {
      ctx.fillStyle = '#1e293b';
      ctx.font = 'bold 11px -apple-system, sans-serif';
      ctx.fillText(val, x + barWidth / 2, y - 6);
    }
  });
}

function roundRect(ctx, x, y, w, h, r) {
  if (h <= 0) return;
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function drawDonutChart(canvasId, segments) {
  var canvas = document.getElementById(canvasId);
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var dpr = window.devicePixelRatio || 1;
  var size = Math.min(canvas.clientWidth, canvas.clientHeight);
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, size, size);

  var total = segments.reduce(function (sum, s) { return sum + s.value; }, 0) || 1;
  var cx = size / 2;
  var cy = size / 2;
  var radius = size / 2 - 8;
  var innerRadius = radius * 0.62;
  var start = -Math.PI / 2;

  segments.forEach(function (seg) {
    var angle = (seg.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, start, start + angle);
    ctx.arc(cx, cy, innerRadius, start + angle, start, true);
    ctx.closePath();
    ctx.fillStyle = seg.color;
    ctx.fill();
    start += angle;
  });
}
