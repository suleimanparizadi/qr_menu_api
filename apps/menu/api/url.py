from django.urls import path
from apps.menu.api.views.menu_view import MenuView, SectionView, ItemView, MenuAnalyticView


urlpatterns = [
    path('menus/', MenuView.as_view(), name='menu_list_create'),
    path('menus/<int:menu_id>/', MenuView.as_view(), name='menu_detail'),
    
    path('menus/<int:menu_id>/sections/', SectionView.as_view(), name='section_create'),
    path('sections/<int:section_id>/', SectionView.as_view(), name='section_detail'),
    
    path('sections/<int:section_id>/items/', ItemView.as_view(), name='item_create'),
    path('items/<int:item_id>/', ItemView.as_view(), name='item_detail'),
    
    path('menus/<int:menu_id>/analytics/', MenuAnalyticView.as_view(), name='menu_analytics'),
]