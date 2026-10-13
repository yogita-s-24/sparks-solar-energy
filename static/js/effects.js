/* Extra motion: scroll progress, back-to-top, counting prices, word-by-word
   headings, card tilt with a light glow, and magnetic buttons.
   Everything decorative is skipped when the visitor prefers reduced motion. */
(() => {
  const doc = document.documentElement;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ---- Scroll progress bar + back-to-top ------------------------------- */
  const bar = document.querySelector("[data-scroll-progress]");
  const topBtn = document.querySelector("[data-back-to-top]");
  let ticking = false;
  const onScroll = () => {
    const max = doc.scrollHeight - window.innerHeight;
    const progress = max > 0 ? Math.min(1, window.scrollY / max) : 0;
    if (bar) bar.style.transform = `scaleX(${progress.toFixed(4)})`;
    if (topBtn) {
      topBtn.style.setProperty("--p", progress.toFixed(4));
      topBtn.classList.toggle("is-shown", window.scrollY > window.innerHeight * 0.8);
    }
    ticking = false;
  };
  const requestScroll = () => {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(onScroll);
    }
  };
  window.addEventListener("scroll", requestScroll, { passive: true });
  window.addEventListener("resize", requestScroll, { passive: true });
  onScroll();
  if (topBtn) {
    topBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" }));
  }

  if (reduceMotion || !("IntersectionObserver" in window)) return;

  const whenVisible = (elements, callback, threshold = 0.3) => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            callback(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold }
    );
    elements.forEach((el) => io.observe(el));
  };

  /* ---- Prices count up when they scroll into view ---------------------- */
  const fmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
  const counters = Array.from(document.querySelectorAll("[data-count]"));
  counters.forEach((el) => (el.textContent = "0"));
  whenVisible(counters, (el) => {
    const target = Number(el.dataset.count) || 0;
    const duration = 1400;
    const start = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = fmt.format(Math.round(target * eased));
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, 0.6);

  /* ---- Section headings rise word by word ------------------------------ */
  const titles = Array.from(document.querySelectorAll(".section-title")).filter((h) => !h.children.length);
  titles.forEach((title) => {
    const words = title.textContent.trim().split(/\s+/);
    title.textContent = "";
    words.forEach((word, i) => {
      const outer = document.createElement("span");
      outer.className = "word";
      const inner = document.createElement("span");
      inner.textContent = word;
      inner.style.setProperty("--i", i);
      outer.appendChild(inner);
      title.appendChild(outer);
      if (i < words.length - 1) title.appendChild(document.createTextNode(" "));
    });
    title.classList.add("split-words");
  });
  whenVisible(titles, (title) => title.classList.add("words-in"), 0.4);

  if (!finePointer) return;

  /* ---- Card tilt with a glow that follows the pointer ------------------ */
  document.querySelectorAll("[data-tilt]").forEach((card) => {
    card.classList.add("tilt-card");
    let settle = null;
    card.addEventListener("pointerenter", () => {
      window.clearTimeout(settle);
      card.classList.add("is-tilting");
    });
    card.addEventListener("pointermove", (e) => {
      const box = card.getBoundingClientRect();
      const x = (e.clientX - box.left) / box.width;
      const y = (e.clientY - box.top) / box.height;
      card.style.setProperty("--mx", `${(x * 100).toFixed(1)}%`);
      card.style.setProperty("--my", `${(y * 100).toFixed(1)}%`);
      card.style.transform =
        `perspective(1000px) rotateX(${((0.5 - y) * 7).toFixed(2)}deg) rotateY(${((x - 0.5) * 7).toFixed(2)}deg) translateY(-4px)`;
    });
    card.addEventListener("pointerleave", () => {
      card.style.transform = "";
      settle = window.setTimeout(() => card.classList.remove("is-tilting"), 400);
    });
  });

  /* ---- Magnetic buttons ------------------------------------------------- */
  document.querySelectorAll("[data-magnetic]").forEach((btn) => {
    btn.addEventListener("pointermove", (e) => {
      const box = btn.getBoundingClientRect();
      const dx = e.clientX - (box.left + box.width / 2);
      const dy = e.clientY - (box.top + box.height / 2);
      btn.style.transform = `translate(${(dx * 0.18).toFixed(1)}px, ${(dy * 0.28 - 2).toFixed(1)}px)`;
    });
    btn.addEventListener("pointerleave", () => {
      btn.style.transform = "";
    });
  });
})();
