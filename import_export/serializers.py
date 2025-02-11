from rest_framework import serializers

class ImportFileSerializer(serializers.Serializer):
    """
    Serializer để xử lý file upload qua API.
    """
    file = serializers.FileField()
    # Thêm validate tùy ý
