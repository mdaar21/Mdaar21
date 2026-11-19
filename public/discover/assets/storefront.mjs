const year = document.querySelector('#footer-year');
if (year) year.textContent = new Intl.NumberFormat('ar-SA', { useGrouping: false }).format(new Date().getFullYear());

// Move keyboard focus to in-page destinations without interrupting scrolling.
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', () => {
    const target = document.getElementById(link.hash.slice(1));
    if (!target) return;
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
  });
});
