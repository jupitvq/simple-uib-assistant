# UIB Assistant

Chatbot sederhana berbasis scikit-learn untuk membantu mahasiswa memberikan informasi seputar akademik & administrasi UIB.

## Installation

Pastikan [pip](https://pip.pypa.io/en/stable/) dan [Python 3.11](https://www.python.org/downloads/release/python-31110/) terinstal, lalu jalankan dependencies yang dibutuhkan dengan cmd dibawah:

```bash
pip install -r requirements.txt
```

## Konfigurasi
Clone file .env.example menjadi .env dan isi token & server channel ID jika ingin di deploy ke Discord/Telegram.
Contoh:
```python
TELEGRAM_BOT_TOKEN=8160179:AAGX3bBfqA4U-v0OQmQ1nAasdfwegWFWsFEwd
DISCORD_BOT_TOKEN=MTI5NjAwNzYefFegGRxNzE0MQ.GB_mft.OmA3rkjgieDdFGtgerfEFfRwT_7uiAqht0BI4_1OxpK4
MY_GUILD_ID=12963768XXXXXXX3465
```