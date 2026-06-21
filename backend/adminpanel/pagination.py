from rest_framework.pagination import PageNumberPagination


class AdminPagination(PageNumberPagination):
    """Server-side pagination for admin tables (uiux.md §15 / django.md §7)."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
