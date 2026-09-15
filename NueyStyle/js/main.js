/* i3Automations - NueyStyle
   Motion and behaviour: header, dock nav, mobile nav, accordion, reveal,
   counters, pinned journey, marquee, background video, smooth scroll. */

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const coarsePointer = window.matchMedia('(pointer: coarse)');
const narrowScreen = window.matchMedia('(max-width: 1023px)');
const saveData = navigator.connection && navigator.connection.saveData === true;
const slowNetwork = navigator.connection && /^(slow-2g|2g|3g)$/.test(navigator.connection.effectiveType || '');

function flatScroll(){
  return narrowScreen.matches || coarsePointer.matches || prefersReducedMotion.matches;
}

function videoAllowed(){
  return !prefersReducedMotion.matches && !saveData && !slowNetwork;
}

/* Scroll and resize plumbing --------------------------------------------- */

const scrollPainters = new Set();
let scrollFrame = 0;
let viewportHeight = window.innerHeight;

function runScrollPainters(){
  scrollFrame = 0;
  const offset = window.scrollY;
  scrollPainters.forEach(painter => painter(offset, viewportHeight));
}

function scheduleScroll(){
  if(!scrollFrame) scrollFrame = requestAnimationFrame(runScrollPainters);
}

function paintScrollNow(){
  if(scrollFrame) cancelAnimationFrame(scrollFrame);
  runScrollPainters();
}

function onScroll(painter){
  scrollPainters.add(painter);
  scheduleScroll();
  return () => scrollPainters.delete(painter);
}

const resizeHandlers = new Set();
let resizeTimer = 0;

function onResize(handler){
  resizeHandlers.add(handler);
  return () => resizeHandlers.delete(handler);
}

window.addEventListener('scroll', scheduleScroll, { passive:true });
window.addEventListener('resize', () => {
  viewportHeight = window.innerHeight;
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    resizeHandlers.forEach(handler => handler());
    scheduleScroll();
  }, 120);
}, { passive:true });

if(document.fonts && document.fonts.ready){
  document.fonts.ready.then(() => {
    resizeHandlers.forEach(handler => handler());
    scheduleScroll();
  });
}

/* Header ------------------------------------------------------------------ */

function setupHeaderState(){
  const header = document.querySelector('.site-header');
  const ctaBar = document.querySelector('.mobile-cta-bar');
  if(!header) return;

  let bands = [];

  const measure = () => {
    bands = Array.from(document.querySelectorAll('[data-immersive]')).map(element => ({
      top: element.offsetTop,
      bottom: element.offsetTop + element.offsetHeight
    }));
  };

  const covered = (offset) => bands.some(band => (
    band.top - offset <= 0 && band.bottom - offset > 80
  ));

  let lastScrolled = null;
  let lastHidden = null;
  let lastVisible = null;

  const update = (offset, height) => {
    const scrolled = String(offset > 80);
    const hidden = String((bands.length > 0 && offset < 80) || covered(offset));
    if(scrolled !== lastScrolled){ header.dataset.scrolled = scrolled; lastScrolled = scrolled; }
    if(hidden !== lastHidden){ header.dataset.hidden = hidden; lastHidden = hidden; }
    if(ctaBar){
      const visible = String(offset > height * 0.4);
      if(visible !== lastVisible){ ctaBar.dataset.visible = visible; lastVisible = visible; }
    }
  };

  measure();
  update(window.scrollY, viewportHeight);
  onScroll(update);
  onResize(measure);
}

/* Dock navigation --------------------------------------------------------- */

