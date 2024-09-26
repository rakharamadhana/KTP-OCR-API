from collections import OrderedDict
import json


class KTPInformation(object):
    def __init__(self):
        self.nik = ""
        self.nama = ""
        self.tempat_lahir = ""
        self.tanggal_lahir = ""
        self.jenis_kelamin = ""
        self.golongan_darah = ""
        self.provinsi = ""
        self.kota = ""
        self.alamat = ""
        self.rt = ""
        self.rw = ""
        self.kelurahan_atau_desa = ""
        self.kecamatan = ""
        self.agama = ""
        self.status_perkawinan = ""
        self.pekerjaan = ""
        self.kewarganegaraan = ""
        self.berlaku_hingga = "SEUMUR HIDUP"

    def to_ordered_dict(self):
        return OrderedDict([
            ("nik", self.nik),
            ("nama", self.nama),
            ("tempat_lahir", self.tempat_lahir),
            ("tanggal_lahir", self.tanggal_lahir),
            ("jenis_kelamin", self.jenis_kelamin),
            ("golongan_darah", self.golongan_darah),
            ("alamat", self.alamat),
            ("rt", self.rt),
            ("rw", self.rw),
            ("kelurahan_atau_desa", self.kelurahan_atau_desa),
            ("kecamatan", self.kecamatan),
            ("agama", self.agama),
            ("status_perkawinan", self.status_perkawinan),
            ("pekerjaan", self.pekerjaan),
            ("kewarganegaraan", self.kewarganegaraan),
            ("berlaku_hingga", self.berlaku_hingga),
        ])

    def to_json(self):
        return json.dumps(self.to_ordered_dict(), indent=4)