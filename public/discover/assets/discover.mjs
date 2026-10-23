import { programs } from './programs.mjs';

const $ = selector => document.querySelector(selector);
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const arabic = new Intl.NumberFormat('ar-SA');

// All navigation and purchase links work without this enhancement layer.
const menuButton = $('#menu-toggle');
const nav = $('#main-nav');
function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'فتح قائمة التنقل');
  nav.classList.remove('is-open');
}
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'إغلاق قائمة التنقل' : 'فتح قائمة التنقل');
  nav.classList.toggle('is-open', open);
});
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('click', event => {
  if (!event.target.closest('.header-inner')) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
matchMedia('(min-width: 701px)').addEventListener('change', closeMenu);

function animateImage(image, source, alt) {
  image.src = source;
  image.alt = alt;
  if (reducedMotion.matches) return;
  image.classList.remove('image-changing');
  requestAnimationFrame(() => image.classList.add('image-changing'));
}

// Genuine PDF excerpts; no checkout, file delivery, or customer data is handled here.
const previews = [
  { source: 'assets/book-cover.webp', alt: 'غلاف بروتوكول التحول الأصلي', caption: 'غلاف بروتوكول التحول · الصفحة ١' },
  { source: 'assets/push-cover.webp', alt: 'غلاف يوم الدفع الأصلي من الكتاب', caption: 'غلاف يوم الدفع · الصفحة ٨' },
  { source: 'assets/exercise-preview.webp', alt: 'معاينة جدول تمارين الدفع وبطاقاته المصوّرة', caption: 'جدول تمارين الدفع · الصفحة ٩' },
];
let previewIndex = 1;
let previewTrigger;
const dialog = $('#book-preview');
function showPreview(index) {
  previewIndex = (index + previews.length) % previews.length;
  const item = previews[previewIndex];
  animateImage($('#preview-image'), item.source, item.alt);
  $('#preview-caption').textContent = item.caption;
  $('#preview-position').textContent = `${arabic.format(previewIndex + 1)} / ${arabic.format(previews.length)}`;
}
document.querySelectorAll('[data-preview-open]').forEach(button => {
  button.addEventListener('click', () => {
    previewTrigger = button;
    showPreview(1);
    dialog.showModal();
    $('#preview-close').focus();
  });
});
$('#preview-close').addEventListener('click', () => dialog.close());
$('#preview-prev').addEventListener('click', () => showPreview(previewIndex - 1));
$('#preview-next').addEventListener('click', () => showPreview(previewIndex + 1));
dialog.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft') { event.preventDefault(); showPreview(previewIndex + 1); }
  if (event.key === 'ArrowRight') { event.preventDefault(); showPreview(previewIndex - 1); }
});
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const box = dialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
});
dialog.addEventListener('close', () => previewTrigger?.focus({ preventScroll: true }));

function tabs(list, activate, vertical = false) {
  const buttons = Array.from(list.querySelectorAll('[role="tab"]'));
  if (vertical) list.setAttribute('aria-orientation', 'vertical');
  function select(button) {
    buttons.forEach(item => {
      const selected = item === button;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    activate(button);
  }
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => select(button));
    button.addEventListener('keydown', event => {
      let next;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (event.key === (vertical ? 'ArrowDown' : 'ArrowLeft')) next = (index + 1) % buttons.length;
      if (event.key === (vertical ? 'ArrowUp' : 'ArrowRight')) next = (index - 1 + buttons.length) % buttons.length;
      if (next === undefined) return;
      event.preventDefault();
      select(buttons[next]);
      buttons[next].focus();
    });
  });
}

