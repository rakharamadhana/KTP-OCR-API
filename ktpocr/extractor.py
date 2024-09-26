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
        self.raw_result = ""  # Initialize a variable to store raw OCR text
        self.master_process()

    def process(self, image):
        raw_extracted_text = pytesseract.image_to_string(self.threshed, lang="ind")
        self.raw_result = raw_extracted_text  # Store the raw OCR text
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
        # Mapping of characters to their corresponding number replacements
        word_dict = {
            'b': "6",
            'e': "2",
            '?': "7"
        }

        res = ""
        for letter in word:
            # Check if the letter is numeric; if so, add it to the result
            if letter.isdigit():
                res += letter
            else:
                # Replace non-numeric letters with corresponding numbers from the dictionary
                res += word_dict.get(letter, "")  # Default to "" to ignore if not found

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

                # Extract the date of birth using regex
                date_match = re.search(r"([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])
                if date_match:
                    self.result.tanggal_lahir = date_match[0]
                    # Remove the found date from the string to isolate tempat lahir
                    tempat_lahir_raw = word[-1].replace(self.result.tanggal_lahir, '')

                    # Use regex to keep only letters and spaces
                    self.result.tempat_lahir = re.sub(r'[^a-zA-Z\s]', '',
                                                      tempat_lahir_raw).strip()  # Clean and strip spaces
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
                    # Check if 'desa' is not in the word and strip leading unwanted characters
                    cleaned_word = wr.lstrip(': ,')  # Strip leading ':', ' ', and ','
                    if 'desa' not in cleaned_word.lower():  # Ensure 'desa' is not in the cleaned word
                        desa.append(cleaned_word.strip())  # Append the stripped word to the list
                self.result.kelurahan_atau_desa = ' '.join(desa).strip()  # Join the words and strip extra spaces

            if 'Kewarganegaraan' in word:
                self.result.kewarganegaraan = word.split(':')[1].strip()
            if 'Pekerjaan' in word:
                wrod = word.split()
                pekerjaan = []
                for wr in wrod:
                    # Clean the word by stripping unwanted leading characters
                    cleaned_word = wr.lstrip(': ,')  # Strip leading ':', ' ', and ','
                    if '-' not in cleaned_word:  # Ensure there's no '-' in the cleaned word
                        pekerjaan.append(cleaned_word.strip())  # Append the stripped word to the list
                self.result.pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan','').strip()  # Join and strip extra spaces
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

                # Normalize the status_value to handle variations
                if re.search(r'BLUM|BELUM', status_value):  # Check for variations of 'BELUM'
                    status_value = "BELUM KAWIN"  # Normalize to 'BELUM KAWIN'
                elif "KAWIN" in status_value:
                    status_value = "KAWIN"  # Normalize to 'KAWIN'

                # Check if the normalized value is valid
                if status_value in ["BELUM KAWIN", "KAWIN"]:
                    self.result.status_perkawinan = status_value
                else:
                    # Handle invalid value if needed, e.g., set to None or log a message
                    self.result.status_perkawinan = status_value  # or some default value

            if "RTRW" in word:
                word = word.replace("RTRW", '')
                parts = word.split('/')
                if len(parts) > 1:  # Ensure there are at least 2 parts
                    self.result.rt = parts[0].strip()
                    self.result.rw = parts[1].strip()
                else:
                    # Handle the case where there is no '/' or insufficient parts
                    self.result.rt = word
                    self.result.rw = word

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return self.result.to_json()  # Ensure you're calling the KTPInformation's to_json method

    def to_raw_result(self):
        return self.raw_result  # Return the raw OCR result