(function () {
  "use strict";

  const DATA = window.AMAZONIQ_DATA;
  if (!DATA) {
    document.body.innerHTML =
      "<p style='padding:2rem;color:#e05555'>Missing data.js — run: python src/build_web_data.py</p>";
    return;
  }

  const PALETTE = DATA.palette || {
    electronics: "#e07a5f",
    home_kitchen: "#3d9a8b",
    clothing: "#c45c7a",
    health: "#6b8cae",
    garden: "#8fb339",
    toys: "#d4a24c",
  };

  const TIER_COLORS = {
    standard: "#3d9a8b",
    elevated: "#d4a24c",
    high: "#e05555",
  };

  Chart.defaults.color = "#a89f94";
  Chart.defaults.borderColor = "#3a342c";
  Chart.defaults.font = { family: "'Outfit', sans-serif", size: 11 };
  Chart.defaults.animation = { duration: 750, easing: "easeOutQuart" };

  const metrics = DATA.forecast_metrics;
  const inventory = DATA.inventory_planning;
  const categories = DATA.categories;
  const mapeValues = metrics.map((m) => m.mape_pct);
  const mapeMin = Math.min(...mapeValues);
  const mapeMax = Math.max(...mapeValues);
  const highUncertainty = inventory.filter((r) => r.high_uncertainty_flag);
  const weakCount = metrics.filter((m) => m.weak_accuracy_flag).length;

  let forecastChart = null;

  function catColor(id) {
    return PALETTE[id] || "#e07a5f";
  }

  function hexAlpha(hex, a) {
    const h = hex.replace("#", "");
    const n = parseInt(h, 16);
    const r = (n >> 16) & 255;
    const g = (n >> 8) & 255;
    const b = n & 255;
    return `rgba(${r},${g},${b},${a})`;
  }

  function fmtPct(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return `${Number(n).toFixed(1)}%`;
  }

  function fmtNum(n) {
    if (n == null || Number.isNaN(Number(n))) return "—";
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 });
  }

  function whenVisible(canvas, build) {
    let done = false;
    const run = () => {
      if (done) return;
      done = true;
      build();
    };
    if (!("IntersectionObserver" in window)) {
      run();
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          io.disconnect();
          run();
        }
      },
      { threshold: 0.15 }
    );
    io.observe(canvas);
  }

  function tooltipTitle(label) {
    return String(label).replace(/\n/g, " ");
  }

  /* --- Overview KPIs --- */
  function renderOverview() {
    document.getElementById("framingSentence").textContent =
      "This models U.S. Google Trends search interest (0–100 index) as a demand proxy — not Amazon warehouse units, orders, or Seller Central inventory.";

    document.getElementById("generatedAt").textContent =
      `Data embed: ${DATA.generated_at}`;

    const kpis = [
      {
        label: "MAPE range",
        value: `${fmtPct(mapeMin)} – ${fmtPct(mapeMax)}`,
        sub: "26-week Prophet holdout",
        cls: "kpi-accent",
      },
      {
        label: "Weak accuracy",
        value: String(weakCount),
        sub: "categories flagged (MAPE ≥ 15%)",
        cls: weakCount > 0 ? "kpi-warn" : "",
      },
      {
        label: "High uncertainty",
        value: String(highUncertainty.length),
        sub: "Electronics & Clothing (MAPE ≥ 25%)",
        cls: highUncertainty.length ? "kpi-warn" : "",
      },
      {
        label: "Service level",
        value: "95%",
        sub: "Stated assumption · z = 1.645",
        cls: "",
      },
      {
        label: "Lead time",
        value: "2 wk",
        sub: "Illustrative replenishment",
        cls: "",
      },
      {
        label: "Categories",
        value: String(categories.length),
        sub: "Amazon-style merchandise groups",
        cls: "",
      },
    ];

    document.getElementById("kpiGrid").innerHTML = kpis
      .map(
        (k) => `
      <div class="kpi ${k.cls}">
        <div class="kpi-label">${k.label}</div>
        <div class="kpi-value">${k.value}</div>
        <div class="kpi-sub">${k.sub}</div>
      </div>`
      )
      .join("");

    document.getElementById("mapeLegend").innerHTML = `
      <span><i class="tier-dot standard"></i> Standard border (MAPE &lt; 15%)</span>
      <span><i class="tier-dot elevated"></i> Elevated border (15–25%)</span>
      <span><i class="tier-dot high"></i> High border (≥ 25%)</span>
    `;

    whenVisible(document.getElementById("mapeChart"), renderMapeChart);
  }

  function renderMapeChart() {
    const sorted = [...metrics].sort((a, b) => a.mape_pct - b.mape_pct);
    new Chart(document.getElementById("mapeChart"), {
      type: "bar",
      data: {
        labels: sorted.map((m) => m.category_name.replace(" & ", " &\n")),
        datasets: [
          {
            label: "Holdout MAPE",
            data: sorted.map((m) => m.mape_pct),
            backgroundColor: sorted.map((m) => catColor(m.category_id)),
            borderColor: sorted.map((m) => TIER_COLORS[m.uncertainty_tier] || TIER_COLORS.elevated),
            borderWidth: 2,
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => tooltipTitle(items[0].label),
              label: (ctx) => {
                const row = sorted[ctx.dataIndex];
                return [
                  ` MAPE: ${fmtPct(row.mape_pct)}`,
                  ` Tier: ${row.uncertainty_tier}`,
                  ` Keyword: ${row.keyword}`,
                ];
              },
            },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(58,52,44,0.5)" },
            ticks: { callback: (v) => `${v}%` },
            title: { display: true, text: "MAPE %", color: "#a89f94" },
          },
          y: { grid: { display: false } },
        },
      },
    });
  }

  /* --- Forecast vs actual --- */
  function initForecastSection() {
    const select = document.getElementById("categorySelect");
    metrics.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.category_id;
      opt.textContent = `${m.category_name} (${m.keyword})`;
      select.appendChild(opt);
    });

    select.addEventListener("change", () => updateForecastChart(select.value));
    whenVisible(document.getElementById("forecastChart"), () =>
      updateForecastChart(select.value)
    );
    whenVisible(document.getElementById("rollingMapeChart"), renderRollingMape);
  }

  function updateForecastChart(categoryId) {
    const metric = metrics.find((m) => m.category_id === categoryId);
    const series =
      DATA.forecast_series?.[categoryId] ||
      (DATA.forecast_backtest?.[categoryId] || []).map((p) => ({
        ...p,
        holdout: true,
      }));
    const color = catColor(categoryId);
    const badge = document.getElementById("categoryMapeBadge");
    badge.textContent = `Holdout MAPE: ${fmtPct(metric.mape_pct)}`;
    badge.className = "mape-badge" + (metric.weak_accuracy_flag ? " weak" : "");

    const labels = series.map((p) => p.ds);
    const holdoutStart = metric.test_start || "2026-02-15";
    const holdoutEnd = metric.test_end || "2026-08-09";

    const ctx = document.getElementById("forecastChart");
    if (forecastChart) forecastChart.destroy();

    forecastChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Actual (Trends)",
            data: series.map((p) => p.actual),
            borderColor: color,
            backgroundColor: hexAlpha(color, 0.12),
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            tension: 0.15,
            spanGaps: false,
          },
          {
            label: "Prophet forecast",
            data: series.map((p) => p.predicted),
            borderColor: hexAlpha(color, 0.85),
            borderWidth: 2,
            borderDash: [6, 4],
            pointRadius: 0,
            pointHoverRadius: 4,
            tension: 0.15,
            spanGaps: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { usePointStyle: true, padding: 16 } },
          tooltip: {
            callbacks: {
              title: (items) => series[items[0].dataIndex]?.ds || "",
              afterBody: (items) => {
                const p = series[items[0].dataIndex];
                if (!p) return [];
                const delta =
                  p.actual != null && p.predicted != null
                    ? p.actual - p.predicted
                    : null;
                const zone = p.holdout ? "Holdout (backtest)" : "Training (in-sample)";
                return [
                  `Delta (actual − forecast): ${delta == null ? "—" : fmtNum(delta)}`,
                  zone,
                ];
              },
            },
          },
          annotation: {
            annotations: {
              holdoutBand: {
                type: "box",
                xMin: holdoutStart,
                xMax: holdoutEnd,
                backgroundColor: "rgba(224, 122, 95, 0.12)",
                borderColor: "rgba(224, 122, 95, 0.35)",
                borderWidth: 1,
                label: {
                  display: true,
                  content: "26-week holdout",
                  position: { x: "center", y: "start" },
                  color: "#e07a5f",
                  font: { size: 10, family: "'Outfit', sans-serif" },
                },
              },
            },
          },
        },
        scales: {
          y: {
            title: {
              display: true,
              text: "Search interest index (0–100)",
              color: "#a89f94",
            },
            grid: { color: "rgba(58,52,44,0.5)" },
            min: 0,
            suggestedMax: 100,
          },
          x: {
            grid: { display: false },
            ticks: {
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 8,
              callback: (val, idx) => {
                const ds = labels[idx];
                return ds ? ds.slice(0, 7) : "";
              },
            },
          },
        },
      },
    });
  }

  function renderRollingMape() {
    const rolling = DATA.rolling_mape || {};
    const catIds = metrics.map((m) => m.category_id);
    const dateSet = new Set();
    catIds.forEach((id) => (rolling[id] || []).forEach((p) => dateSet.add(p.ds)));
    const labels = [...dateSet].sort();

    const datasets = catIds.map((id) => {
      const lookup = Object.fromEntries(
        (rolling[id] || []).map((p) => [p.ds, p.rolling_mape_4w])
      );
      const meta = metrics.find((m) => m.category_id === id);
      return {
        label: meta.category_name,
        data: labels.map((d) => lookup[d] ?? null),
        borderColor: catColor(id),
        backgroundColor: hexAlpha(catColor(id), 0.12),
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 5,
        tension: 0.2,
        spanGaps: true,
      };
    });

    new Chart(document.getElementById("rollingMapeChart"), {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { usePointStyle: true, boxWidth: 8, padding: 12 } },
          tooltip: {
            callbacks: {
              title: (items) => items[0].label,
              label: (ctx) =>
                ` ${ctx.dataset.label}: ${fmtPct(ctx.raw)} rolling 4w MAPE`,
            },
          },
        },
        scales: {
          y: {
            title: { display: true, text: "Rolling 4-week MAPE %", color: "#a89f94" },
            grid: { color: "rgba(58,52,44,0.5)" },
            ticks: { callback: (v) => `${v}%` },
            min: 0,
          },
          x: {
            grid: { display: false },
            ticks: { maxTicksLimit: 8, maxRotation: 0 },
          },
        },
      },
    });
  }

  /* --- Inventory --- */
  function renderInventory() {
    document.getElementById("tierLegend").innerHTML = `
      <span><i class="tier-dot standard"></i> Standard (MAPE &lt; 15%)</span>
      <span><i class="tier-dot elevated"></i> Elevated (15–25%)</span>
      <span><i class="tier-dot high"></i> High (≥ 25%)</span>
    `;

    const sorted = [...inventory].sort((a, b) => b.safety_stock - a.safety_stock);
    const labels = sorted.map((r) => r.category_name.replace(" & ", " &\n"));

    whenVisible(document.getElementById("inventoryGroupedChart"), () => {
      new Chart(document.getElementById("inventoryGroupedChart"), {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Safety stock",
              data: sorted.map((r) => r.safety_stock),
              backgroundColor: sorted.map((r) => catColor(r.category_id)),
              borderRadius: 5,
            },
            {
              label: "Reorder point",
              data: sorted.map((r) => r.reorder_point),
              backgroundColor: sorted.map((r) => hexAlpha(catColor(r.category_id), 0.38)),
              borderColor: sorted.map((r) => catColor(r.category_id)),
              borderWidth: 1,
              borderRadius: 5,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { usePointStyle: true, padding: 16 } },
            tooltip: {
              callbacks: {
                title: (items) => tooltipTitle(items[0].label),
                label: (ctx) => {
                  const row = sorted[ctx.dataIndex];
                  const name = ctx.dataset.label;
                  const val = name === "Safety stock" ? row.safety_stock : row.reorder_point;
                  return ` ${name}: ${fmtNum(val)}  ·  ${row.uncertainty_tier}  ·  MAPE ${fmtPct(row.mape_pct_baseline)}`;
                },
              },
            },
          },
          scales: {
            y: {
              title: { display: true, text: "Search-interest index units", color: "#a89f94" },
              grid: { color: "rgba(58,52,44,0.5)" },
            },
            x: { grid: { display: false } },
          },
        },
      });
    });

    const tbody = document.querySelector("#inventoryTable tbody");
    tbody.innerHTML = inventory
      .map((r) => {
        const tierCls = `tier-${r.uncertainty_tier}`;
        const badgeCls = `badge badge-${r.uncertainty_tier}`;
        return `<tr class="${tierCls}">
          <td>${r.category_name}</td>
          <td>${fmtPct(r.mape_pct_baseline)}</td>
          <td><span class="${badgeCls}">${r.uncertainty_tier}</span></td>
          <td>${fmtNum(r.safety_stock)}</td>
          <td>${fmtNum(r.reorder_point)}</td>
          <td>${r.high_uncertainty_flag ? "Yes" : "No"}</td>
        </tr>`;
      })
      .join("");
  }

  /* --- Data quality --- */
  function renderDQ() {
    const others = DATA.dq_highlights.filter((d) => d.id !== "DQ-025");
    document.getElementById("dqGrid").innerHTML = others
      .map(
        (d) => `
      <article class="dq-card ${d.severity}">
        <div class="dq-id">${d.id}</div>
        <h3 class="dq-title">${d.title}</h3>
        <p class="dq-detail">${d.detail}</p>
      </article>`
      )
      .join("");

    whenVisible(document.getElementById("catalogChart"), renderCatalogChart);
  }

  function renderCatalogChart() {
    const sorted = [...categories].sort(
      (a, b) => b.catalog_product_count - a.catalog_product_count
    );
    new Chart(document.getElementById("catalogChart"), {
      type: "bar",
      data: {
        labels: sorted.map((c) => c.category_name.replace(" & ", " &\n")),
        datasets: [
          {
            label: "Mapped products",
            data: sorted.map((c) => c.catalog_product_count),
            backgroundColor: sorted.map((c) => catColor(c.category_id)),
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => tooltipTitle(items[0].label),
              label: (ctx) => {
                const row = sorted[ctx.dataIndex];
                const max = Math.max(...sorted.map((c) => c.catalog_product_count));
                const ratio = max / row.catalog_product_count;
                return [
                  ` ${row.catalog_product_count.toLocaleString()} products`,
                  ` ${ratio.toFixed(1)}× smaller than largest category` ,
                ];
              },
            },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(58,52,44,0.5)" },
            ticks: {
              callback: (v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v),
            },
            title: { display: true, text: "Mapped catalog products (linear)", color: "#a89f94" },
          },
          y: { grid: { display: false } },
        },
      },
    });
  }

  renderOverview();
  initForecastSection();
  renderInventory();
  renderDQ();
})();
