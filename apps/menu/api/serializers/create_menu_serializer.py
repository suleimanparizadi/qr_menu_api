from rest_framework import serializers
from django.core.exceptions import ValidationError


class CreateMenuSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=225)
    description = serializers.CharField(max_length=350, required=False, allow_blank=True)




class UpdateMenuSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=225, required=True)
    description = serializers.CharField(max_length=350, required=False, allow_blank=True)
    available = serializers.BooleanField(required=False)




class SectionSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=225, required=False)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    order = serializers.IntegerField(required=False)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()




class ItemInputSerializer(serializers.Serializer):
    item = serializers.CharField(max_length=225)
    description = serializers.CharField(max_length=225, required=False, allow_blank=True)
    price = serializers.IntegerField(min_value=0)
    order = serializers.IntegerField(required=False)



class AddItemsSerializer(serializers.Serializer):
    items = ItemInputSerializer(many=True, allow_empty=False)
    
    def validate_items(self, value):

        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 items per request")
        
        return value




class UpdateItemSerializer(serializers.Serializer):
    item = serializers.CharField(max_length=225, required=False)
    description = serializers.CharField(max_length=225, required=False, allow_blank=True)
    price = serializers.IntegerField(min_value=0, required=False)
    order = serializers.IntegerField(required=False)