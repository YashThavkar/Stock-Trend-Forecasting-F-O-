(function () {
  const SECTION_ORDER = ["overview", "interactive-demo", "demo", "method"];
  const OFFSET = 110;

  function updateActiveNav() {
    const pills = document.querySelectorAll(".js-nav-pill[data-section]");
    let active = SECTION_ORDER[0];
    for (let i = SECTION_ORDER.length - 1; i >= 0; i--) {
      const id = SECTION_ORDER[i];
      const el = document.getElementById(id);
      if (!el) continue;
      const top = el.getBoundingClientRect().top;
      if (top <= OFFSET) {
        active = id;
        break;
      }
    }
    pills.forEach((a) => {
      const on = a.dataset.section === active;
      a.classList.toggle("nav__pill--active", on);
      if (on) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    });
  }

  let ticking = false;
  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        updateActiveNav();
        ticking = false;
      });
      ticking = true;
    }
  }

  function initReveal() {
    const sections = document.querySelectorAll("main > section");
    if (!sections.length || !("IntersectionObserver" in window)) {
      sections.forEach((s) => s.classList.add("is-revealed"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) en.target.classList.add("is-revealed");
        });
      },
      { threshold: 0.06, rootMargin: "0px 0px -8% 0px" }
    );
    sections.forEach((sec) => {
      sec.classList.add("section-reveal");
      io.observe(sec);
    });
  }

  function init() {
    updateActiveNav();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", updateActiveNav, { passive: true });
    window.addEventListener("load", updateActiveNav, { passive: true });
    initReveal();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
