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

async function loadDecryptionResults() {
  const container = document.getElementById("decryptionContainer");
  container.innerHTML = "<p>Loading decrypted data...</p>";

  try {
    const res = await fetch("/api/decrypted_results");
    const json = await res.json();

    if (json.length === 0) {
      container.innerHTML = "<p>No decrypted files found.</p>";
      return;
    }

    container.innerHTML = "";

    json.forEach((file, i) => {
      const div = document.createElement("div");
      div.classList.add("decryption-card");
      div.innerHTML = `
        <h3>${i + 1}. ${file.filename || "Unknown File"}</h3>
        <p><b>Records:</b> ${file.record_count || "N/A"}</p>
        <p><b>Speed:</b> ${file.records_per_sec || "N/A"} rec/sec</p>
        <p><b>Time:</b> ${file.elapsed_time_sec || "N/A"} sec</p>
        <p><b>Sample Data:</b></p>
        <pre>${JSON.stringify(file.parsed_samples?.slice(0, 3) || {}, null, 2)}</pre>
      `;
      container.appendChild(div);
    });
  } catch (error) {
    container.innerHTML = `<p style="color:red;">Error loading decrypted data: ${error.message}</p>`;
  }
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
// Replace your existing tab click handler with this:
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    const targetTab = tab.dataset.target;
    
    document
      .querySelectorAll(".tab")
      .forEach((t) => t.classList.remove("active"));
    document
      .querySelectorAll(".tab-content")
      .forEach((c) => c.classList.remove("active"));
    
    tab.classList.add("active");
    document.getElementById(targetTab).classList.add("active");
    
    // Load decryption results when decryption tab is clicked
    if (targetTab === 'decryption') {
      loadDecryptionResults();
    }
  });
});
