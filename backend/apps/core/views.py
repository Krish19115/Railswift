from django.db import connection
from django.db.utils import DatabaseError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    database = "ok"
    http_status = status.HTTP_200_OK
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        database = "unavailable"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        {"status": "ok" if database == "ok" else "degraded", "database": database},
        status=http_status,
    )
