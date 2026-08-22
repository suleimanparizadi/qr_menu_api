from rest_framework import serializers
from apps.menu.models import menu_model


# this serializers are just for being shown in menus 


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu_model.MenuItem
        fields = ['id', 'item', 'description', 'price', 'order', 'available']



class MenuSectionSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = menu_model.MenuSection
        fields = ['id', 'name', 'start_time', 'end_time', 'order', 'items']



class PublicMenuSerializer(serializers.ModelSerializer):
    # for customers
    
    class Meta:
        model = menu_model.QRMenu
        fields = ['id', 'title', 'description',]


class MenuSerializer(serializers.ModelSerializer):
    # for menu owner
    sections = MenuSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = menu_model.QRMenu
        fields = ['id', 'title', 'description', 'qr_code', 'available', 'sections', 'created_at', 'updated_at']

