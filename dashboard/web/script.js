(function () {
  "use strict";

  const DATA = window.AMAZONIQ_DATA;
  if (!DATA) {
    document.body.innerHTML =
      "<p style='padding:2rem;color:#e05555'>Missing data.js — run: python src/build_web_data.py</p>";
    return;
  }

  const TIER_COLORS = {
    standard: "#3d9a8b",
    elevated: "#d4a24c",
    high: "#e05555",
  };

  const CHART_DEFAULTS = {
    color: "#a89f94",
    borderColor: "#3a342c",
    font: { family: "'Outfit', sans-serif", size: 11 },
  };

  Chart.defaults.color = CHART_DEFAULTS.color;
  Chart.defaults.borderColor = CHART_DEFAULTS.borderColor;
  Chart.defaults.font = CHART_DEFAULTS.font;

  const metrics = DATA.forecast_metrics;
  const inventory = DATA.inventory_planning;
  const categories = DATA.categories;

  const mapeValues = metrics.map((m) => m.mape_pct);
  const mapeMin = Math.min(...mapeValues);
  const mapeMax = Math.max(...mapeValues);
  const highUncertainty = inventory.filter((r) => r.high_uncertainty_flag);
  const weakCount = metrics.filter((m) => m.weak_accuracy_flag).length;

  let forecastChart = null;

  function tierColor(tier) {
    return TIER_COLORS[tier] || TIER_COLORS.elevated;
  }

  function fmtPct(n) {
    return `${Number(n).toFixed(1)}%`;
  }

  function fmtNum(n) {
    return Number(n).toLocaleString(undefined, { maximumFractionDigits: 1 });
  }

  /* --- Executive KPIs --- */
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

    renderMapeChart();
    renderCatalogChart();
  }

  function renderMapeChart() {
    const sorted = [...metrics].sort((a, b) => a.mape_pct - b.mape_pct);
    const ctx = document.getElementById("mapeChart");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: sorted.map((m) => m.category_name.replace(" & ", " &\n")),
        datasets: [
          {
            label: "MAPE %",
            data: sorted.map((m) => m.mape_pct),
            backgroundColor: sorted.map((m) =>
              m.mape_pct >= 25
                ? TIER_COLORS.high
                : m.mape_pct >= 15
                  ? TIER_COLORS.elevated
                  : TIER_COLORS.standard
            ),
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
              label: (ctx) => ` MAPE: ${fmtPct(ctx.raw)}`,
            },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(58,52,44,0.5)" },
            ticks: { callback: (v) => `${v}%` },
          },
          y: { grid: { display: false } },
        },
      },
    });
  }

  function renderCatalogChart() {
    const sorted = [...categories].sort(
      (a, b) => b.catalog_product_count - a.catalog_product_count
    );
    const ctx = document.getElementById("catalogChart");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: sorted.map((c) => c.category_name.replace(" & ", " &\n")),
        datasets: [
          {
            label: "Mapped products",
            data: sorted.map((c) => c.catalog_product_count),
            backgroundColor: sorted.map((c) =>
              c.category_id === "garden" ? TIER_COLORS.high : "#e07a5f"
            ),
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.raw.toLocaleString()} products`,
            },
          },
        },
        scales: {
          y: {
            grid: { color: "rgba(58,52,44,0.5)" },
            ticks: {
              callback: (v) =>
                v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v,
            },
          },
          x: { grid: { display: false } },
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
    updateForecastChart(select.value);
  }

  function updateForecastChart(categoryId) {
    const metric = metrics.find((m) => m.category_id === categoryId);
    const points = DATA.forecast_backtest[categoryId] || [];
    const badge = document.getElementById("categoryMapeBadge");
    badge.textContent = `Holdout MAPE: ${fmtPct(metric.mape_pct)}`;
    badge.className =
      "mape-badge" + (metric.weak_accuracy_flag ? " weak" : "");

    const labels = points.map((p) => p.ds.slice(5));
    const ctx = document.getElementById("forecastChart");

    if (forecastChart) forecastChart.destroy();

    forecastChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Actual (Trends)",
            data: points.map((p) => p.actual),
            borderColor: "#f5f0ea",
            backgroundColor: "rgba(245,240,234,0.08)",
            borderWidth: 2,
            pointRadius: 2,
            tension: 0.2,
          },
          {
            label: "Prophet forecast",
            data: points.map((p) => p.predicted),
            borderColor: "#e07a5f",
            backgroundColor: "rgba(224,122,95,0.1)",
            borderWidth: 2,
            borderDash: [6, 4],
            pointRadius: 2,
            tension: 0.2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            labels: { usePointStyle: true, padding: 16 },
          },
          tooltip: {
            callbacks: {
              title: (items) => {
                const idx = items[0].dataIndex;
                return points[idx]?.ds || "";
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
            max: 100,
          },
          x: {
            grid: { display: false },
            ticks: { maxRotation: 45, minRotation: 0, autoSkip: true, maxTicksLimit: 10 },
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

    const sorted = [...inventory].sort(
      (a, b) => b.safety_stock - a.safety_stock
    );
    const labels = sorted.map((r) => r.category_name.replace(" & ", " &\n"));
    const colors = sorted.map((r) => tierColor(r.uncertainty_tier));

    new Chart(document.getElementById("safetyStockChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Safety stock (modeled)",
            data: sorted.map((r) => r.safety_stock),
            backgroundColor: colors,
            borderRadius: 6,
          },
        ],
      },
      options: barOptions("Index units"),
    });

    const sortedRop = [...inventory].sort(
      (a, b) => b.reorder_point - a.reorder_point
    );
    new Chart(document.getElementById("reorderPointChart"), {
      type: "bar",
      data: {
        labels: sortedRop.map((r) => r.category_name.replace(" & ", " &\n")),
        datasets: [
          {
            label: "Reorder point (modeled)",
            data: sortedRop.map((r) => r.reorder_point),
            backgroundColor: sortedRop.map((r) => tierColor(r.uncertainty_tier)),
            borderRadius: 6,
          },
        ],
      },
      options: barOptions("Index units"),
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

  function barOptions(yTitle) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          title: { display: true, text: yTitle, color: "#a89f94" },
          grid: { color: "rgba(58,52,44,0.5)" },
        },
        x: { grid: { display: false } },
      },
    };
  }

  /* --- Data quality --- */
  function renderDQ() {
    document.getElementById("dqGrid").innerHTML = DATA.dq_highlights
      .map(
        (d) => `
      <article class="dq-card ${d.severity}">
        <div class="dq-id">${d.id}</div>
        <h3 class="dq-title">${d.title}</h3>
        <p class="dq-detail">${d.detail}</p>
      </article>`
      )
      .join("");
  }

  /* --- Init --- */
  renderOverview();
  initForecastSection();
  renderInventory();
  renderDQ();
})();
