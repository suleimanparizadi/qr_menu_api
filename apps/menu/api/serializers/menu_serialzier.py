from rest_framework import serializers
from apps.menu.models import menu_model


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu_model.MenuItem
        fields = ['id', 'item', 'description', 'price', 'order', 'available']




class MenuSectionSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = menu_model.MenuSection
        fields = ['id', 'name', 'start_time', 'end_time', 'order', 'items']




class MenuSerializer(serializers.ModelSerializer):
    sections = MenuSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = menu_model.QRMenu
        fields = ['id', 'title', 'description', 'available', 'qr_code', 'sections', 'created_at', 'updated_at']




class PublicMenuSerializer(serializers.ModelSerializer):
    """
    Serializer for the public menu endpoint.
    Shows only active sections (handled by the service query).
    """
    sections = MenuSectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = menu_model.QRMenu
        fields = ['id', 'title', 'description', 'sections']


        