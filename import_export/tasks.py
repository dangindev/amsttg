# import_export/tasks.py

import time, csv
from celery import shared_task
from django.db import IntegrityError
from django.core.files.storage import default_storage
from assets.models.asset import Asset
from django.db import transaction
import csv

@shared_task
def import_data_celery(file_path, name_col, code_col, desc_col):
    """
    parse CSV -> nếu trùng code => ghi đè (update)
    """
    with default_storage.open(file_path, 'r') as f:
        lines = f.read().splitlines()

    sample = "\n".join(lines[:5])
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(lines, dialect)
    header = next(reader, None)
    total = sum(1 for _ in reader)

    with default_storage.open(file_path, 'r') as f2:
        lines2 = f2.read().splitlines()
    sample2 = "\n".join(lines2[:5])
    try:
        dialect2 = csv.Sniffer().sniff(sample2)
    except csv.Error:
        dialect2 = csv.excel

    reader2 = csv.reader(lines2, dialect2)
    next(reader2, None)  # skip header

    current = 0
    nc = int(name_col)
    cc = int(code_col)
    dc = desc_col and int(desc_col) or None

    for row in reader2:
        current += 1
        import_data_celery.update_state(
            state='PROGRESS',
            meta={'current': current, 'total': total}
        )

        name_val = row[nc] if nc < len(row) else ''
        code_val = row[cc] if cc < len(row) else ''
        desc_val = ''
        if dc is not None and dc < len(row):
            desc_val = row[dc]

        # Ghi đè: update_or_create -> nếu code_val đã tồn tại => update
        Asset.objects.update_or_create(
            code=code_val,
            defaults={
                'name': name_val,
                'description': desc_val,
            }
        )

        time.sleep(0.01)

    return {'current': total, 'total': total, 'status': 'Done'}