function setupDockNav(){
  const nav = document.querySelector('.header-nav');
  if(!nav) return;

  const links = Array.from(nav.querySelectorAll('a'));
  if(!links.length) return;

  const RANGE = 132;
  const SCALE = 0.22;
  const LIFT = 6;
  const DOT = 0.9;
  const desktop = window.matchMedia('(min-width:1024px)');

  const items = links.map(link => ({ link, center:0, current:0, target:0 }));
  let frame = 0;

  const clamp01 = (value) => Math.min(1, Math.max(0, value));

  const measure = () => {
    const base = nav.getBoundingClientRect().left - nav.offsetLeft;
    items.forEach(item => {
      item.center = base + item.link.offsetLeft + item.link.offsetWidth / 2;
    });
  };

  const paintItem = (item) => {
    const value = item.current;
    item.link.style.setProperty('--dock-scale', (1 + value * SCALE).toFixed(4));
    item.link.style.setProperty('--dock-lift', (-value * LIFT).toFixed(2) + 'px');
    item.link.style.setProperty('--dock-dot', (value * DOT).toFixed(3));
  };

  const paint = () => {
    frame = 0;
    let moving = false;
    items.forEach(item => {
      const delta = item.target - item.current;
      if(Math.abs(delta) > 0.0008){
        item.current += delta * 0.2;
        moving = true;
      } else {
        item.current = item.target;
      }
      paintItem(item);
    });
    if(moving) schedule();
  };

  function schedule(){
    if(!frame) frame = requestAnimationFrame(paint);
  }

  const aim = (pointerX) => {
    items.forEach(item => {
      const distance = clamp01(1 - Math.abs(pointerX - item.center) / RANGE);
      item.target = distance * distance * (3 - 2 * distance);
    });
    schedule();
  };

  const release = () => {
    items.forEach(item => { item.target = 0; });
    schedule();
  };

  const reset = () => {
    items.forEach(item => {
      item.current = 0;
      item.target = 0;
      item.link.style.removeProperty('--dock-scale');
      item.link.style.removeProperty('--dock-lift');
      item.link.style.removeProperty('--dock-dot');
    });
  };

  const onMove = (event) => {
    if(event.pointerType === 'touch') return;
    aim(event.clientX);
  };

  const bind = () => {
    measure();
    nav.addEventListener('pointerenter', measure);
    nav.addEventListener('pointermove', onMove);
    nav.addEventListener('pointerleave', release);
  };

  const unbind = () => {
    nav.removeEventListener('pointerenter', measure);
    nav.removeEventListener('pointermove', onMove);
    nav.removeEventListener('pointerleave', release);
    reset();
  };

  const sync = () => {
    if(desktop.matches && !prefersReducedMotion.matches) bind();
    else unbind();
  };

  sync();
  desktop.addEventListener('change', () => { unbind(); sync(); });
  prefersReducedMotion.addEventListener('change', () => { unbind(); sync(); });
  onResize(() => { if(desktop.matches) measure(); });
}

/* Mobile navigation ------------------------------------------------------- */

function setupMobileNav(){
  const nav = document.querySelector('.mobile-nav');
  const openButton = document.querySelector('.header-toggle');
  const closeButton = document.querySelector('.mobile-nav-close');
  if(!nav || !openButton || !closeButton) return;

  const scrim = nav.querySelector('[data-mobile-nav-scrim]');
  const links = Array.from(nav.querySelectorAll('a'));
  links.forEach((link, index) => { link.style.setProperty('--nav-index', String(index)); });
  links.forEach(link => {
    if(isCurrentPage(link)) link.setAttribute('aria-current', 'page');
  });

  let open = false;
  let restoreScroll = 0;

  const focusable = () => Array.from(
    nav.querySelectorAll('a[href], button:not([disabled])')
  ).filter(element => element.getClientRects().length > 0);

  const lock = () => {
    restoreScroll = window.scrollY;
    document.body.style.position = 'fixed';
    document.body.style.top = '-' + restoreScroll + 'px';
    document.body.style.left = '0';
    document.body.style.right = '0';
    document.body.style.width = '100%';
  };

  const unlock = () => {
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    document.body.style.width = '';
    window.scrollTo(0, restoreScroll);
  };

  const setOpen = (next) => {
    if(next === open) return;
    open = next;
    nav.dataset.open = String(open);
    openButton.setAttribute('aria-expanded', String(open));
    if(open){
      lock();
      nav.removeAttribute('inert');
      requestAnimationFrame(() => {
        if(open) closeButton.focus({ preventScroll:true });
      });
    } else {
      nav.setAttribute('inert', '');
      unlock();
      openButton.focus({ preventScroll:true });
    }
  };

  nav.setAttribute('inert', '');

  openButton.addEventListener('click', () => setOpen(true));
  closeButton.addEventListener('click', () => setOpen(false));
  if(scrim) scrim.addEventListener('click', () => setOpen(false));
  links.forEach(link => link.addEventListener('click', () => setOpen(false)));

  document.addEventListener('keydown', event => {
    if(!open) return;
    if(event.key === 'Escape'){
      setOpen(false);
      return;
    }
    if(event.key !== 'Tab') return;
    const stops = focusable();
    if(!stops.length) return;
    const first = stops[0];
    const last = stops[stops.length - 1];
    if(event.shiftKey && document.activeElement === first){
      event.preventDefault();
      last.focus();
    } else if(!event.shiftKey && document.activeElement === last){
      event.preventDefault();
      first.focus();
    }
  });

  narrowScreen.addEventListener('change', event => { if(!event.matches) setOpen(false); });
}

