# Auritas-Hackathon

A Python-based tool for analyzing and decoding SAP .ARCHIVE files generated through the SAP Archive Development Kit (ADK).
This project was created as part of the Auritas Hackathon 2025 – Algorithm Decryption Challenge.
It identifies binary segments, extracts readable information, and interprets record structures,
then exports the results into JSON for integration with a Flask-based visualization dashboard.

## Quickstart
```bash
pip install -r requirements.txt
or install these:
flask
pandas
lz4
zstandard
chardet
tqdm
```
## Run the decoder file
Run decoder.py and view the results in algorithms/results/ 

## Performance
Processed 5 files in 0.65 seconds
Total records parsed: 19,495
Data Types: 6 supported
Summary report: results\summary_all_files.json

## Our approach and Findings
Initial Investigation

    Tested standard compression algorithms (GZIP, LZ4, ZSTD) - all failed

    Hex analysis revealed no compression magic bytes

    Discovered files use SAP's proprietary ADK binary format, not conventional compression

Technical Breakthrough

    Built custom ADK segment scanner

    Identified key segment: ID 0065, 585KB at offset 2

    Detected 16-byte repeating patterns indicating fixed-length records

Solution Delivery

    Developed ASCII extraction and field type detection

    Parsed binary data into structured JSON

    Integrated results into web dashboard for visualization

Key Finding: SAP .ARCHIVE files are binary serialization containers, not compressed data - requiring specialized ADK parsing rather than standard decompression.


## Technical Highlights

Advanced Binary Analysis

    Reverse-engineered SAP's proprietary ADK archive format through hex analysis and pattern recognition

    Developed custom segment scanners to identify 0x0065 headers and extract 585KB data segments

    Implemented heuristic field detection for 16-byte fixed-length records

Multi-Algorithm Decryption Pipeline

    Automated detection of compression signatures (GZIP, LZ4, ZSTD, ZLIB)

    Intelligent fallback to SAP ADK binary parsing when standard decompression fails

    Real-time ASCII extraction and pattern analysis from binary streams

Full-Stack Data Integration

    Unified data pipeline from raw binary decryption to modern web visualization

    RESTful API serving both CSV data and decrypted archive results

    Real-time search and filtering across 100,000+ SAP records
