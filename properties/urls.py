from django.urls import path

from . import views

app_name = "api_properties"

urlpatterns = [
    path("", views.PropertyListView.as_view(), name="property-list"),
    path(
        "<uuid:pk>/",
        views.PropertyDetailView.as_view(),
        name="property-detail",
    ),
    path(
        "features/",
        views.PropertyFeatureListView.as_view(),
        name="feature-list",
    ),
    path(
        "features/categories/",
        views.PropertyFeatureCategoryListView.as_view(),
        name="feature-category-list",
    ),
    path(
        "<uuid:pk>/images/",
        views.PropertyImageView.as_view(),
        name="property-images",
    ),
    path(
        "<uuid:pk>/images/<uuid:image_pk>/",
        views.PropertyImageDetailView.as_view(),
        name="property-image-detail",
    ),
    path(
        "<uuid:pk>/videos/",
        views.PropertyVideoView.as_view(),
        name="property-videos",
    ),
    path(
        "<uuid:pk>/documents/",
        views.PropertyDocumentView.as_view(),
        name="property-documents",
    ),
    path(
        "<uuid:pk>/comment/",
        views.PropertyCommentView.as_view(),
        name="property-comments",
    ),
]
