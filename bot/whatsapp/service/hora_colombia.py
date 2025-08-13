from datetime import datetime
import pytz

zona_colombia = pytz.timezone("America/Bogota")

def ahora_colombia():
    return datetime.now(zona_colombia)

