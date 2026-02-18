from django.core.management.base import BaseCommand
from django.utils.text import slugify

from properties.models import PropertyFeature, PropertyFeatureCategory


FEATURE_DATA = {
    "General": {
        "order": 1,
        "features": [
            ("Ascensor", "elevator"),
            ("Portero / Conserje", "concierge"),
            ("Trastero", "storage-room"),
            ("Parking incluido", "parking"),
            ("Accesible", "accessible"),
            ("Videovigilancia", "cctv"),
        ],
    },
    "Exterior": {
        "order": 2,
        "features": [
            ("Piscina", "pool"),
            ("Jardín", "garden"),
            ("Terraza", "terrace"),
            ("Balcón", "balcony"),
            ("Patio", "patio"),
            ("Zona comunitaria", "community-area"),
            ("Zona infantil", "playground"),
        ],
    },
    "Interior": {
        "order": 3,
        "features": [
            ("Aire acondicionado", "air-conditioning"),
            ("Calefacción central", "central-heating"),
            ("Suelo radiante", "underfloor-heating"),
            ("Chimenea", "fireplace"),
            ("Armarios empotrados", "built-in-wardrobes"),
            ("Suite con baño", "en-suite"),
            ("Lavadero", "laundry-room"),
            ("Despensa", "pantry"),
        ],
    },
    "Equipamiento": {
        "order": 4,
        "features": [
            ("Cocina equipada", "equipped-kitchen"),
            ("Domótica", "smart-home"),
            ("Alarma", "alarm"),
            ("Puerta blindada", "armored-door"),
            ("Doble acristalamiento", "double-glazing"),
            ("Paneles solares", "solar-panels"),
        ],
    },
}


class Command(BaseCommand):
    help = "Seed default property feature categories and features"

    def handle(self, *args, **options):
        created_cats = 0
        created_feats = 0

        for cat_name, cat_data in FEATURE_DATA.items():
            category, cat_created = PropertyFeatureCategory.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={
                    "name": cat_name,
                    "order": cat_data["order"],
                },
            )
            if cat_created:
                created_cats += 1

            for feat_name, feat_icon in cat_data["features"]:
                _, feat_created = PropertyFeature.objects.get_or_create(
                    slug=slugify(feat_name),
                    defaults={
                        "name": feat_name,
                        "category": category,
                        "icon": feat_icon,
                    },
                )
                if feat_created:
                    created_feats += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_cats} categories and {created_feats} features."
            )
        )
