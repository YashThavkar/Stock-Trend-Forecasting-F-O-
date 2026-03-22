(function () {
  function parseUsDate(s) {
    const parts = String(s).split("/");
    if (parts.length !== 3) return 0;
    const m = parseInt(parts[0], 10);
    const d = parseInt(parts[1], 10);
    const y = parseInt(parts[2], 10);
    return new Date(y, m - 1, d).getTime();
  }

  function uniqueSortedDates(keys) {
    const set = new Set();
    for (const k of keys) {
      set.add(k.split("|")[0]);
    }
    return Array.from(set).sort((a, b) => parseUsDate(a) - parseUsDate(b));
  }

  function tenorsForDate(lookupKeys, dateStr) {
    const tenors = new Set();
    for (const k of lookupKeys) {
      const p = k.split("|");
      if (p.length >= 3 && p[0] === dateStr) tenors.add(p[1]);
    }
    return Array.from(tenors);
  }

  function initDemo(payload, err, sourceLabel) {
    const selDate = document.getElementById("demo-date");
    const selTenor = document.getElementById("demo-tenor");
    const selMoney = document.getElementById("demo-moneyness");
    const btn = document.getElementById("demo-submit");
    const out = document.getElementById("demo-output");
    const hint = document.getElementById("demo-source-hint");

    if (!selDate || !btn || !out) return;

    if (hint && sourceLabel) {
      hint.textContent = sourceLabel;
      hint.hidden = false;
    }
    if (err) err.hidden = true;

    const lookup = payload.lookup || {};
    const keys = Object.keys(lookup);
    const dates = uniqueSortedDates(keys);
    const moneyness = payload.moneyness || [];

    if (!dates.length) {
      if (err) {
        err.hidden = false;
        err.textContent = "Demo data is empty. Run python scripts/build_docs_assets.py from the project root.";
      }
      return;
    }

    dates.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      selDate.appendChild(opt);
    });

    moneyness.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      selMoney.appendChild(opt);
    });

    function refreshTenors() {
      const d = selDate.value;
      selTenor.innerHTML = "";
      const tenors = tenorsForDate(keys, d).sort();
      tenors.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t;
        opt.textContent = t;
        selTenor.appendChild(opt);
      });
    }

    selDate.addEventListener("change", refreshTenors);
    refreshTenors();

    if (dates.includes("10/15/2019")) selDate.value = "10/15/2019";
    else if (dates.length) selDate.selectedIndex = Math.max(0, dates.length - 30);
    refreshTenors();
    if ([...selTenor.options].some((o) => o.value === "10Y")) selTenor.value = "10Y";
    if ([...selMoney.options].some((o) => o.value === "1")) selMoney.value = "1";

    function runLookup() {
      if (err) err.hidden = true;
      const d = selDate.value;
      const t = selTenor.value;
      const m = selMoney.value;
      const key = `${d}|${t}|${m}`;
      const v = lookup[key];
      if (v === undefined) {
        out.innerHTML =
          '<p class="demo-result demo-result--empty">No value for this combination in the demo dataset. Pick another date (forecast period or last 150 training days).</p>';
        return;
      }
      out.innerHTML = `
        <p class="demo-result__label">Surface level (model / data)</p>
        <p class="demo-result__value">${v}</p>
        <p class="demo-result__meta">Key: <code>${key}</code></p>
      `;
    }

    btn.addEventListener("click", runLookup);
    runLookup();
  }

  async function main() {
    const err = document.getElementById("demo-error");

    if (window.__DEMO_LOOKUP_PAYLOAD) {
      initDemo(
        window.__DEMO_LOOKUP_PAYLOAD,
        err,
        "Data source: embedded demo-data.js (works when opening files locally with file://)."
      );
      return;
    }

    const base =
      document.querySelector("meta[name='demo-base']")?.content || "";
    const url =
      (base ? base.replace(/\/$/, "") + "/" : "") + "assets/demo_lookup.json";

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      const payload = await res.json();
      initDemo(
        payload,
        err,
        "Data source: demo_lookup.json (loaded over http/https)."
      );
    } catch (e) {
      if (err) {
        err.hidden = false;
        err.innerHTML =
          "Could not load demo data. Ensure <code>assets/demo-data.js</code> is included before <code>demo.js</code> " +
          "(run <code>python scripts/build_docs_assets.py</code>). If you removed the embed script, serve the site over " +
          "<code>http://</code> so <code>demo_lookup.json</code> can load.";
      }
      console.error(e);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
