# import_export/utils.py
import csv
from django.core.files.storage import default_storage

def parse_csv(file_obj):
    decoded_file = file_obj.read().decode('utf-8').splitlines()
    sample = "\n".join(decoded_file[:5])
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(decoded_file, dialect)
    header = next(reader, None)
    data = []
    for row in reader:
        data.append(row)
    return data

def save_temp_file(upload_file):
    file_path = f"temp/{upload_file.name}"
    saved_path = default_storage.save(file_path, upload_file)
    return saved_path
