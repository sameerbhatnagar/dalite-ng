from rest_framework.pagination import PageNumberPagination


class SearchPagination(PageNumberPagination):
    page_size = 10
