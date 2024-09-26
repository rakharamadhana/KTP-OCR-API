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
            if "PROVINSI" in word:
                # Extract the part after "PROVINSI" and clean it
                provinsi_part = word.split(':')[-1].strip() if ':' in word else word.replace("PROVINSI", "").strip()

                # Initialize a list to hold the full province name parts
                provinsi_parts = [provinsi_part]

                # Get the index of the current word to continue processing from the next line
                current_index = extracted_result.split("\n").index(word)

                # Loop to collect additional province parts until hitting an empty line or known field
                next_line_index = current_index + 1
                while next_line_index < len(extracted_result.split("\n")):
                    next_line = extracted_result.split("\n")[next_line_index].strip()

                    # If the next line is empty, continue to the next line
                    if not next_line:
                        next_line_index += 1
                        continue

                    # If the next line starts with a known field or a keyword, stop the loop
                    if any(keyword in next_line for keyword in
                           ["KOTA", "NIK"]):
                        break

                    # If it's a part of the province name, add it to provinsi_parts
                    provinsi_parts.append(next_line)

                    # Move to the next line
                    next_line_index += 1

                # Join all collected parts for the final province name
                self.result.provinsi = ' '.join(provinsi_parts).strip()

            if "KOTA" in word:
                # Extract the part after "KOTA" and clean it
                kota_part = word.split(':')[-1].strip() if ':' in word else word.replace("KOTA", "").strip()

                # Initialize a list to hold the full city name parts
                kota_parts = [kota_part]

                # Get the index of the current word to continue processing from the next line
                current_index = extracted_result.split("\n").index(word)

                # Loop to collect additional city parts until hitting an empty line or known field
                next_line_index = current_index + 1
                while next_line_index < len(extracted_result.split("\n")):
                    next_line = extracted_result.split("\n")[next_line_index].strip()

                    # If the next line is empty, continue to the next line
                    if not next_line:
                        next_line_index += 1
                        continue

                    # If the next line starts with a known field or a keyword, stop the loop
                    if any(keyword in next_line for keyword in
                           ["NIK", "Nama", ":"]):
                        break

                    # If it's a part of the city name, add it to kota_parts
                    kota_parts.append(next_line)

                    # Move to the next line
                    next_line_index += 1

                # Join all collected parts for the final city name
                self.result.kota_kab = ' '.join(kota_parts).strip()

            if "NIK" in word:
                word = word.split(':')
                self.result.nik = self.nik_extract(word[-1].replace(" ", ""))
                continue

            if "Nama" in word:
                # Split the word at the colon and get the part after "Nama"
                name_part = word.split(':')[-1].strip().replace('Nama', '')

                # Initialize a list to hold the full name parts
                name_parts = [name_part]

                # Get the index of the current word to continue processing from the next line
                current_index = extracted_result.split("\n").index(word)

                # Initialize a variable to track the next line
                next_line_index = current_index + 1

                # Loop to collect additional name parts until hitting an empty line or known field
                while next_line_index < len(extracted_result.split("\n")):
                    next_line = extracted_result.split("\n")[next_line_index].strip()

                    # If the next line is empty, continue to the next line
                    if not next_line:
                        next_line_index += 1
                        continue

                    # If the next line starts with a known field or a keyword, stop the loop
                    if any(keyword in next_line for keyword in
                           ["Tempat", "Lahir", "Tempat/Tgi Lahir", ":", ","]):
                        break

                    # If it's a part of the name, add it to name_parts
                    name_parts.append(next_line)

                    # Move to the next line
                    next_line_index += 1

                # Join all collected parts for the final name
                self.result.nama = ' '.join(name_parts).strip()  # Combine the parts into a single name string

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
                self.result.pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan',
                                                                    '').strip()  # Join and strip extra spaces
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

            if "RI/RW" in word or "RT/RW" in word or "RTRW" in word:  # Check for either "RI/RW" or "RT/RW"
                if "RI/RW" in word:
                    word = word.replace("RI/RW", '')  # Remove the "RI/RW" prefix
                elif "RTRW" in word:
                    word = word.replace("RTRW", '')  # Remove the "RI/RW" prefix
                else:
                    word = word.replace("RT/RW", '')  # Remove the "RT/RW" prefix if detected

                parts = word.split(':')  # Split the line at the colon
                if len(parts) > 1:  # Ensure there is something after the colon
                    rt_rw = parts[1].strip()  # Get the part after the colon
                    rt_rw_parts = rt_rw.split('/')  # Split by '/'
                    if len(rt_rw_parts) > 1:  # Ensure there are at least 2 parts
                        self.result.rt = rt_rw_parts[0].strip()  # Assign the first part as RT
                        self.result.rw = rt_rw_parts[1].strip()  # Assign the second part as RW
                    else:
                        self.result.rt = rt_rw.strip()  # If no '/', assign the whole part to RT
                        self.result.rw = '-'  # Assign '-' if RW is missing
                else:
                    self.result.rt = '-'  # Assign '-' if no value is found
                    self.result.rw = '-'  # Assign '-' if no value is found

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return self.result.to_json()  # Ensure you're calling the KTPInformation's to_json method

    def to_raw_result(self):
        return self.raw_result  # Return the raw OCR result
