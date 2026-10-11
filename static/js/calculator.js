/* Illustrative solar savings estimator.
   Assumptions come from CALCULATOR in config.py (rendered into data-calculator).
   Results are indicative only and never a quotation. */
(() => {
  const root = document.querySelector("[data-calculator]");
  if (!root) return;

  let cfg;
  try {
    cfg = JSON.parse(root.dataset.calculator);
  } catch (err) {
    return;
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (sel) => root.querySelector(sel);
  const billInput = $("[data-calc-bill]");
  const range = $("[data-calc-range]");
  const kwhInput = $("[data-calc-kwh]");
  const errorEl = $("[data-calc-error]");
  const assumptionEl = $("[data-calc-assumption]");
  const out = {
    annual: $("[data-out='annual']"),
    range: $("[data-out='range']"),
    bar: $("[data-out='bar']"),
    rate: $("[data-out='rate']"),
  };
  const cta = $("[data-calc-cta]");
  const ctaPath = cta ? cta.pathname : "/contact";
  const typeInputs = Array.from(root.querySelectorAll("[data-calc-type]"));
  root.querySelector("[data-calc-form]").addEventListener("submit", (e) => e.preventDefault());

  const fmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
  const rupees = (n) => "₹" + fmt.format(Math.round(n));
  const roundTo = (n, step) => Math.round(n / step) * step;
  const pct = (n) => Math.round(n * 100);

  let shown = { annual: 0, low: 0, high: 0 };
  let frame = null;

  const render = (v) => {
    out.annual.textContent = rupees(v.annual);
    out.range.textContent = `${rupees(v.low)} – ${rupees(v.high)}`;
  };

  const animateTo = (target) => {
    if (frame) cancelAnimationFrame(frame);
    if (reduceMotion) {
      shown = target;
      render(target);
      return;
    }
    const from = { ...shown };
    const start = performance.now();
    const duration = 650;
    const step = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const e = 1 - Math.pow(1 - t, 3);
      shown = {
        annual: from.annual + (target.annual - from.annual) * e,
        low: from.low + (target.low - from.low) * e,
        high: from.high + (target.high - from.high) * e,
      };
      render(shown);
      frame = t < 1 ? requestAnimationFrame(step) : null;
    };
    frame = requestAnimationFrame(step);
  };

  const selectedType = () => {
    const checked = typeInputs.find((i) => i.checked);
    return checked ? checked.value : Object.keys(cfg.property_types)[0];
  };

  const setRangeFill = () => {
    const min = Number(range.min);
    const max = Number(range.max);
    const fill = ((Number(range.value) - min) / (max - min)) * 100;
    range.style.setProperty("--fill", `${Math.max(0, Math.min(100, fill))}%`);
  };

  const showError = (message) => {
    errorEl.textContent = message;
    errorEl.classList.toggle("hidden", !message);
    billInput.classList.toggle("has-error", Boolean(message));
  };

  const update = ({ source = "", strict = false } = {}) => {
    const bill = Number(billInput.value);
    const valid = billInput.value !== "" && Number.isFinite(bill) && bill >= cfg.min_bill && bill <= cfg.max_bill;
    if (!valid) {
      if (strict) showError(`Please enter a monthly bill between ₹${fmt.format(cfg.min_bill)} and ₹${fmt.format(cfg.max_bill)}.`);
      return;
    }
    showError("");

    if (source !== "range") range.value = Math.min(bill, cfg.slider_max);
    setRangeFill();

    const typeKey = selectedType();
    const type = cfg.property_types[typeKey];
    const annual = bill * 12;
    const low = roundTo(annual * type.offset_low, 100);
    const high = roundTo(annual * type.offset_high, 100);
    animateTo({ annual, low, high });

    out.bar.style.left = `${pct(type.offset_low)}%`;
    out.bar.style.width = `${pct(type.offset_high - type.offset_low)}%`;
    assumptionEl.textContent =
      `Assumption used: a suitably sized system might offset roughly ${pct(type.offset_low)}–${pct(type.offset_high)}% ` +
      `of a typical ${type.label.toLowerCase()} bill. This is an illustrative assumption, not a promise.`;

    const kwh = Number(kwhInput.value);
    if (kwhInput.value !== "" && Number.isFinite(kwh) && kwh > 0) {
      const rate = bill / kwh;
      out.rate.textContent =
        `From your figures, you currently pay about ₹${rate.toFixed(2)} per unit and use roughly ` +
        `${fmt.format(kwh * 12)} units a year. Useful information for planning a system size.`;
      out.rate.classList.remove("hidden");
    } else {
      out.rate.classList.add("hidden");
    }

    if (cta) {
      cta.dataset.enquire = typeKey;
      cta.dataset.bill = String(Math.round(bill));
      cta.setAttribute("href", `${ctaPath}?type=${encodeURIComponent(typeKey)}#enquiry`);
    }
  };

  billInput.addEventListener("input", () => update({ source: "bill" }));
  billInput.addEventListener("change", () => update({ source: "bill", strict: true }));
  range.addEventListener("input", () => {
    billInput.value = range.value;
    update({ source: "range" });
  });
  typeInputs.forEach((i) => i.addEventListener("change", () => update()));
  kwhInput.addEventListener("input", () => update());

  update({ strict: true });
})();
