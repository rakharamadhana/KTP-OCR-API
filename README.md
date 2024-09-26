# KTP-OCR

## Kartu Tanda Penduduk Extractor
**KTP-OCR-API** is a modified version of the KTP-OCR project by <a href="https://github.com/YukaLangbuana/KTP-OCR">YukaLangbuana</a>, designed to extract comprehensive information from Kartu Tanda Penduduk (KTP) while retaining the integrity of the data.

**KTP-OCR** is an open-source Python package that aims to create a production-grade KTP extractor. The goal of the package is to extract as much information as possible while ensuring the accuracy of the extracted data.


---
## Requirements
To run this project, you need to have Tesseract OCR installed with Indonesian language support. You can install it on a server using the following commands:

### For Ubuntu/Debian
```console
$ sudo apt update
$ sudo apt install tesseract-ocr tesseract-ocr-ind
```

### For Windows via Chocolatey
If you are using Windows, you can install Tesseract via Chocolatey:

1. Open an elevated Command Prompt (Run as Administrator). 
2. Run the following command:
```console
$ choco install tesseract
```
3. After installation, you may need to manually add the Indonesian language file. You can download it from <a href="https://github.com/tesseract-ocr/tessdata">Tesseract Language Data</a> and place it in the Tesseract installation directory under <b>tessdata</b>.

---

## 🚀 How to launch

```console
$ git clone https://github.com/rakharamadhana/KTP-OCR-API.git
$ cd KTP-OCR-API
$ pip install -r requirements.txt
$ python app.py
```
Then access through your Flask server in  <a href="localhost:5000">localhost:5000</a>

---
## How to use

Make a request with <a href="https://www.postman.com/downloads/">Postman</a> (or similar program) to <a href="localhost:5000">localhost:5000/ocr</a> with form-data body of ```File``` type

### Example returned Json
```json
{
    "parsed": {
        "agama": "ISLAM",
        "alamat": "'JL.JATI JAYA",
        "berlaku_hingga": "SEUMUR HIDUP",
        "golongan_darah": "-",
        "jenis_kelamin": "LAKI-LAKI",
        "kecamatan": "PONDOK AREN",
        "kelurahan_atau_desa": "JURANGMANGU TIMUR",
        "kewarganegaraan": "WNI",
        "kota_kab": "ISLAM",
        "nama": "ADJIE BOESTAMI",
        "nik": "36740302101XXXXXX",
        "pekerjaan": "PELAJAR/MAHASISWA",
        "provinsi": "BANTEN",
        "rt": "007",
        "rw": "007",
        "status_perkawinan": "BELUM KAWIN",
        "tanggal_lahir": "DD-MM-19YY",
        "tempat_lahir": "TANGERANG"
    },
    "raw": "<raw-result>"
}
```

---

<p align="center"> This repository is a modified version from <a href="https://github.com/YukaLangbuana/KTP-OCR">YukaLangbuana</a> to made it possible as an API.</p>