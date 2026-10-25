from django.contrib import admin
from apps.menu.models.menu_model import QRMenu, MenuSection, MenuItem, MenuView


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ['item', 'description', 'price', 'order', 'available']
    ordering = ['order']


class MenuSectionInline(admin.TabularInline):
    model = MenuSection
    extra = 0
    fields = ['name', 'start_time', 'end_time', 'order']
    ordering = ['order']
    show_change_link = True


@admin.register(QRMenu)
class QRMenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'available', 'view_count', 'created_at']
    list_filter = ['available', 'created_at']
    search_fields = ['title', 'user__phone_number']
    readonly_fields = ['qr_code_preview', 'created_at', 'updated_at']
    inlines = [MenuSectionInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'available')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_preview')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def view_count(self, obj):
        return obj.views.count()
    view_count.short_description = 'Views'
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return f'<img src="{obj.qr_code.url}" style="max-height: 200px;" />'
        return 'No QR code generated yet'
    qr_code_preview.short_description = 'QR Preview'
    qr_code_preview.allow_tags = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Superusers see everything; regular users see only their own
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def save_model(self, request, obj, form, change):
        # Auto-assign user when a regular user creates a menu
        if not change and not request.user.is_superuser:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu', 'start_time', 'end_time', 'order']
    list_filter = ['menu']
    search_fields = ['name', 'menu__title']
    inlines = [MenuItemInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(menu__user=request.user)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'section', 'price', 'available', 'order']
    list_filter = ['available', 'section__menu']
    search_fields = ['item', 'section__name', 'section__menu__title']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(section__menu__user=request.user)


@admin.register(MenuView)
class MenuViewAdmin(admin.ModelAdmin):
    list_display = ['menu', 'viewed_at']
    list_filter = ['viewed_at']
    readonly_fields = ['menu', 'viewed_at']
    
    def has_add_permission(self, request):
        # Views are created automatically, not manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Read-only
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(menu__user=request.user)