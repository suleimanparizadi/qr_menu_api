from django.urls import path
from apps.menu.api.views.menu_view import (
MenuView, MenuDetailView, MenuPreviewView,
    SectionView, ItemView, MenuAnalyticView,
)

app_name = 'menu'


urlpatterns = [
    # Menus
    path('menus/', MenuView.as_view(), name='menu-list-create'),
    path('menus/<int:menu_id>/', MenuDetailView.as_view(), name='menu-detail'),
    path('menus/<int:menu_id>/preview/', MenuPreviewView.as_view(), name='menu-preview'),
    path('menus/<int:menu_id>/analytics/', MenuAnalyticView.as_view(), name='menu-analytics'),

    # Sections
    path('menus/<int:menu_id>/sections/', SectionView.as_view(), name='section-create'),
    path('sections/<int:section_id>/', SectionView.as_view(), name='section-detail'),

    # Items
    path('sections/<int:section_id>/items/', ItemView.as_view(), name='item-create'),
    path('items/<int:item_id>/', ItemView.as_view(), name='item-detail'),
]