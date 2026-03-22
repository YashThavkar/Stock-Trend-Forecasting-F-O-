(function () {
  const chartLayout = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: "DM Sans, sans-serif", color: "#e8ecf1" },
    margin: { t: 24, r: 16, b: 48, l: 56 },
    xaxis: { gridcolor: "#1e2633", zeroline: false },
    yaxis: { gridcolor: "#1e2633", zeroline: false },
    autosize: true,
    transition: {
      duration: 600,
      easing: "cubic-in-out",
    },
  };

  function markChartMounted(el) {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => el.classList.add("chart--mounted"));
    });
  }

  function lineChart(elId, dates, values, name) {
    const el = document.getElementById(elId);
    if (!el || !dates || !values) return Promise.resolve();

    const p = Plotly.newPlot(
      el,
      [
        {
          x: dates,
          y: values,
          type: "scatter",
          mode: "lines",
          line: { color: "#3d9cf5", width: 2.2, shape: "linear" },
          name: name,
        },
      ],
      {
        ...chartLayout,
        showlegend: false,
        yaxis: { ...chartLayout.yaxis, title: { text: "Level" } },
        xaxis: { ...chartLayout.xaxis, title: { text: "Date" } },
      },
      { responsive: true, displayModeBar: false }
    );

    const done = () => markChartMounted(el);
    if (p && typeof p.then === "function") return p.then(done);
    done();
    return Promise.resolve();
  }

  function heatmapChart(elId, tenors, moneyness, z) {
    const el = document.getElementById(elId);
    if (!el || !z || !tenors || !moneyness) return Promise.resolve();

    const p = Plotly.newPlot(
      el,
      [
        {
          z: z,
          x: moneyness,
          y: tenors,
          type: "heatmap",
          colorscale: [
            [0, "#0c4a6e"],
            [0.5, "#3d9cf5"],
            [1, "#a5f3fc"],
          ],
          colorbar: { title: "Level", tickfont: { color: "#8b98a8" } },
        },
      ],
      {
        ...chartLayout,
        margin: { t: 24, r: 24, b: 56, l: 72 },
        xaxis: { ...chartLayout.xaxis, title: { text: "Moneyness" } },
        yaxis: { ...chartLayout.yaxis, title: { text: "Tenor" }, autorange: "reversed" },
      },
      { responsive: true, displayModeBar: false }
    );

    const done = () => markChartMounted(el);
    if (p && typeof p.then === "function") return p.then(done);
    done();
    return Promise.resolve();
  }

  function setStats(m) {
    document.getElementById("stat-rows").textContent =
      m.trainingRows != null ? m.trainingRows.toLocaleString() : "—";
    document.getElementById("stat-dates").textContent =
      m.uniqueDates != null ? m.uniqueDates.toLocaleString() : "—";
    document.getElementById("stat-tenors").textContent =
      m.tenors != null ? String(m.tenors) : "—";
    document.getElementById("stat-mae").textContent =
      m.valMae != null ? m.valMae.toFixed(4) : "—";
    document.getElementById("stat-rmse").textContent =
      m.valRmse != null ? m.valRmse.toFixed(4) : "—";
  }

  async function main() {
    const base =
      document.querySelector("meta[name='demo-base']")?.content || "";
    const url = (base ? base.replace(/\/$/, "") + "/" : "") + "assets/data.json";
    const notice = document.getElementById("js-notice");

    let data;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      data = await res.json();
    } catch (e) {
      if (notice) {
        notice.hidden = false;
        notice.textContent =
          "Interactive Plotly charts need data.json (use GitHub Pages or run python -m http.server in /docs). PNG images above still work.";
      }
      document.querySelectorAll(".chart").forEach((el) => el.classList.add("chart--mounted"));
      console.error(e);
      return;
    }

    setStats(data.meta || {});

    const s = data.series10yAtm;
    if (s && s.dates && s.values) {
      await lineChart(
        "chart-history",
        s.dates,
        s.values,
        "10Y, ATM (moneyness 1.0)"
      );
    }

    const surf = data.surfaceLastTrain;
    if (surf && surf.z && surf.tenors && surf.moneyness) {
      await heatmapChart(
        "chart-heatmap",
        surf.tenors,
        surf.moneyness,
        surf.z
      );
    }

    const fc = data.forecast10yAtm;
    if (fc && fc.dates && fc.values && fc.dates.length) {
      await lineChart("chart-forecast", fc.dates, fc.values, "Forecast (10Y ATM)");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
