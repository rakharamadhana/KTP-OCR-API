import cv2
import json
import re
import numpy as np
import pytesseract
from ktpocr.form import KTPInformation

valid_religions = ['ISLAM', 'KRISTEN', 'KATOLIK', 'HINDU', 'BUDHA', 'KONGHUCU']

class KTPOCR(object):
    def __init__(self, image):
        # Directly assign the image passed as a NumPy array
        self.image = image
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.th, self.threshed = cv2.threshold(self.gray, 127, 255, cv2.THRESH_TRUNC)
        self.result = KTPInformation()
        self.master_process()

    def process(self, image):
        raw_extracted_text = pytesseract.image_to_string(self.threshed, lang="ind")
        return raw_extracted_text

    def word_to_number_converter(self, word):
        word_dict = {
            '|': "1"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def nik_extract(self, word):
        word_dict = {
            'b': "6",
            'e': "2",
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res

    def extract(self, extracted_result):
        for word in extracted_result.split("\n"):
            if "NIK" in word:
                word = word.split(':')
                self.result.nik = self.nik_extract(word[-1].replace(" ", ""))
                continue

            if "Nama" in word:
                word = word.split(':')
                self.result.nama = word[-1].replace('Nama ', '')
                continue

            if "Tempat" in word:
                word = word.split(':')
                self.result.tanggal_lahir = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])[0]
                self.result.tempat_lahir = word[-1].replace(self.result.tanggal_lahir, '')
                continue

            if 'Darah' in word:
                match = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)
                if match:  # Check if a match was found
                    self.result.jenis_kelamin = match[0]
                else:
                    self.result.jenis_kelamin = "Unknown"  # Default value

                word_parts = word.split(':') if word else []  # Ensure word is not None
                if len(word_parts) > 1:
                    self.result.golongan_darah = re.search("(O|A|B|AB)", word_parts[-1]) or '-'
                else:
                    self.result.golongan_darah = '-'

            if 'jenis kelamin' in word:
                match = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)
                if match:  # Ensure a match was found
                    self.result.jenis_kelamin = match[0]
                else:
                    self.result.jenis_kelamin = "Unknown"  # Handle no match

            if 'Alamat' in word:
                self.result.alamat = self.word_to_number_converter(word).replace("Alamat ", "")
            if 'NO.' in word:
                self.result.alamat = self.result.alamat + ' ' + word
            if "Kecamatan" in word:
                self.result.kecamatan = word.split(':')[1].strip()
            if "Desa" in word:
                wrd = word.split()
                desa = []
                for wr in wrd:
                    if not 'desa' in wr.lower():
                        desa.append(wr)
                self.result.kelurahan_atau_desa = ''.join(desa)

            if 'Kewarganegaraan' in word:
                self.result.kewarganegaraan = word.split(':')[1].strip()
            if 'Pekerjaan' in word:
                wrod = word.split()
                pekerjaan = []
                for wr in wrod:
                    if not '-' in wr:
                        pekerjaan.append(wr)
                self.result.pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan', '').strip()

            if 'Agama' in word:
                # Remove the prefix 'Agama' and strip any extra spaces
                agama_value = word.replace('Agama', "").strip() if word else ''

                # Define a list of known religions
                known_religions = ["ISLAM", "KATOLIK", "PROTESTAN", "HINDU", "BUDHA"]

                # Normalize agama_value by checking for known religions
                detected_religion = None
                for religion in known_religions:
                    if religion in agama_value:  # Check if the known religion is part of the detected value
                        detected_religion = religion
                        break

                if detected_religion:
                    self.result.agama = detected_religion
                else:
                    self.result.agama = agama_value  # Handle cases where no known religion is found

            if 'Perkawinan' in word:
                # Split the word and get the value
                status_value = word.split(':')[1].strip()  # Use strip() to remove any leading/trailing spaces

                # Check if the value is valid
                if status_value in ["BELUM KAWIN", "KAWIN"]:
                    self.result.status_perkawinan = status_value
                else:
                    # Handle invalid value if needed, e.g., set to None or log a message
                    self.result.status_perkawinan = None  # or some default value
            if "RTRW" in word:
                word = word.replace("RTRW", '')
                parts = word.split('/')
                if len(parts) > 1:  # Ensure there are at least 2 parts
                    self.result.rt = parts[0].strip()
                    self.result.rw = parts[1].strip()
                else:
                    # Handle the case where there is no '/' or insufficient parts
                    self.result.rt = parts[0].strip() if parts else '-'
                    self.result.rw = '-'

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return self.result.to_json()  # Ensure you're calling the KTPInformation's to_json method