from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Tags
from common.models import Attachments, Comment, Profile
from common.serializer import CommentSerializer
from contacts.models import Contact
from teams.models import Teams

from .models import (
    Property,
    PropertyDocument,
    PropertyFeature,
    PropertyFeatureCategory,
    PropertyFloorPlan,
    PropertyImage,
    PropertyVideo,
)
from .serializer import (
    PropertyCommentSwaggerSerializer,
    PropertyCreateSerializer,
    PropertyCreateSwaggerSerializer,
    PropertyDetailSerializer,
    PropertyDocumentSerializer,
    PropertyFeatureCategorySerializer,
    PropertyFeatureSerializer,
    PropertyFloorPlanSerializer,
    PropertyImageSerializer,
    PropertyListSerializer,
    PropertyVideoSerializer,
)


class PropertyListView(APIView, LimitOffsetPagination):
    model = Property
    permission_classes = (IsAuthenticated,)

    def get_context_data(self, **kwargs):
        params = self.request.query_params
        queryset = (
            self.model.objects.filter(org=self.request.profile.org)
            .select_related("address", "owner_contact", "created_by")
            .prefetch_related("tags", "assigned_to", "teams", "images")
        ).order_by("-created_at")

        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to__in=[self.request.profile])
                | Q(created_by=self.request.profile.user)
            )

        if params:
            if params.get("reference"):
                queryset = queryset.filter(
                    reference__icontains=params.get("reference")
                )
            if params.get("title"):
                queryset = queryset.filter(title__icontains=params.get("title"))
            if params.get("search"):
                search = params.get("search")
                queryset = queryset.filter(
                    Q(reference__icontains=search)
                    | Q(title__icontains=search)
                    | Q(description__icontains=search)
                    | Q(address__city__icontains=search)
                )
            if params.get("property_type"):
                queryset = queryset.filter(property_type=params.get("property_type"))
            if params.get("operation"):
                queryset = queryset.filter(operation=params.get("operation"))
            if params.get("status"):
                queryset = queryset.filter(status=params.get("status"))
            if params.get("min_price"):
                queryset = queryset.filter(
                    Q(sale_price__gte=params.get("min_price"))
                    | Q(rent_price__gte=params.get("min_price"))
                )
            if params.get("max_price"):
                queryset = queryset.filter(
                    Q(sale_price__lte=params.get("max_price"))
                    | Q(rent_price__lte=params.get("max_price"))
                )
            if params.get("min_bedrooms"):
                queryset = queryset.filter(
                    bedrooms__gte=params.get("min_bedrooms")
                )
            if params.get("min_bathrooms"):
                queryset = queryset.filter(
                    bathrooms__gte=params.get("min_bathrooms")
                )
            if params.get("min_area"):
                queryset = queryset.filter(
                    built_area__gte=params.get("min_area")
                )
            if params.get("max_area"):
                queryset = queryset.filter(
                    built_area__lte=params.get("max_area")
                )
            if params.get("city"):
                queryset = queryset.filter(
                    address__city__icontains=params.get("city")
                )
            if params.get("zone"):
                queryset = queryset.filter(zone__icontains=params.get("zone"))
            if params.get("energy_rating"):
                queryset = queryset.filter(
                    energy_rating=params.get("energy_rating")
                )
            if params.get("is_featured"):
                queryset = queryset.filter(
                    is_featured=params.get("is_featured").lower() == "true"
                )
            if params.get("is_active"):
                queryset = queryset.filter(
                    is_active=params.get("is_active").lower() == "true"
                )
            if params.getlist("assigned_to"):
                queryset = queryset.filter(
                    assigned_to__id__in=params.getlist("assigned_to")
                )
            if params.get("tags"):
                queryset = queryset.filter(tags__in=params.getlist("tags"))

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter("search", str, description="Search by reference, title, description, city"),
            OpenApiParameter("property_type", str, description="Filter by property type"),
            OpenApiParameter("operation", str, description="Filter by operation (sale/rent)"),
            OpenApiParameter("status", str, description="Filter by status"),
            OpenApiParameter("min_price", float, description="Minimum price"),
            OpenApiParameter("max_price", float, description="Maximum price"),
            OpenApiParameter("min_bedrooms", int, description="Minimum bedrooms"),
            OpenApiParameter("city", str, description="Filter by city"),
        ],
        responses={200: PropertyListSerializer(many=True)},
    )
    def get(self, request):
        queryset = self.get_context_data()
        results = self.paginate_queryset(queryset, request, view=self)
        serializer = PropertyListSerializer(results, many=True)
        return Response(
            {
                "count": queryset.count(),
                "properties": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=PropertyCreateSwaggerSerializer,
        responses={201: PropertyDetailSerializer},
    )
    def post(self, request):
        serializer = PropertyCreateSerializer(
            data=request.data, request_obj=request,
        )
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        property_obj = serializer.save(org=request.profile.org)

        if request.data.get("assigned_to"):
            property_obj.assigned_to.set(
                Profile.objects.filter(
                    id__in=request.data.get("assigned_to"),
                    org=request.profile.org,
                )
            )
        if request.data.get("teams"):
            property_obj.teams.set(
                Teams.objects.filter(
                    id__in=request.data.get("teams"),
                    org=request.profile.org,
                )
            )
        if request.data.get("tags"):
            property_obj.tags.set(
                Tags.objects.filter(id__in=request.data.get("tags"))
            )
        if request.data.get("features"):
            property_obj.features.set(
                PropertyFeature.objects.filter(
                    id__in=request.data.get("features")
                )
            )
        if request.data.get("owner_contact"):
            property_obj.owner_contact = Contact.objects.filter(
                id=request.data.get("owner_contact"),
                org=request.profile.org,
            ).first()
            property_obj.save()

        return Response(
            PropertyDetailSerializer(property_obj).data,
            status=status.HTTP_201_CREATED,
        )


class PropertyDetailView(APIView):
    model = Property
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(
            Property.objects.select_related(
                "address", "owner_contact", "created_by"
            ).prefetch_related(
                "images", "videos", "floor_plans", "documents",
                "features", "assigned_to", "teams", "tags",
            ),
            pk=pk,
            org=self.request.profile.org,
        )

    @extend_schema(responses={200: PropertyDetailSerializer})
    def get(self, request, pk):
        property_obj = self.get_object(pk)
        serializer = PropertyDetailSerializer(property_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PropertyCreateSwaggerSerializer,
        responses={200: PropertyDetailSerializer},
    )
    def put(self, request, pk):
        property_obj = self.get_object(pk)
        serializer = PropertyCreateSerializer(
            instance=property_obj,
            data=request.data,
            request_obj=request,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        property_obj = serializer.save()

        if "assigned_to" in request.data:
            property_obj.assigned_to.set(
                Profile.objects.filter(
                    id__in=request.data.get("assigned_to"),
                    org=request.profile.org,
                )
            )
        if "teams" in request.data:
            property_obj.teams.set(
                Teams.objects.filter(
                    id__in=request.data.get("teams"),
                    org=request.profile.org,
                )
            )
        if "tags" in request.data:
            property_obj.tags.set(
                Tags.objects.filter(id__in=request.data.get("tags"))
            )
        if "features" in request.data:
            property_obj.features.set(
                PropertyFeature.objects.filter(
                    id__in=request.data.get("features")
                )
            )

        return Response(
            PropertyDetailSerializer(property_obj).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        property_obj = self.get_object(pk)
        property_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyImageView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        serializer = PropertyImageSerializer(
            property_obj.images.all(), many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        is_primary = not property_obj.images.exists()
        image_obj = PropertyImage.objects.create(
            property=property_obj,
            image=image_file,
            title=request.data.get("title", ""),
            alt_text=request.data.get("alt_text", ""),
            is_primary=request.data.get("is_primary", is_primary),
            order=property_obj.images.count(),
        )
        return Response(
            PropertyImageSerializer(image_obj).data,
            status=status.HTTP_201_CREATED,
        )


class PropertyImageDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, image_pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        image_obj = get_object_or_404(
            PropertyImage, pk=image_pk, property=property_obj,
        )
        if "order" in request.data:
            image_obj.order = request.data["order"]
        if "is_primary" in request.data:
            if request.data["is_primary"]:
                property_obj.images.update(is_primary=False)
            image_obj.is_primary = request.data["is_primary"]
        if "title" in request.data:
            image_obj.title = request.data["title"]
        if "alt_text" in request.data:
            image_obj.alt_text = request.data["alt_text"]
        image_obj.save()
        return Response(
            PropertyImageSerializer(image_obj).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, image_pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        image_obj = get_object_or_404(
            PropertyImage, pk=image_pk, property=property_obj,
        )
        image_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyVideoView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        serializer = PropertyVideoSerializer(
            property_obj.videos.all(), many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        video_obj = PropertyVideo.objects.create(
            property=property_obj,
            video_url=request.data.get("video_url", ""),
            video_file=request.FILES.get("video_file"),
            title=request.data.get("title", ""),
            is_virtual_tour=request.data.get("is_virtual_tour", False),
            order=property_obj.videos.count(),
        )
        return Response(
            PropertyVideoSerializer(video_obj).data,
            status=status.HTTP_201_CREATED,
        )


class PropertyDocumentView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        serializer = PropertyDocumentSerializer(
            property_obj.documents.all(), many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        doc_file = request.FILES.get("file")
        if not doc_file:
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        doc_obj = PropertyDocument.objects.create(
            property=property_obj,
            file=doc_file,
            title=request.data.get("title", doc_file.name),
            is_private=request.data.get("is_private", True),
        )
        return Response(
            PropertyDocumentSerializer(doc_obj).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk, doc_pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        doc_obj = get_object_or_404(
            PropertyDocument, pk=doc_pk, property=property_obj,
        )
        doc_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        comments = Comment.objects.filter(property=property_obj).order_by(
            "-commented_on"
        )
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=PropertyCommentSwaggerSerializer)
    def post(self, request, pk):
        property_obj = get_object_or_404(
            Property, pk=pk, org=request.profile.org,
        )
        comment_text = request.data.get("comment")
        if not comment_text:
            return Response(
                {"error": "Comment text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        comment = Comment.objects.create(
            comment=comment_text,
            commented_by=request.profile.user,
            property=property_obj,
        )
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )


class PropertyFeatureListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        features = PropertyFeature.objects.filter(
            Q(org=request.profile.org) | Q(org__isnull=True)
        ).select_related("category")
        serializer = PropertyFeatureSerializer(features, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyFeatureCategoryListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        categories = PropertyFeatureCategory.objects.filter(
            Q(org=request.profile.org) | Q(org__isnull=True)
        ).prefetch_related("features")
        serializer = PropertyFeatureCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
