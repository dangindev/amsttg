# assets/views/asset_views.py

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions

from assets.models.asset import Asset
from assets.serializers.asset_serializer import AssetSerializer
from assets.forms import AssetForm  

import csv
import io
from django.contrib import messages
from django.http import HttpResponse
from django.db import IntegrityError

# Tạo logger (file log này sẽ được cấu hình trong settings.py)
logger = logging.getLogger(__name__)


# ========== 1. API CRUD (Django REST Framework) ==========
class AssetViewSet(viewsets.ModelViewSet):
    """
    API CRUD Asset 
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]


# ========== 2. Danh sách & Chi tiết (HTML) ==========

@login_required
def asset_list_view(request):
    """
    Hiển thị danh sách asset (HTML).
    """
    assets = Asset.objects.all()
    return render(request, 'assets/list.html', {'assets': assets})


@login_required
def asset_detail_view(request, pk):
    """
    Hiển thị chi tiết 1 asset (HTML).
    """
    asset_obj = get_object_or_404(Asset, pk=pk)
    return render(request, 'assets/detail.html', {'asset': asset_obj})


# ========== 3. Gộp Tạo / Chỉnh sửa Asset (ModelForm) ==========

@login_required
def asset_form_view(request, pk=None):
    """
    Gộp Create/Edit trong 1 view:
    - pk=None => Tạo mới
    - pk có => Sửa
    """
    if pk:
        asset_obj = get_object_or_404(Asset, pk=pk)
    else:
        asset_obj = None

    if request.method == 'POST':
        if asset_obj:
            form = AssetForm(request.POST, instance=asset_obj)
        else:
            form = AssetForm(request.POST)

        try:
            if form.is_valid():
                form.save()
                return redirect('asset_list')
        except IntegrityError as e:
            logger.error(f"IntegrityError (AssetForm): {str(e)}")
            form.add_error('code', 'Mã code này đã tồn tại. Vui lòng nhập code khác.')
    else:
        if asset_obj:
            form = AssetForm(instance=asset_obj)
        else:
            form = AssetForm()

    return render(request, 'assets/edit.html', {
        'form': form,
        'asset': asset_obj,
    })
# ========== 4. Xóa Asset ==========

@login_required
def asset_delete_view(request):
    """
    Xóa asset qua POST. (Dùng modal confirm -> gửi POST)
    """
    if request.method == 'POST':
        pk = request.POST.get('pk')
        asset_obj = get_object_or_404(Asset, pk=pk)
        asset_obj.delete()
    # Dù xóa hay fail => quay lại danh sách
    return redirect('asset_list')


# ========== 5. Import / Export ==========



@login_required
def asset_import_view(request):
    """
    Upload file CSV -> tạo Asset. Tích hợp qua modal "Import CSV".
    """
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if not file_obj:
            messages.error(request, "Chưa chọn file CSV!")
            return redirect('asset_list')

        try:
            decoded_file = file_obj.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            # Dòng đầu: header?
            # name, code, description, ...
            header = next(reader, None)
            count = 0
            for row in reader:
                # Tùy logic. Giả sử: row[0]=name, row[1]=code, row[2]=desc
                name = row[0]
                code = row[1]
                description = row[2] if len(row)>2 else ''
                # Tạo asset
                Asset.objects.create(name=name, code=code, description=description)
                count += 1
            messages.success(request, f"Đã import {count} tài sản.")
        except (UnicodeDecodeError, IndexError, IntegrityError, Exception) as e:
            messages.error(request, f"Lỗi import: {str(e)}")

        return redirect('asset_list')
    else:
        # Không cho GET => redirect
        return redirect('asset_list')


def asset_export_view(request):
    columns = request.GET.getlist('columns')
    if not columns:
        columns = ['name','code','description']
    
    # Tạo response, gắn charset=utf-8-sig
    response = HttpResponse(
        content_type='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': 'attachment; filename="assets_export.csv"'},
    )
    
    # Ghi BOM để Excel Windows nhận diện UTF-8
    response.write('\ufeff')

    # Bạn có thể dùng dấu phẩy "," hoặc chấm phẩy ";" tùy địa phương
    # Nhiều khi Excel Việt Nam quen ";" làm cột, ta thử delimiter=';'
    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    # Ghi header
    writer.writerow(columns)

    # Ghi data
    from assets.models.asset import Asset
    for asset in Asset.objects.all():
        row_data = []
        for col in columns:
            val = getattr(asset, col, "")
            row_data.append(str(val))
        writer.writerow(row_data)

    return response
