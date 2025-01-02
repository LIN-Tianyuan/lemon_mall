from django.urls import include,re_path

from . import views

app_name = 'goods'

urlpatterns = [
    # Product List Page
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    # top seller
    re_path(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # Product Details
    re_path(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    # Statistics on the number of visits to categorized products
    re_path(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view())
]