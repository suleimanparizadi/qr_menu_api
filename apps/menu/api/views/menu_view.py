from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.menu.services import analytics, item_service, menu_service, public_menu, section_service
from apps.menu.api.serializers import create_menu_serializer, display_serializer, menu_serializer
from apps.menu.models.menu_model import QRMenu, MenuSection, MenuItem




User = get_user_model()



class PublicMenuView(views.APIView):


    permission_classes = [permissions.AllowAny]

    def get(self, request, menu_id):

        service = public_menu.PublicMenuService()
        result = service.get_menu(menu_id)

        if result.success:
            menu_serializer = display_serializer.PublicMenuSerializer(
                result.data['menu'])# just serialize the menu
            
            section_serializer = display_serializer.MenuSectionSerializer(
                result.data['sections'], many=True)# call the queryset by the serializer data

                                                                 
            return Response({'menu':menu_serializer.data,
                            'sections':section_serializer.data},
                                                                status=status.HTTP_200_OK)

        return Response({'message':result.message}, status=status.HTTP_404_NOT_FOUND)





class MenuView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self ,request):

        serializer = create_menu_serializer.CreateMenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = menu_service.MenuService(request.user)

        result = service.create_menu(**serializer.validated_data)

        if result.success:
            return Response({'message':result.message, 'menu':serializer.data},
                            status=status.HTTP_201_CREATED)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, menu_id):

        menu = get_object_or_404(QRMenu, id=menu_id, user=request.user)
        serializer = create_menu_serializer.UpdateMenuSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)


        for field, value in serializer.validated_data.items():
            setattr (menu, field, value)

        menu.save()

        return Response({'message': 'Menu updated successfully'}, status=status.HTTP_200_OK) 



    def delete(self, request, menu_id):
    
        service = menu_service.MenuService(request.user)

        result = service.delete_menu(menu_id)

        return Response({'message':result.message},
                         status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)




class SectionView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self, request, menu_id):

        serializer = create_menu_serializer.SectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = section_service.SectionService(request.user)
        result = service.create_section(
            menu_id=menu_id,
            name=serializer.validated_data.get('name', 'Main'),
            start_time=serializer.validated_data.get('start_time'),
            end_time=serializer.validated_data.get('end_time'),
            order=serializer.validated_data.get('order', 0)
            )
        

        if result.success:

            section_serializer = display_serializer.MenuSectionSerializer(result.data['section'])
            return Response({'message':result.message, 'section':section_serializer.data},
                            status=status.HTTP_201_CREATED)
        

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)




    def patch(self, request, section_id):

        section = get_object_or_404(MenuSection, id=section_id)

        serializer = create_menu_serializer.SectionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)


        for field, value in serializer.validated_data.items():
            setattr (section, field, value)

        section.save()

        return Response({'message': 'section updated successfully'}, status=status.HTTP_200_OK) 





    def delete(self, request, section_id):
    
        service = section_service.SectionService(request.user)

        result = service.delete_sections(section_id)

        return Response({'message':result.message},
                         status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)






class ItemView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self, request, section_id):
        serializer = create_menu_serializer.AddItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = item_service.ItemService(request.user)
        result = service.add_item(
            section_id=section_id,
            items_data=serializer.validated_data['items']
            )

        if result.success:
            return Response({'message':result.message, 'items_count':result.data['items_count']},
                            status=status.HTTP_201_CREATED)

        return Response({'message':result.message}, status=status.HTTP_400_BAD_REQUEST)
        


    def patch(self, request, item_id):

        item = get_object_or_404(MenuItem, id=item_id)

        serializer = create_menu_serializer.UpdateItemSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr (item, field, value)

        item.save(update_fields=list(serializer.validated_data.keys()))


        return Response(
            {'message': 'Item updated successfully'},
            status=status.HTTP_200_OK
        )



    def delete(self, request, item_id):

        service = item_service.ItemService(request.user)
        result = service.delete_item()

        return Response({'message':result.message},
                         status=status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST)




    