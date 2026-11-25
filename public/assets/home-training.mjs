// "Gym | Home" switch for the training tab. Home plans come from /data/home-exercises.json (book "Home edition").
const host = document.getElementById('t-training');
if (host) {
  const wrap = document.createElement('div');
  wrap.id = 'training-home-wrap';
  wrap.hidden = true;
  wrap.innerHTML = `<div class="training-mode" role="group" aria-label="مكان التمرين">
    <button class="mini" type="button" data-mode="gym" aria-pressed="true">النادي</button>
    <button class="mini g" type="button" data-mode="home" aria-pressed="false">البيت</button></div>
    <section id="home-training" class="home-training" hidden aria-live="polite"></section>`;
  host.before(wrap);
  const panel = wrap.querySelector('#home-training');
  let data = null, program = '3', day = 0, mode = 'gym';
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const safeUrl = u => /^https:\/\/(www\.)?youtube\.com\//.test(u) ? u : '#';
  function variant(ex, key, title) {
    const v = ex[key], tag = key === 'with' ? 'بدمبل' : 'بدون دمبل';
    return `<div class="home-version"><span class="tag">${tag}</span><h4>${esc(v.label)}</h4>
      <a class="home-figure" href="${esc(safeUrl(v.video))}" target="_blank" rel="noopener noreferrer" aria-label="افتح مقطع شرح ${esc(title)}، ${tag}، ${esc(v.label)}">
      <img src="${esc(v.image)}" alt="رسم يوضح ${esc(ex.name)}، ${tag}، ${esc(v.label)}" loading="lazy" width="320" height="220"></a>
      <p class="note">${esc(ex.sets)} × ${esc(ex.reps)} · راحة ${esc(ex.rest)} ث</p><p>${esc(v.cue)}</p></div>`;
  }
  function render() {
    if (!data) { panel.textContent = 'جارٍ تحميل تمارين البيت…'; return; }
    const days = data.programs[program];
    const d = days[day] || days[0];
    panel.innerHTML = `<div class="head"><p class="eyebrow">HOME EDITION</p><h2>تمارين البيت</h2><p>لكل تمرين نسختان: بدمبل أو بدون. اختر وحدة وكمّل عليها. اضغط صورة التمرين لفتح مقطع الشرح على يوتيوب.</p></div>
      <div class="training-week" role="group" aria-label="عدد أيام البرنامج">${Object.keys(data.programs).map(p => `<button class="mini ${p === program ? '' : 'g'}" type="button" data-program="${p}" aria-pressed="${p === program}">${p} أيام</button>`).join('')}</div>
      <div class="training-week" role="group" aria-label="أيام البرنامج">${days.map((x, i) => `<button class="mini ${i === day ? '' : 'g'}" type="button" data-day="${i}" aria-pressed="${i === day}">${i + 1} · ${esc(x.name)}</button>`).join('')}</div>
      <div class="training-exercises">${d.exercises.map(id => { const ex = data.exercises[id]; return `<article class="card training-exercise"><h3>${esc(ex.title)} <small>${esc(ex.name)}</small></h3><div class="home-versions">${variant(ex, 'with', ex.title)}${variant(ex, 'without', ex.title)}</div></article>`; }).join('')}</div>
      <p class="note">الجرعات مقترحة للتوعية العامة وليست وصفة طبية. توقف عند ألم حاد أو دوخة، واستشر مختصاً إذا عندك حالة صحية. المقاطع من يوتيوب ومالكوها غير مدار.</p>`;
  }
  async function load() {
    if (data) return;
    try { const r = await fetch('/data/home-exercises.json'); if (!r.ok) throw new Error(); data = await r.json(); }
    catch { panel.textContent = 'تعذر تحميل تمارين البيت. تحقق من الاتصال وأعد المحاولة.'; return; }
    render();
  }
  function setMode(m) {
    mode = m;
    wrap.querySelectorAll('[data-mode]').forEach(b => { const on = b.dataset.mode === m; b.classList.toggle('g', !on); b.setAttribute('aria-pressed', String(on)); });
    document.body.dataset.trainingMode = m;
    panel.hidden = m !== 'home';
    if (m === 'home') { render(); load(); }
  }
  wrap.addEventListener('click', e => {
    const m = e.target.closest('[data-mode]'); if (m) return setMode(m.dataset.mode);
    const p = e.target.closest('[data-program]'); if (p) { program = p.dataset.program; day = 0; return render(); }
    const d = e.target.closest('[data-day]'); if (d) { day = Number(d.dataset.day); render(); }
  });
  new MutationObserver(() => { wrap.hidden = host.hidden; }).observe(host, { attributes: true, attributeFilter: ['hidden'] });
  wrap.hidden = host.hidden;
}