/* Accordion --------------------------------------------------------------- */

function setupAccordion(){
  document.querySelectorAll('[data-accordion]').forEach(group => {
    const items = Array.from(group.querySelectorAll('.accordion-item'));

    items.forEach(item => {
      const trigger = item.querySelector('.accordion-trigger');
      const panel = item.querySelector('.accordion-panel');
      if(!trigger || !panel) return;
      panel.inert = item.dataset.open !== 'true';

      trigger.addEventListener('click', () => {
        const willOpen = item.dataset.open !== 'true';
        items.forEach(other => {
          const otherTrigger = other.querySelector('.accordion-trigger');
          const otherPanel = other.querySelector('.accordion-panel');
          other.dataset.open = 'false';
          if(otherTrigger) otherTrigger.setAttribute('aria-expanded', 'false');
          if(otherPanel){ otherPanel.setAttribute('aria-hidden', 'true'); otherPanel.inert = true; }
        });
        item.dataset.open = String(willOpen);
        trigger.setAttribute('aria-expanded', String(willOpen));
        panel.setAttribute('aria-hidden', String(!willOpen));
        panel.inert = !willOpen;
      });
    });
  });
}

/* Reveal ------------------------------------------------------------------ */

function setupReveal(){
  const all = Array.from(document.querySelectorAll('.reveal'));
  if(!all.length) return;

  const show = (element) => {
    const index = Number(element.dataset.revealIndex || 0);
    if(index) element.style.setProperty('--reveal-delay', (index * 60) + 'ms');
    element.dataset.visible = 'true';
  };

  if(prefersReducedMotion.matches || !('IntersectionObserver' in window)){
    all.forEach(show);
    return;
  }

  const groups = Array.from(document.querySelectorAll('[data-reveal-group]'));
  const solo = all.filter(element => !element.closest('[data-reveal-group]'));

  const soloObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(!entry.isIntersecting) return;
      show(entry.target);
      soloObserver.unobserve(entry.target);
    });
  }, { threshold:0.2, rootMargin:'0px 0px -8% 0px' });

  solo.forEach(element => soloObserver.observe(element));

  if(!groups.length) return;

  const groupObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(!entry.isIntersecting) return;
      entry.target.querySelectorAll('.reveal').forEach(show);
      groupObserver.unobserve(entry.target);
    });
  }, { threshold:0, rootMargin:'0px 0px -12% 0px' });

  groups.forEach(group => groupObserver.observe(group));
}

/* Counters ---------------------------------------------------------------- */

function formatNumber(value){
  return new Intl.NumberFormat('en-US').format(Math.round(value));
}

function setupCounters(){
  const counters = document.querySelectorAll('[data-count-to]');
  if(!counters.length) return;

  const run = (element) => {
    const target = Number(element.dataset.countTo);
    const suffix = element.dataset.countSuffix || '';
    if(prefersReducedMotion.matches){
      element.textContent = formatNumber(target) + suffix;
      return;
    }
    const start = target * 0.6;
    const duration = 1100;
    const startedAt = performance.now();

    const step = (now) => {
      const progress = Math.min(1, (now - startedAt) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = formatNumber(start + (target - start) * eased) + suffix;
      if(progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  if(!('IntersectionObserver' in window)){
    counters.forEach(run);
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(!entry.isIntersecting) return;
      run(entry.target);
      observer.unobserve(entry.target);
    });
  }, { threshold:0.6 });

  counters.forEach(counter => observer.observe(counter));
}

/* Background video -------------------------------------------------------- */

function playVideo(video){
  if(!video) return;
  const resumed = video.play();
  if(resumed && typeof resumed.catch === 'function') resumed.catch(() => {});
}

function startBackgroundVideo(video){
  if(!video || video.dataset.started === 'true') return;
  video.dataset.started = 'true';
  video.addEventListener('canplay', () => { video.dataset.ready = 'true'; }, { once:true });
  video.load();
  playVideo(video);
}

function setupBackgroundVideo(){
  const videos = Array.from(document.querySelectorAll('[data-video]'));
  if(!videos.length) return;

  if(!videoAllowed()){
    videos.forEach(video => { video.removeAttribute('autoplay'); });
    return;
  }

  videos.forEach(video => {
    if(video.dataset.video === 'eager'){
      startBackgroundVideo(video);
      return;
    }
    if(!('IntersectionObserver' in window)){
      startBackgroundVideo(video);
      return;
    }
    const holder = video.closest('section') || video.parentElement;
    const loader = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if(!entry.isIntersecting) return;
        startBackgroundVideo(video);
        loader.disconnect();
      });
    }, { rootMargin:'30% 0px' });
    loader.observe(holder);
  });

  if(!('IntersectionObserver' in window)) return;

  const player = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const video = entry.target;
      if(video.dataset.started !== 'true') return;
      if(entry.isIntersecting){
        if(video.dataset.paused !== 'true') playVideo(video);
      } else {
        video.pause();
      }
    });
  }, { threshold:0.15 });

  videos.forEach(video => player.observe(video));

  document.addEventListener('visibilitychange', () => {
    if(!document.hidden) return;
    videos.forEach(video => video.pause());
  });
}

