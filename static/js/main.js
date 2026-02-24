/* ═══════════════════════════════════════════════════════════
   EyeDetect AI — Main JavaScript
═══════════════════════════════════════════════════════════ */

// ── Mobile nav ─────────────────────────────────────────────
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (navToggle && mobileMenu) {
  navToggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!navToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

// ── Animate elements on scroll ─────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.step-item, .disease-card, .feature-card, .stat-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// ── Animate probability bars ────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const fills = document.querySelectorAll('.prob-fill');
  fills.forEach((fill, i) => {
    const targetWidth = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => {
      fill.style.width = targetWidth;
    }, 200 + i * 80);
  });
});

// ── Sample question click in chatbot ───────────────────────
document.querySelectorAll('.sample-questions li').forEach(li => {
  li.addEventListener('click', () => {
    const input = document.getElementById('chatInput');
    if (input) {
      input.value = li.textContent.trim();
      input.focus();
    }
  });
});

// ── Auto-scroll chat to bottom ─────────────────────────────
function scrollChatBottom() {
  const msgs = document.getElementById('chatMessages');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
}
scrollChatBottom();

// ── Flash message auto-close ────────────────────────────────
const alerts = document.querySelectorAll('.alert');
alerts.forEach(alert => {
  setTimeout(() => {
    alert.style.transition = 'opacity 0.5s';
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 500);
  }, 5000);
});

// ── Copy detection ID to clipboard ─────────────────────────
document.querySelectorAll('code').forEach(el => {
  el.style.cursor = 'pointer';
  el.title = 'Click to copy';
  el.addEventListener('click', () => {
    navigator.clipboard.writeText(el.textContent).then(() => {
      const orig = el.textContent;
      el.textContent = '✓ Copied!';
      setTimeout(() => el.textContent = orig, 1500);
    });
  });
});

// ── Lazy image loading ──────────────────────────────────────
document.querySelectorAll('img[data-src]').forEach(img => {
  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        img.src = img.dataset.src;
        imgObserver.unobserve(img);
      }
    });
  });
  imgObserver.observe(img);
});

console.log('✅ EyeDetect AI JavaScript loaded');
