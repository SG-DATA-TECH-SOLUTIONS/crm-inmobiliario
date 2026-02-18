PROPERTY_TYPES = (
    ("flat", "Piso"),
    ("house", "Casa"),
    ("chalet", "Chalet"),
    ("duplex", "Dúplex"),
    ("penthouse", "Ático"),
    ("studio", "Estudio"),
    ("villa", "Villa"),
    ("townhouse", "Adosado"),
    ("country_house", "Casa Rural"),
    ("building", "Edificio"),
    ("land", "Terreno"),
    ("garage", "Garaje"),
    ("storage", "Trastero"),
    ("office", "Oficina"),
    ("commercial", "Local Comercial"),
    ("warehouse", "Nave Industrial"),
)

OPERATION_TYPES = (
    ("sale", "Venta"),
    ("rent", "Alquiler"),
    ("sale_rent", "Venta y Alquiler"),
    ("transfer", "Traspaso"),
)

PROPERTY_STATUS = (
    ("available", "Disponible"),
    ("reserved", "Reservado"),
    ("sold", "Vendido"),
    ("rented", "Alquilado"),
    ("withdrawn", "Retirado"),
)

ENERGY_RATINGS = (
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
    ("E", "E"),
    ("F", "F"),
    ("G", "G"),
    ("exempt", "Exento"),
    ("pending", "En trámite"),
)

ORIENTATION_CHOICES = (
    ("north", "Norte"),
    ("south", "Sur"),
    ("east", "Este"),
    ("west", "Oeste"),
    ("northeast", "Noreste"),
    ("northwest", "Noroeste"),
    ("southeast", "Sureste"),
    ("southwest", "Suroeste"),
)

FURNISHED_CHOICES = (
    ("furnished", "Amueblado"),
    ("partially", "Parcialmente amueblado"),
    ("unfurnished", "Sin amueblar"),
)

CURRENCY_CHOICES = (
    ("EUR", "EUR"),
    ("USD", "USD"),
    ("GBP", "GBP"),
)
