# UIB Assistant

Chatbot sederhana berbasis scikit-learn untuk membantu mahasiswa memberikan informasi seputar akademik & administrasi UIB.

## Installation

Lakukan di terminal agar dapat melakukan clone dari github ini:
```bash
https://github.com/jupitvq/simple-uib-assistant.git
```

Buatlah environment khusus project ini:
```bash
python -m venv venv
```
```bash
.\venv\Scripts\activate
```

Pastikan [pip](https://pip.pypa.io/en/stable/) dan [Python 3.11](https://www.python.org/downloads/release/python-31110/) terinstal, lalu jalankan dependencies yang dibutuhkan dengan cmd dibawah:

```bash
pip install -r requirements.txt
```
Ketika semua selesai, project siap dijalankan, di repo ini akan ada 2 model yang sudah ditrain, model dari jupyter notebook dan dari python file, **satu model untuk deployment** dan **satu model untuk testing di environment**.
- Jika model ingin diubah, ubah di `data/intents.json` lalu jalankan `sklearn_chatbot.ipynb` dan isi input yang ada untuk pengetesan.
- Jika ingin mencoba lokal dengan model yang ada (tidak dideploy), jalankan `chatbot_sklearn_training.py`
- Jika ingin di deploy di Discord/Telegram, maka isilah parameter `.env` yang diperlukan.

## Konfigurasi
Clone file .env.example menjadi .env dan isi token & server channel ID jika ingin di deploy ke Discord/Telegram.
Contoh:
```python
TELEGRAM_BOT_TOKEN=8160179:AAGXxxxxxxA4U-v0OQmQ1nAasdfwegWFWsFEwd
DISCORD_BOT_TOKEN=MTI5NjAwxxxxxxxxxNzE0MQ.GB_mft.OmA3rkjgiexxxxgerfEFfRwT_7uiAqht0BI4_1OxpK4
MY_GUILD_ID=12963768XXXXXXX3465
```