function setupPauseButtons(){
  document.querySelectorAll('[data-pause-target]').forEach(button => {
    const video = document.getElementById(button.dataset.pauseTarget);
    if(!video){ button.hidden = true; return; }
    if(!videoAllowed()){ button.hidden = true; return; }

    const label = (paused) => {
      button.setAttribute('aria-pressed', String(paused));
      button.setAttribute('aria-label', paused ? 'Play background video' : 'Pause background video');
    };

    button.addEventListener('click', () => {
      if(video.paused){
        video.dataset.paused = 'false';
        startBackgroundVideo(video);
        playVideo(video);
      } else {
        video.dataset.paused = 'true';
        video.pause();
      }
    });

    video.addEventListener('play', () => label(false));
    video.addEventListener('playing', () => label(false));
    video.addEventListener('pause', () => label(true));
    label(video.paused);
  });
}

/* Pinned journey ---------------------------------------------------------- */

function setupJourney(){
  const section = document.querySelector('[data-journey]');
  if(!section) return;

  const stages = Array.from(section.querySelectorAll('.journey-stage'));
  const video = section.querySelector('[data-journey-video]');
  if(!stages.length) return;

  const loadJourneyVideo = () => {
    if(!video || !videoAllowed()) return;
    startBackgroundVideo(video);
  };

  if(prefersReducedMotion.matches){
    stages.forEach(stage => { stage.dataset.active = 'true'; });
    if(video) video.remove();
    return;
  }

  if(flatScroll()){
    section.dataset.motion = 'light';
    stages.forEach(stage => { stage.dataset.active = 'true'; });
    loadJourneyVideo();
    return;
  }

  const PANEL_TILT = 42;
  const PANEL_BLUR = 4;
  const PANEL_DEPTH = 150;
  const PANEL_DIM = 0.34;
  const PANEL_SHIFT_X = 10;
  const PANEL_ROLL = 2.5;
  const PANEL_SKEW = 5;
  const PANEL_FADE = 0.32;
  const PANEL_LIFT = 26;

  const sideOf = (stage) => {
    if(stage.classList.contains('stage-left')) return -1;
    if(stage.classList.contains('stage-right')) return 1;
    return 0;
  };

  const windows = stages.map(stage => ({
    element: stage,
    from: Number(stage.dataset.in || 0),
    to: Number(stage.dataset.out || 1),
    side: sideOf(stage)
  }));

  const clamp01 = (value) => Math.min(1, Math.max(0, value));
  const ramp = (value, a, b) => {
    const t = clamp01((value - a) / (b - a));
    return t * t * (3 - 2 * t);
  };

  let target = 0;
  let eased = 0;
  let looping = false;
  let sectionTop = 0;
  let sectionSpan = 0;

  const stageBox = section.querySelector('.journey-viewport');

  const measure = () => {
    sectionTop = section.offsetTop;
    sectionSpan = section.offsetHeight - (stageBox ? stageBox.offsetHeight : viewportHeight);
  };

  const progressAt = (offset) => {
    if(sectionSpan <= 0) return 0;
    return Math.min(1, Math.max(0, (offset - sectionTop) / sectionSpan));
  };

  const paint = (value) => {
    windows.forEach(entry => {
      const appearing = ramp(value, entry.from, entry.from + 0.10);
      const leaving = ramp(value, entry.to, entry.to + 0.10);
      const opacity = appearing * (1 - leaving);
      const shift = (1 - appearing) * 30 - leaving * 48;
      const phase = leaving - (1 - appearing);
      const away = Math.abs(phase);
      const softened = away * away * (3 - 2 * away);
      const side = entry.side;

      entry.element.style.setProperty('--stage-opacity', opacity.toFixed(3));
      entry.element.dataset.active = String(opacity > 0.6);
      entry.element.style.setProperty('--stage-shift', shift.toFixed(1) + 'px');
      entry.element.style.setProperty('--panel-blur', (softened * PANEL_BLUR).toFixed(2) + 'px');
      entry.element.style.setProperty('--panel-bright', (1 - softened * PANEL_DIM).toFixed(3));
      entry.element.style.setProperty('--panel-sat', (1 - softened * PANEL_DIM).toFixed(3));
      entry.element.style.setProperty('--panel-fade', (1 - softened * PANEL_FADE).toFixed(3));
      entry.element.style.setProperty('--panel-lift', (PANEL_LIFT - softened * PANEL_LIFT * 0.6).toFixed(1) + 'px');
      entry.element.style.setProperty('--panel-transform',
        'translate3d(' + (side * softened * PANEL_SHIFT_X).toFixed(2) + '%, 0, ' + (softened * PANEL_DEPTH).toFixed(1) + 'px)' +
        ' rotateX(' + (-phase * PANEL_TILT).toFixed(2) + 'deg)' +
        ' rotateZ(' + (side * phase * PANEL_ROLL).toFixed(2) + 'deg)' +
        ' skewX(' + (-side * phase * PANEL_SKEW).toFixed(2) + 'deg)');
    });
  };

  const tick = () => {
    const gap = target - eased;
    if(Math.abs(gap) > 0.14) eased = target - Math.sign(gap) * 0.14;
    const delta = target - eased;
    eased = Math.abs(delta) < 0.0004 ? target : eased + delta * 0.22;
    paint(eased);
    if(looping) requestAnimationFrame(tick);
  };

  const startLoop = () => {
    if(looping) return;
    looping = true;
    requestAnimationFrame(tick);
  };

  const stopLoop = () => {
    looping = false;
    eased = target;
    paint(eased);
  };

  const update = (offset) => {
    target = progressAt(offset);
    if(!looping) paint(target);
  };

  measure();
  update(window.scrollY);
  eased = target;
  onScroll(update);
  onResize(() => { measure(); update(window.scrollY); });

  if(!('IntersectionObserver' in window)){
    loadJourneyVideo();
    startLoop();
    return;
  }

  const preloader = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(!entry.isIntersecting) return;
      loadJourneyVideo();
      preloader.disconnect();
    });
  }, { rootMargin:'50% 0px' });
  preloader.observe(section);

  const runner = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        startLoop();
        if(video && video.dataset.started === 'true' && video.paused) playVideo(video);
      } else {
        stopLoop();
        if(video) video.pause();
      }
    });
  }, { rootMargin:'10% 0px' });
  runner.observe(section);
}

