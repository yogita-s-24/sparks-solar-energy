/* Navigation, mobile menu, enquiry links, accordions, gallery filter and form states. */
(() => {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Navbar background on scroll ------------------------------------- */
  const nav = document.getElementById("site-nav");
  const setNavState = () => nav && nav.classList.toggle("is-scrolled", window.scrollY > 24);
  setNavState();
  window.addEventListener("scroll", setNavState, { passive: true });

  /* ---- Mobile menu ----------------------------------------------------- */
  const toggle = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-mobile-menu]");
  const setMenu = (open) => {
    if (!toggle || !menu) return;
    menu.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? toggle.dataset.labelClose || "Close menu" : toggle.dataset.labelOpen || "Open menu");
    document.body.style.overflow = open ? "hidden" : "";
    if (open) nav.classList.add("is-scrolled");
    else setNavState();
  };
  if (toggle && menu) {
    toggle.addEventListener("click", () => setMenu(!menu.classList.contains("is-open")));
    menu.querySelectorAll("[data-menu-link]").forEach((link) => link.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && menu.classList.contains("is-open")) {
        setMenu(false);
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 1024px)").addEventListener("change", (e) => e.matches && setMenu(false));
  }

  /* ---- Enquiry links: scroll to the on-page form and pre-fill it -------- */
  const form = document.querySelector("[data-enquiry-form]");
  document.addEventListener("click", (e) => {
    const link = e.target.closest("[data-enquire]");
    if (!link || !form) return;
    e.preventDefault();
    const type = link.dataset.enquire;
    const select = form.querySelector("select[name='property_type']");
    if (type && select) select.value = type;
    const bill = link.dataset.bill;
    const billInput = form.querySelector("input[name='monthly_bill']");
    if (bill && billInput && !billInput.value) billInput.value = bill;
    const target = document.getElementById("enquiry") || form;
    target.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    const first = form.querySelector("input[name='name']");
    if (first) window.setTimeout(() => first.focus({ preventScroll: true }), reduceMotion ? 0 : 700);
  });

  /* ---- Accordions (FAQ + benefits explorer) ---------------------------- */
  const setupAccordion = (itemSelector, openClass) => {
    const items = Array.from(document.querySelectorAll(itemSelector));
    items.forEach((item) => {
      const button = item.querySelector("button[aria-controls]");
      if (!button) return;
      button.addEventListener("click", () => {
        const willOpen = !item.classList.contains(openClass);
        items.forEach((other) => {
          other.classList.remove(openClass);
          const b = other.querySelector("button[aria-controls]");
          if (b) b.setAttribute("aria-expanded", "false");
        });
        if (willOpen) {
          item.classList.add(openClass);
          button.setAttribute("aria-expanded", "true");
        }
      });
    });
  };
  setupAccordion("[data-faq]", "is-open");
  setupAccordion("[data-benefit]", "is-active");

  /* ---- Gallery filter -------------------------------------------------- */
  const gallery = document.querySelector("[data-gallery]");
  const filterButtons = document.querySelectorAll("[data-filter]");
  if (gallery && filterButtons.length) {
    const items = Array.from(gallery.querySelectorAll("[data-category]"));
    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.dataset.filter;
        filterButtons.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
        items.forEach((item) => {
          const show = filter === "all" || item.dataset.category === filter;
          if (show) {
            item.hidden = false;
            item.classList.add("is-visible");
            requestAnimationFrame(() => item.classList.remove("is-hiding"));
          } else {
            item.classList.add("is-hiding");
            window.setTimeout(() => {
              if (item.classList.contains("is-hiding")) item.hidden = true;
            }, reduceMotion ? 0 : 400);
          }
        });
      });
    });
  }

  /* ---- Enquiry form: client check + loading state ---------------------- */
  document.querySelectorAll("[data-enquiry-form]").forEach((f) => {
    f.addEventListener("submit", (e) => {
      const submit = f.querySelector("[data-submit]");
      if (submit && submit.disabled) {
        e.preventDefault(); // already sending: ignore double clicks
        return;
      }
      if (!f.checkValidity()) {
        e.preventDefault();
        f.reportValidity();
        return;
      }
      if (submit) {
        submit.disabled = true;
        submit.classList.add("is-loading");
        submit.setAttribute("aria-busy", "true");
      }
    });
  });
  // Reset buttons if the page is restored from the back/forward cache.
  window.addEventListener("pageshow", () => {
    document.querySelectorAll("[data-submit]").forEach((b) => {
      b.disabled = false;
      b.classList.remove("is-loading");
      b.removeAttribute("aria-busy");
    });
  });
})();