const programCopy = {
  '5': { title: 'مساحة لكل جزء.', kicker: 'دفع / سحب / أرجل / علوي / سفلي', summary: 'خمسة أيام تدريب ويومان للراحة، موزعة على دورة أسبوعية واضحة.', cover: 'assets/program-five.webp', alt: 'غلاف برنامج خمسة أيام الأصلي' },
  '4': { title: 'التوازن، على إيقاعك.', kicker: 'علوي / سفلي / علوي / سفلي', summary: 'أربعة أيام تدريب وثلاثة أيام للراحة، بتقسيمة علوي وسفلي خلال الأسبوع.', cover: 'assets/program-four.webp', alt: 'غلاف برنامج أربعة أيام الأصلي' },
};
tabs($('.program-tabs'), button => {
  const key = button.dataset.program;
  const copy = programCopy[key];
  const program = programs[key];
  $('#program-name').textContent = copy.title;
  $('#program-kicker').textContent = copy.kicker;
  $('#program-summary').textContent = copy.summary;
  $('#program-count').textContent = `0${program.trainingDays}`;
  $('#program-count').setAttribute('aria-label', `${arabic.format(program.trainingDays)} أيام تدريب`);
  $('#program-panel').setAttribute('aria-labelledby', button.id);
  animateImage($('#program-cover'), copy.cover, copy.alt);
  const rows = program.days.map((day, index) => {
    const row = document.createElement('li');
    row.classList.toggle('rest', day.rest);
    const label = document.createElement('span');
    label.textContent = `اليوم ${arabic.format(index + 1)}`;
    const name = document.createElement('strong');
    name.textContent = day.name;
    const english = document.createElement('small');
    english.lang = 'en';
    english.textContent = day.rest ? 'RECOVER' : day.en.toUpperCase();
    row.append(label, name, english);
    return row;
  });
  $('#week-list').replaceChildren(...rows);
});

const tools = {
  recipes: { image: 'assets/site-recipes.webp', alt: 'مكتبة وصفات مدار وتعرض 500 وصفة', caption: 'أكلك على ذوقك. يومك أوضح.' },
  calculator: { image: 'assets/site-calculator.webp', alt: 'حاسبة السعرات والماكروز الفعلية من مدار', caption: 'خطوتك الأولى، بتقدير أوضح.' },
  training: { image: 'assets/site-training.webp', alt: 'صفحة التدريب الفعلية في موقع مدار', caption: 'برنامجك معك، وين ما تكون.' },
};
tabs($('.tool-tabs'), button => {
  const item = tools[button.dataset.tool];
  animateImage($('#tool-image'), item.image, item.alt);
  $('#tool-caption').textContent = item.caption;
  $('#tool-panel').setAttribute('aria-labelledby', button.id);
}, true);

if ('IntersectionObserver' in window) {
  // Hidden entrance states are added only when this observer is ready.
  if (!reducedMotion.matches) {
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px 25px 0px' });
    document.querySelectorAll('.reveal').forEach(element => {
      element.classList.add('reveal-ready');
      revealObserver.observe(element);
    });
  }
  const links = Array.from(nav.querySelectorAll('a'));
  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(link => {
        if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-20% 0px -50% 0px' });
  ['inside', 'programs', 'tools', 'questions'].forEach(id => sectionObserver.observe(document.getElementById(id)));

  let heroInView = true;
  let purchaseInView = false;
  const mobileViewport = matchMedia('(max-width: 700px)');
  const mobileBar = $('#mobile-purchase');
  function updateMobileBar() {
    const show = mobileViewport.matches && !heroInView && !purchaseInView;
    mobileBar.hidden = !show;
    document.body.classList.toggle('mobile-bar-visible', show);
  }
  new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.target.matches('.hero-actions')) heroInView = entry.isIntersecting;
      else purchaseInView = entry.isIntersecting;
    });
    updateMobileBar();
  }).observe($('.hero-actions'));
  new IntersectionObserver(entries => {
    purchaseInView = entries[0].isIntersecting;
    updateMobileBar();
  }, { threshold: 0.05 }).observe($('#get-mdaar'));
  mobileViewport.addEventListener('change', updateMobileBar);
}

if (!reducedMotion.matches && matchMedia('(hover: hover) and (pointer: fine)').matches) {
  const stage = $('#hero-product');
  const book = $('#book-tilt');
  let frame;
  stage.addEventListener('pointermove', event => {
    if (frame) cancelAnimationFrame(frame);
    const box = stage.getBoundingClientRect();
    const x = (event.clientX - box.left) / box.width - 0.5;
    const y = (event.clientY - box.top) / box.height - 0.5;
    frame = requestAnimationFrame(() => {
      book.style.transform = `rotate(${-6 + x * 3}deg) rotateY(${x * 8}deg) rotateX(${-y * 5}deg)`;
    });
  });
  stage.addEventListener('pointerleave', () => {
    if (frame) cancelAnimationFrame(frame);
    book.style.transform = '';
  });
}

$('#footer-year').textContent = new Intl.DateTimeFormat('ar-SA-u-ca-gregory', { year: 'numeric' }).format(new Date());
