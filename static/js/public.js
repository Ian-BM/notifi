// Mobile nav toggle
function toggleMobileNav() {
  var nav = document.getElementById('mobile-nav');
  var overlay = document.getElementById('nav-overlay');
  nav.classList.toggle('open');
  overlay.classList.toggle('open');
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
  anchor.addEventListener('click', function(e) {
    var target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Close mobile nav if open
      document.getElementById('mobile-nav').classList.remove('open');
      document.getElementById('nav-overlay').classList.remove('open');
    }
  });
});
