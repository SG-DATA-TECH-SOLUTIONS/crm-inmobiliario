from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from accounts.models import Tags
from common.base import BaseModel
from common.models import Address, Org, Profile
from contacts.models import Contact
from teams.models import Teams

from .constants import (
    CURRENCY_CHOICES,
    ENERGY_RATINGS,
    FURNISHED_CHOICES,
    OPERATION_TYPES,
    ORIENTATION_CHOICES,
    PROPERTY_STATUS,
    PROPERTY_TYPES,
)


class PropertyFeatureCategory(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0)
    org = models.ForeignKey(
        Org, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="feature_categories",
    )

    class Meta:
        db_table = "property_feature_category"
        ordering = ("order",)
        verbose_name = "Feature Category"
        verbose_name_plural = "Feature Categories"

    def __str__(self):
        return self.name


class PropertyFeature(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        PropertyFeatureCategory,
        related_name="features",
        on_delete=models.CASCADE,
    )
    icon = models.CharField(max_length=50, blank=True, default="")
    org = models.ForeignKey(
        Org, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="property_features",
    )

    class Meta:
        db_table = "property_feature"
        ordering = ("category__order", "name")
        verbose_name = "Property Feature"
        verbose_name_plural = "Property Features"

    def __str__(self):
        return self.name


