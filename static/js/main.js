let tableData = [];

function filterNonEmpty(data, keys) {
  // Keep only rows where at least one column for this tab is not blank
  return data.filter((row) =>
    keys.some((k) => row[k] && row[k].toString().trim() !== "")
  );
}

let filteredData = [];

// Simple grouping by field keywords
const groupMap = {
  // Header Info
  header: ["EBELN", "LIFNR", "NAME1", "BEDAT", "WAERS", "EKORG", "EKGRP", "BUKRS"],

  // Item Details
  items: ["EBELN", "EBELP", "MATNR", "TXZ01", "MENGE", "MEINS", "NETPR", "EINDT"],

  // Account Assignment
  account: ["EBELN", "EBELP", "SAKTO", "KOSTL", "PRCTR", "PS_PSP_PNR", "AUFNR"],

  // Pricing
  pricing: ["EBELN", "EBELP", "KSCHL", "KBETR", "WAERS", "KMEIN"],

  // History
  history: ["EBELN", "EBELP", "BELNR", "BWART", "BUDAT", "MENGE", "WRBTR"],

  // Changes
  changes: ["EBELN", "USERNAME", "UDATE", "UTIME", "TCODE"],

  // Notes / Text
  notes: ["EBELN", "TDOBJECT", "TDID", "TDNAME", "TDSPRAS"]
};


function buildTable(id, data, keys) {
  const headerRow = document.querySelector(`#header-row-${id}`);
  const tbody = document.querySelector(`#table-${id} tbody`);
  headerRow.innerHTML = "";
  tbody.innerHTML = "";

  keys.forEach((k) => {
    const th = document.createElement("th");
    th.textContent = k;
    headerRow.appendChild(th);
  });

  data.forEach((row) => {
    const tr = document.createElement("tr");
    keys.forEach((k) => {
      const td = document.createElement("td");
      td.textContent = row[k] ?? "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

fetch("/api/data")
  .then((res) => res.json())
  .then((data) => {
    console.log("Columns available:", Object.keys(data[0]));
    console.log("✅ Loaded", data.length, "records");
    tableData = data;
    filteredData = data;
    updateTables();
  })
  .catch((err) => console.error("❌ Fetch error:", err));

function updateTables() {
  Object.entries(groupMap).forEach(([id, keys]) => {
    const subset = filterNonEmpty(
      filteredData.map((row) =>
        Object.fromEntries(keys.map((k) => [k, row[k] ?? ""]))
      ),
      keys
    );
    buildTable(id, subset, keys);
  });
}

// Search filter
document.getElementById("search").addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  filteredData = tableData.filter((row) =>
    Object.values(row).some(
      (v) => v && v.toString().toLowerCase().includes(query)
    )
  );
  updateTables();
});

// Tabs logic
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document
      .querySelectorAll(".tab")
      .forEach((t) => t.classList.remove("active"));
    document
      .querySelectorAll(".tab-content")
      .forEach((c) => c.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.target).classList.add("active");
  });
});