/* Marquee ----------------------------------------------------------------- */

function setupMarquee(){
  const track = document.querySelector('.marquee-track');
  if(!track) return;

  const seed = track.querySelector('.marquee-group');
  if(!seed) return;

  const PIXELS_PER_SECOND = 34;

  const fit = () => {
    const groupWidth = seed.getBoundingClientRect().width;
    if(!groupWidth) return;

    const needed = Math.ceil(window.innerWidth / groupWidth) + 1;
    let groups = track.querySelectorAll('.marquee-group').length;

    while(groups < needed){
      const clone = seed.cloneNode(true);
      clone.setAttribute('aria-hidden', 'true');
      track.appendChild(clone);
      groups += 1;
    }

    while(groups > needed && track.lastElementChild !== seed){
      track.lastElementChild.remove();
      groups -= 1;
    }

    track.style.setProperty('--marquee-shift', groupWidth + 'px');
    track.style.animationDuration = (groupWidth / PIXELS_PER_SECOND).toFixed(2) + 's';
  };

  fit();
  onResize(fit);
}

/* Storage notice and year ------------------------------------------------- */

function setupYear(){
  const year = String(new Date().getFullYear());
  document.querySelectorAll('[data-year]').forEach(element => { element.textContent = year; });
}

function setupNotice(){
  const notice = document.getElementById('storage-notice');
  if(!notice) return;

  const KEY = 'i3-notice';
  let dismissed = false;
  try { dismissed = window.localStorage.getItem(KEY) === '1'; } catch (error) { dismissed = false; }
  if(dismissed) return;

  const button = notice.querySelector('[data-notice-ok]');
  setTimeout(() => {
    notice.hidden = false;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { notice.dataset.visible = 'true'; });
    });
  }, 1400);

  if(!button) return;
  button.addEventListener('click', () => {
    try { window.localStorage.setItem(KEY, '1'); } catch (error) { /* private mode */ }
    notice.dataset.visible = 'false';
    if(prefersReducedMotion.matches){ notice.hidden = true; return; }
    setTimeout(() => { notice.hidden = true; }, 400);
  });
}