class Property(BaseModel):
    # -- Identification --
    reference = models.CharField(
        _("Reference"), max_length=50, unique=True, db_index=True,
    )
    title = models.CharField(_("Title"), max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)

    # -- Classification --
    property_type = models.CharField(
        max_length=30, choices=PROPERTY_TYPES, db_index=True,
    )
    operation = models.CharField(
        max_length=20, choices=OPERATION_TYPES, db_index=True,
    )
    status = models.CharField(
        max_length=20, choices=PROPERTY_STATUS, default="available", db_index=True,
    )

    # -- Pricing --
    sale_price = models.DecimalField(
        _("Sale Price"), max_digits=12, decimal_places=2, null=True, blank=True,
    )
    rent_price = models.DecimalField(
        _("Rent Price/month"), max_digits=10, decimal_places=2, null=True, blank=True,
    )
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default="EUR",
    )
    community_fees = models.DecimalField(
        _("Community Fees"), max_digits=8, decimal_places=2, null=True, blank=True,
    )
    ibi_tax = models.DecimalField(
        _("IBI Annual Tax"), max_digits=8, decimal_places=2, null=True, blank=True,
    )

    # -- Location --
    address = models.ForeignKey(
        Address, related_name="properties",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    zone = models.CharField(
        _("Zone/Neighborhood"), max_length=255, blank=True, default="",
    )

    # -- Dimensions --
    built_area = models.DecimalField(
        _("Built Area m²"), max_digits=10, decimal_places=2, null=True, blank=True,
    )
    usable_area = models.DecimalField(
        _("Usable Area m²"), max_digits=10, decimal_places=2, null=True, blank=True,
    )
    plot_area = models.DecimalField(
        _("Plot Area m²"), max_digits=10, decimal_places=2, null=True, blank=True,
    )
    terrace_area = models.DecimalField(
        _("Terrace Area m²"), max_digits=10, decimal_places=2, null=True, blank=True,
    )

    # -- Rooms --
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    floors = models.PositiveIntegerField(_("Number of floors"), default=1)
    floor_number = models.CharField(
        _("Floor"), max_length=10, blank=True, default="",
    )

    # -- Construction --
    year_built = models.PositiveIntegerField(null=True, blank=True)
    year_renovated = models.PositiveIntegerField(null=True, blank=True)
    orientation = models.CharField(
        max_length=20, choices=ORIENTATION_CHOICES, blank=True, default="",
    )
    furnished = models.CharField(
        max_length=20, choices=FURNISHED_CHOICES, blank=True, default="",
    )

    # -- Energy certificate --
    energy_rating = models.CharField(
        max_length=10, choices=ENERGY_RATINGS, blank=True, default="",
    )
    energy_consumption = models.DecimalField(
        _("kWh/m²/year"), max_digits=8, decimal_places=2, null=True, blank=True,
    )
    co2_emissions = models.DecimalField(
        _("CO₂ kg/m²/year"), max_digits=8, decimal_places=2, null=True, blank=True,
    )

    # -- Descriptions --
    description = models.TextField(blank=True, default="")
    internal_notes = models.TextField(
        _("Internal Notes (not public)"), blank=True, default="",
    )

    # -- Features --
    features = models.ManyToManyField(
        PropertyFeature, related_name="properties", blank=True,
    )

    # -- CRM Relations --
    owner_contact = models.ForeignKey(
        Contact, related_name="owned_properties",
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    assigned_to = models.ManyToManyField(
        Profile, related_name="property_assigned_users", blank=True,
    )
    teams = models.ManyToManyField(
        Teams, related_name="property_teams", blank=True,
    )
    tags = models.ManyToManyField(
        Tags, related_name="property_tags", blank=True,
    )
    org = models.ForeignKey(
        Org, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="property_org",
    )

    # -- Visibility --
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_published_web = models.BooleanField(
        _("Published on website"), default=False,
    )

    # -- Portal sync flags --
    publish_idealista = models.BooleanField(default=False)
    publish_fotocasa = models.BooleanField(default=False)
    publish_habitaclia = models.BooleanField(default=False)

    # -- Dates --
    available_from = models.DateField(null=True, blank=True)
    sold_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        db_table = "property"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["property_type", "operation", "status"]),
            models.Index(fields=["sale_price"]),
            models.Index(fields=["rent_price"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.reference}-{self.title}")
            self.slug = base_slug[:280]
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first()

    @property
    def image_count(self):
        return self.images.count()

    @property
    def get_team_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        return Profile.objects.filter(id__in=team_user_ids)

    @property
    def get_team_and_assigned_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        assigned_user_ids = list(self.assigned_to.values_list("id", flat=True))
        user_ids = team_user_ids + assigned_user_ids
        return Profile.objects.filter(id__in=user_ids)


class PropertyImage(BaseModel):
    property = models.ForeignKey(
        Property, related_name="images", on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="properties/images/%Y/%m/")
    thumbnail = models.ImageField(
        upload_to="properties/thumbnails/%Y/%m/", blank=True,
    )
    title = models.CharField(max_length=255, blank=True, default="")
    alt_text = models.CharField(max_length=255, blank=True, default="")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "property_image"
        ordering = ("order", "-created_at")
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"

    def __str__(self):
        return f"Image {self.order} for {self.property.reference}"


class PropertyVideo(BaseModel):
    property = models.ForeignKey(
        Property, related_name="videos", on_delete=models.CASCADE,
    )
    video_url = models.URLField(blank=True, default="")
    video_file = models.FileField(
        upload_to="properties/videos/%Y/%m/", blank=True,
    )
    title = models.CharField(max_length=255, blank=True, default="")
    is_virtual_tour = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "property_video"
        ordering = ("order",)
        verbose_name = "Property Video"
        verbose_name_plural = "Property Videos"

    def __str__(self):
        return f"Video for {self.property.reference}"


class PropertyFloorPlan(BaseModel):
    property = models.ForeignKey(
        Property, related_name="floor_plans", on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to="properties/floorplans/%Y/%m/")
    title = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "property_floor_plan"
        ordering = ("order",)
        verbose_name = "Property Floor Plan"
        verbose_name_plural = "Property Floor Plans"

    def __str__(self):
        return f"Floor plan for {self.property.reference}"


class PropertyDocument(BaseModel):
    property = models.ForeignKey(
        Property, related_name="documents", on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to="properties/docs/%Y/%m/")
    title = models.CharField(max_length=255)
    is_private = models.BooleanField(default=True)

    class Meta:
        db_table = "property_document"
        ordering = ("-created_at",)
        verbose_name = "Property Document"
        verbose_name_plural = "Property Documents"

    def __str__(self):
        return f"{self.title} - {self.property.reference}"
