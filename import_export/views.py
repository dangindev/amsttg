# import_export/views.py

import csv, uuid
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.contrib import messages
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from celery.result import AsyncResult
from .tasks import import_data_celery
from assets.models.asset import Asset

@login_required
def upload_csv_view(request):
    """
    Bước 1: Upload file CSV -> parse Header -> cho user map cột
    Hiển thị choose_columns.html
    """
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if not file_obj:
            messages.error(request, "Chưa chọn file CSV.")
            return redirect('asset_list')

        # Lưu file tạm
        file_name = f"temp/{uuid.uuid4()}_{file_obj.name}"
        saved_path = default_storage.save(file_name, file_obj)

        # Tự đoán delimiter
        lines = default_storage.open(saved_path, 'r').read().splitlines()
        sample = "\n".join(lines[:5])
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel

        reader = csv.reader(lines, dialect)
        header = next(reader, None)
        if not header:
            messages.error(request, "File CSV rỗng hoặc sai format!")
            default_storage.delete(saved_path)
            return redirect('asset_list')

        # Tạo danh sách cột
        columns = []
        for i, col in enumerate(header):
            columns.append({'index': i, 'name': col})

        # sang choose_columns.html
        return render(request, 'import_export/choose_columns.html', {
            'file_path': saved_path,
            'columns': columns,
        })
    else:
        # GET => form import.html
        return render(request, 'import_export/import.html')


@login_required
def mapping_confirm_view(request):
    """
    Bước 2: user POST map cột -> parse CSV chi tiết -> check DB -> ok => mapping_ok.html or import_error
    """
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        name_col = request.POST.get('name_col')
        code_col = request.POST.get('code_col')
        desc_col = request.POST.get('desc_col')  # optional

        if not file_path or not name_col or not code_col:
            messages.error(request, "Chưa đủ cột name, code.")
            return redirect('asset_list')

        lines = default_storage.open(file_path, 'r').read().splitlines()
        sample = "\n".join(lines[:5])
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel

        reader = csv.reader(lines, dialect)
        header = next(reader, None)

        error_list = []
        row_index = 1
        for row in reader:
            row_index += 1
            try:
                nc = int(name_col)
                cc = int(code_col)
                dc = desc_col and int(desc_col) or None

                name_val = row[nc] if nc<len(row) else ''
                code_val = row[cc] if cc<len(row) else ''
                desc_val = ''
                if dc is not None and dc<len(row):
                    desc_val = row[dc]

                # check code
                # if Asset.objects.filter(code=code_val).exists():
                #     error_list.append(f"Dòng {row_index}: code={code_val} đã tồn tại DB.")
            except Exception as e:
                error_list.append(f"Dòng {row_index}: {str(e)}")

        if error_list:
            return render(request, 'import_export/import_error.html', {
                'error_list': error_list,
            })
        else:
            # Ko lỗi => mapping_ok
            return render(request, 'import_export/mapping_ok.html', {
                'file_path': file_path,
                'name_col': name_col,
                'code_col': code_col,
                'desc_col': desc_col,
            })
    else:
        return redirect('asset_list')


@login_required
def import_start_view(request):
    """
    Bước 3: user POST => gọi Celery => sang progress
    """
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        name_col = request.POST.get('name_col')
        code_col = request.POST.get('code_col')
        desc_col = request.POST.get('desc_col')

        if not file_path or not name_col or not code_col:
            messages.error(request, "Thiếu params.")
            return redirect('asset_list')

        task = import_data_celery.delay(file_path, name_col, code_col, desc_col)
        return redirect('import_progress', task_id=task.id)
    else:
        return redirect('asset_list')


@login_required
def import_progress_view(request, task_id):
    return render(request, 'import_export/progress.html', {'task_id': task_id})

@login_required
def import_progress_status_json(request, task_id):
    result = AsyncResult(task_id)
    if result.state == 'PROGRESS':
        return JsonResponse({
            'state': 'PROGRESS',
            'current': result.info.get('current', 0),
            'total': result.info.get('total', 0),
        })
    elif result.state == 'SUCCESS':
        return JsonResponse({
            'state': 'SUCCESS',
            'current': result.info.get('current', 0),
            'total': result.info.get('total', 0),
            'status': result.info.get('status', ''),
        })
    elif result.state == 'FAILURE':
        return JsonResponse({
            'state': 'FAILURE',
            'info': str(result.result),
        })
    else:
        return JsonResponse({
            'state': result.state,
            'info': str(result.info),
        })
