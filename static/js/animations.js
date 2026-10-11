/* Scroll reveals, timeline progress and parallax.
   Uses IntersectionObserver + requestAnimationFrame only; respects reduced motion. */
(() => {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Reveal on scroll ------------------------------------------------ */
  const observed = document.querySelectorAll("[data-reveal], [data-timeline], [data-observe]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    root.classList.add("reveal-ready");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );
    observed.forEach((el) => io.observe(el));
  } else {
    observed.forEach((el) => el.classList.add("is-visible"));
  }

  /* ---- Sun arc (SVG SMIL): freeze at midday for reduced motion ---------- */
  if (reduceMotion) {
    document.querySelectorAll("svg[data-sun-arc]").forEach((svg) => {
      if (typeof svg.pauseAnimations === "function") {
        svg.setCurrentTime(2.5);
        svg.pauseAnimations();
      }
    });
  }

  /* ---- Parallax --------------------------------------------------------- */
  const layers = Array.from(document.querySelectorAll("[data-parallax]"));
  if (!layers.length || reduceMotion) return;

  let ticking = false;
  const update = () => {
    const vh = window.innerHeight;
    layers.forEach((layer) => {
      const box = layer.parentElement.getBoundingClientRect();
      if (box.bottom < -100 || box.top > vh + 100) return;
      const speed = parseFloat(layer.dataset.parallax) || 0.2;
      const limit = box.height * 0.1;
      const centreOffset = box.top + box.height / 2 - vh / 2;
      const y = Math.max(-limit, Math.min(limit, -centreOffset * speed));
      layer.style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`;
    });
    ticking = false;
  };
  const onScroll = () => {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  update();
})();
