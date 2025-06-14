from rest_framework.pagination import PageNumberPagination


class ContestPaginator(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    page_query_param = "page"
    max_page_size = 900
