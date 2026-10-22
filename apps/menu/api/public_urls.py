from django.urls import path
from apps.menu.api.views.menu_view import PublicMenuView

app_name = 'public_url'
urlpatterns = [
    path('<int:menu_id>/', PublicMenuView.as_view(), name='public_menu'),
]


