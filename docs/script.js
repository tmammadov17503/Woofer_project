/* ═══════════════════════════════════════════════════
   Woofer Care AI — script.js
═══════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 1. FLOATING PAW PRINTS ── */
  const pawContainer = document.getElementById('paws');
  if (pawContainer) {
    for (let i = 0; i < 10; i++) {
      const el = document.createElement('div');
      el.className = 'paw';
      el.textContent = '🐾';
      el.style.left = (5 + Math.random() * 88) + '%';
      el.style.top  = (5 + Math.random() * 88) + '%';
      el.style.animationDelay = (i * 0.6) + 's';
      el.style.fontSize = (0.9 + Math.random() * 1.4) + 'rem';
      pawContainer.appendChild(el);
    }
  }

  /* ── 2. SCROLL REVEAL ── */
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        revealObserver.unobserve(e.target); // only animate once
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  /* ── 3. ACTIVE NAV LINK ON SCROLL ── */
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');
  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navLinks.forEach(a => a.classList.remove('active'));
        const active = document.querySelector(`.nav-links a[href="#${e.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { threshold: 0.4 });
  sections.forEach(s => sectionObserver.observe(s));

  /* ── 4. BACK TO TOP BUTTON ── */
  const backToTop = document.getElementById('backToTop');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      backToTop.classList.toggle('visible', window.scrollY > 500);
    });
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── 5. MOBILE HAMBURGER MENU ── */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
    });
    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => mobileMenu.classList.remove('open'));
    });
  }

  /* ── 6. VIDEO PLAY BUTTON ── */
  const videoThumb = document.getElementById('videoThumb');
  const videoFrame = document.getElementById('videoFrame');
  if (videoThumb && videoFrame) {
    videoThumb.addEventListener('click', () => {
      // Add autoplay to iframe src when user clicks play
      const src = videoFrame.getAttribute('data-src');
      videoFrame.setAttribute('src', src + '?autoplay=1');
      videoThumb.classList.add('hidden');
    });
  }

  /* ── 7. NAV SHADOW ON SCROLL ── */
  const nav = document.querySelector('nav');
  window.addEventListener('scroll', () => {
    nav.style.boxShadow = window.scrollY > 20
      ? '0 4px 24px rgba(44,26,14,0.1)'
      : 'none';
  });

});
