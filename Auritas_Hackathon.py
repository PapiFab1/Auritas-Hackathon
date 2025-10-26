from flask import Flask, render_template, jsonify
import pandas as pd
import os
import json


app = Flask(__name__)

# === STEP 1: Load all CSVs from /data ===
def load_data():
    data_dir = "data"
    tables = {}

    for file in os.listdir(data_dir):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            file_path = os.path.join(data_dir, file)
            try:
                tables[table_name] = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                tables[table_name] = pd.read_csv(file_path, encoding="latin1")
    return tables


# === STEP 2: Build unified dataset ===
def build_joined_data(tables):
    ekko = tables.get("EKKO", pd.DataFrame())
    ekpo = tables.get("EKPO", pd.DataFrame())
    ekbe = tables.get("EKBE", pd.DataFrame())
    ekkn = tables.get("EKKN", pd.DataFrame())
    lfa1 = tables.get("LFA1", pd.DataFrame())
    mara = tables.get("MARA", pd.DataFrame())
    prcd = tables.get("PRCD_ELEMENTS", pd.DataFrame())
    cdhdr = tables.get("CDHDR", pd.DataFrame())
    stxl = tables.get("STXL", pd.DataFrame())

    # === Rename friendly Excel labels to SAP field names ===
    rename_map = {
    # EKKO - Header Data
    "Purchasing Document": "EBELN",
    "Vendor": "LIFNR",
    "Document Date": "BEDAT",
    "Currency": "WAERS",
    "Purchasing Organization": "EKORG",
    "Purchasing Group": "EKGRP",
    "Company Code": "BUKRS",

    # EKPO - Item Data
    "Item": "EBELP",
    "Material": "MATNR",
    "Short Text": "TXZ01",
    "Quantity": "MENGE",
    "Order Unit": "MEINS",
    "Net Price": "NETPR",
    "Delivery Date": "EINDT",

    # EKKN - Account Assignment
    "G/L Account": "SAKTO",
    "Cost Center": "KOSTL",
    "Profit Center": "PRCTR",
    "WBS Element": "PS_PSP_PNR",
    "Order": "AUFNR",

    # PRCD_ELEMENTS - Pricing
    "Condition Type": "KSCHL",
    "Condition Amount": "KBETR",
    "Condition Currency": "WAERS",
    "Condition Unit": "KMEIN",

    # EKBE - History
    "Material Document": "BELNR",
    "Movement Type": "BWART",
    "Posting Date": "BUDAT",
    "PO History Quantity": "MENGE",
    "Amount in LC": "WRBTR",

    # CDHDR - Changes
    "Changed by": "USERNAME",
    "Date of Change": "UDATE",
    "Time of Change": "UTIME",
    "Transaction": "TCODE",

    # STXL - Notes
    "Text Object": "TDOBJECT",
    "Text ID": "TDID",
    "Text Name": "TDNAME",
    "Language": "TDSPRAS",

    # Vendor Info (LFA1)
    "Name 1": "NAME1"
}


    for df in [ekko, ekpo, ekbe, ekkn, lfa1, mara, prcd, cdhdr, stxl]:
        if not df.empty:
            df.rename(columns=rename_map, inplace=True)

    # === Force key columns to string to fix int64/object mismatch ===
    key_fields = ["EBELN", "EBELP", "LIFNR", "MATNR"]
    for df in [ekko, ekpo, ekbe, ekkn, lfa1, mara, prcd, cdhdr, stxl]:
        for key in key_fields:
            if key in df.columns:
                df[key] = df[key].astype(str).str.strip()

    # === Merge progressively ===
    merged = ekko.copy()

    if not ekpo.empty and "EBELN" in ekpo.columns:
        merged = merged.merge(ekpo, on="EBELN", how="left", suffixes=("_header", "_item"))

    if "LIFNR" in merged.columns and not lfa1.empty:
        merged = merged.merge(lfa1, on="LIFNR", how="left", suffixes=("", "_vendor"))

    if "MATNR" in merged.columns and not mara.empty:
        merged = merged.merge(mara, on="MATNR", how="left", suffixes=("", "_material"))

    if not ekkn.empty and {"EBELN", "EBELP"}.issubset(ekkn.columns):
        merged = merged.merge(ekkn, on=["EBELN", "EBELP"], how="left", suffixes=("", "_acct"))

    if not ekbe.empty and {"EBELN", "EBELP"}.issubset(ekbe.columns):
        merged = merged.merge(ekbe, on=["EBELN", "EBELP"], how="left", suffixes=("", "_hist"))

    if not prcd.empty and "EBELP" in prcd.columns:
        merged = merged.merge(prcd, on="EBELP", how="left", suffixes=("", "_price"))

    if not cdhdr.empty and "EBELN" in cdhdr.columns:
        merged = merged.merge(cdhdr, on="EBELN", how="left", suffixes=("", "_chg"))

    if not stxl.empty and "EBELN" in stxl.columns:
        merged = merged.merge(stxl, on="EBELN", how="left", suffixes=("", "_text"))

    return merged


# === STEP 3: Initialize Data ===
tables = load_data()
merged_data = build_joined_data(tables)


# === STEP 4: Flask routes ===
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def get_data():
    # Convert to JSON-safe format
    cleaned = (
        merged_data.head(200)
        .replace({pd.NA: None})
        .replace({float("nan"): None})
        .fillna("")
        .astype(str)
    )
    return jsonify(cleaned.to_dict(orient="records"))

@app.route("/api/decrypted_results")
def get_decrypted_results():
    data_dir = os.path.join(os.getcwd(), "data")
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

    results = []
    for file in files:
        with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
            results.append(json.load(f))

    return jsonify(results)


# === STEP 5: Run Server ===
if __name__ == "__main__":
    app.run(debug=True)
