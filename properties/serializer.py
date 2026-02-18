from rest_framework import serializers

from common.serializer import (
    AttachmentsSerializer,
    ProfileSerializer,
    UserSerializer,
)
from contacts.serializer import ContactSerializer
from teams.serializer import TeamsSerializer

from .models import (
    Property,
    PropertyDocument,
    PropertyFeature,
    PropertyFeatureCategory,
    PropertyFloorPlan,
    PropertyImage,
    PropertyVideo,
)


class PropertyFeatureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeatureCategory
        fields = ("id", "name", "slug", "order")


class PropertyFeatureSerializer(serializers.ModelSerializer):
    category = PropertyFeatureCategorySerializer(read_only=True)

    class Meta:
        model = PropertyFeature
        fields = ("id", "name", "slug", "category", "icon")


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = (
            "id", "image", "thumbnail", "title",
            "alt_text", "is_primary", "order",
        )


class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = (
            "id", "video_url", "video_file", "title",
            "is_virtual_tour", "order",
        )


class PropertyFloorPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFloorPlan
        fields = ("id", "file", "title", "order")


class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDocument
        fields = ("id", "file", "title", "is_private", "created_at")


class TagsSerializerShort(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.SlugField()


class PropertyListSerializer(serializers.ModelSerializer):
    primary_image = PropertyImageSerializer(read_only=True)
    image_count = serializers.IntegerField(read_only=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    tags = TagsSerializerShort(read_only=True, many=True)
    address_display = serializers.SerializerMethodField()
    created_by = UserSerializer(read_only=True)

    def get_address_display(self, obj):
        if obj.address:
            return obj.address.get_complete_address()
        return ""

    class Meta:
        model = Property
        fields = (
            "id",
            "reference",
            "title",
            "slug",
            "property_type",
            "operation",
            "status",
            "sale_price",
            "rent_price",
            "currency",
            "built_area",
            "bedrooms",
            "bathrooms",
            "primary_image",
            "image_count",
            "address_display",
            "is_featured",
            "is_active",
            "is_published_web",
            "assigned_to",
            "tags",
            "created_by",
            "created_at",
        )


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    videos = PropertyVideoSerializer(many=True, read_only=True)
    floor_plans = PropertyFloorPlanSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    features = PropertyFeatureSerializer(many=True, read_only=True)
    owner_contact = ContactSerializer(read_only=True)
    assigned_to = ProfileSerializer(many=True, read_only=True)
    teams = TeamsSerializer(many=True, read_only=True)
    tags = TagsSerializerShort(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    address_display = serializers.SerializerMethodField()

    def get_address_display(self, obj):
        if obj.address:
            return obj.address.get_complete_address()
        return ""

    class Meta:
        model = Property
        fields = "__all__"


class PropertyCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        if request_obj and hasattr(request_obj, "profile") and request_obj.profile:
            self.org = request_obj.profile.org
        else:
            self.org = None

    def validate_reference(self, value):
        qs = Property.objects.filter(reference=value, org=self.org)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError(
                "A property with this reference already exists."
            )
        return value

    class Meta:
        model = Property
        exclude = ("slug", "org", "created_by", "updated_by")


class PropertyCreateSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "reference", "title", "property_type", "operation", "status",
            "sale_price", "rent_price", "currency", "bedrooms", "bathrooms",
            "built_area", "description", "assigned_to", "teams", "tags",
            "features", "owner_contact",
        ]


class PropertyCommentSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    property_attachment = serializers.FileField(required=False)
