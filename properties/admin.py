from django.contrib import admin

from .models import (
    Property,
    PropertyDocument,
    PropertyFeature,
    PropertyFeatureCategory,
    PropertyFloorPlan,
    PropertyImage,
    PropertyVideo,
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 0


class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "title", "property_type", "operation",
        "status", "sale_price", "rent_price", "is_active",
    )
    list_filter = ("property_type", "operation", "status", "is_active", "is_featured")
    search_fields = ("reference", "title", "description")
    prepopulated_fields = {"slug": ("reference", "title")}
    inlines = [PropertyImageInline, PropertyVideoInline]


@admin.register(PropertyFeatureCategory)
class PropertyFeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category", "icon")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("property", "title", "is_primary", "order")
    list_filter = ("is_primary",)


@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = ("property", "title", "is_private")


@admin.register(PropertyFloorPlan)
class PropertyFloorPlanAdmin(admin.ModelAdmin):
    list_display = ("property", "title", "order")


@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ("property", "title", "is_virtual_tour", "order")
