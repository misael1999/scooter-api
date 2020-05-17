from rest_framework import viewsets
# Auth
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class ScooterViewSet(viewsets.GenericViewSet):
    # Auth for swagger UI
    authentication_classes = (JWTAuthentication, BasicAuthentication)

    def set_response(self, status, data, message):
        return {"status": status, "data": data, "message": message}

    def set_error_response(self, status, field, message):
        return {"status": status, "errors": {"field": field, "message": message}}

    def get_queryset_pagination(self, queryset, serialize_class):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serialize_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serialize_class(queryset, many=True)
        return serializer.data