/* Smooth wheel scrolling -------------------------------------------------- */

function setupSmoothScroll(){
  if(prefersReducedMotion.matches) return;
  if(!window.matchMedia('(pointer: fine)').matches) return;

  const LERP = 0.11;
  const WHEEL_FLOOR = 50;
  const FRAME = 1000 / 60;
  const root = document.documentElement;

  let target = window.scrollY;
  let running = false;
  let predicted = -1;
  let last = 0;
  let limit = 0;

  const measureLimit = () => { limit = Math.max(0, root.scrollHeight - viewportHeight); };

  measureLimit();
  onResize(() => {
    measureLimit();
    if(!running) target = window.scrollY;
  });

  const toPixels = (event) => {
    if(event.deltaMode === 1) return event.deltaY * 16;
    if(event.deltaMode === 2) return event.deltaY * viewportHeight;
    return event.deltaY;
  };

  const hasScrollableAncestor = (node, direction) => {
    while(node && node !== document.body && node !== root){
      if(node.scrollHeight > node.clientHeight + 1){
        const overflow = window.getComputedStyle(node).overflowY;
        if(overflow === 'auto' || overflow === 'scroll'){
          const max = node.scrollHeight - node.clientHeight;
          if(direction < 0 && node.scrollTop > 0) return true;
          if(direction > 0 && node.scrollTop < max - 1) return true;
        }
      }
      node = node.parentElement;
    }
    return false;
  };

  const stop = () => {
    running = false;
    last = 0;
    predicted = -1;
    root.style.scrollBehavior = '';
  };

  const step = (now) => {
    const delta = last ? Math.min(now - last, 64) : FRAME;
    last = now;
    const factor = 1 - Math.pow(1 - LERP, delta / FRAME);
    const current = window.scrollY;
    if(predicted >= 0 && Math.abs(current - predicted) > 4) target = current;
    if(Math.abs(target - current) < 0.5){
      stop();
      paintScrollNow();
      return;
    }
    const next = current + (target - current) * factor;
    predicted = Math.round(next);
    window.scrollTo(0, next);
    paintScrollNow();
    window.requestAnimationFrame(step);
  };

  window.addEventListener('wheel', (event) => {
    if(event.ctrlKey) return;
    const distance = toPixels(event);
    if(!distance || Math.abs(distance) < WHEEL_FLOOR) return;
    if(hasScrollableAncestor(event.target, distance)) return;
    event.preventDefault();
    if(!running) target = window.scrollY;
    measureLimit();
    target = Math.max(0, Math.min(limit, target + distance));
    if(!running){
      running = true;
      last = 0;
      predicted = -1;
      root.style.scrollBehavior = 'auto';
      window.requestAnimationFrame(step);
    }
  }, { passive:false });

  onScroll(() => {
    if(!running) target = window.scrollY;
  });
}

/* Current page ------------------------------------------------------------ */

function pageSlug(value){
  const last = (value || '').split('#')[0].split('?')[0].split('/').pop().toLowerCase();
  if(!last || last === 'index.html' || last === 'index') return 'index';
  return last.replace(/\.html$/, '');
}

function isCurrentPage(link){
  const href = link.getAttribute('href') || '';
  if(!href || href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('tel:')) return false;
  return pageSlug(href) === pageSlug(location.pathname);
}

function markCurrentPage(){
  document.querySelectorAll('.header-nav a').forEach(link => {
    if(isCurrentPage(link)) link.setAttribute('aria-current', 'page');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  markCurrentPage();
  setupHeaderState();

  setupMobileNav();
  setupAccordion();
  const linkedAccordion = document.getElementById(location.hash.slice(1));
  if(linkedAccordion && linkedAccordion.classList.contains('accordion-trigger') && linkedAccordion.getAttribute('aria-expanded') === 'false') linkedAccordion.click();
  setupReveal();
  setupCounters();
  setupPauseButtons();
  setupBackgroundVideo();
  setupJourney();
  setupMarquee();
  setupYear();


});
