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
