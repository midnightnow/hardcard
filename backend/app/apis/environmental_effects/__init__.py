
from fastapi import APIRouter
from pydantic import BaseModel
import datetime

router = APIRouter(prefix="/environmental-effects")

class EnvironmentalParamsRequest(BaseModel):
    timestamp: datetime.datetime

class SeasonalParams(BaseModel):
    season: str # e.g., "Winter", "Spring", "Summer", "Autumn"
    dominant_tree_species: str
    undergrowth_density: float # 0.0 to 1.0
    color_palette: list[str] # List of hex color codes

class DiurnalParams(BaseModel):
    time_of_day: str # e.g., "Dawn", "Midday", "Sunset", "Night"
    light_intensity: float # 0.0 to 1.0
    light_color: str # hex color code

class EnvironmentalParamsResponse(BaseModel):
    seasonal: SeasonalParams
    diurnal: DiurnalParams

@router.post("/get-params", response_model=EnvironmentalParamsResponse)
def get_environmental_params(request: EnvironmentalParamsRequest) -> EnvironmentalParamsResponse:
    """
    Calculates and returns environmental parameters (seasonal and diurnal)
    based on the provided timestamp.
    """
    # Determine season
    year = request.timestamp.year
    month = request.timestamp.month
    hour = request.timestamp.hour
    
    if 3 <= month <= 5:
        season_name = "Spring"
        dominant_tree = "Flowering Trees"
        undergrowth = 0.6
        palette = ["#90EE90", "#FFB6C1", "#ADD8E6"] # Spring colors
    elif 6 <= month <= 8:
        season_name = "Summer"
        dominant_tree = "Lush Green Trees"
        undergrowth = 0.9
        palette = ["#3CB371", "#FFD700", "#20B2AA"] # Summer colors
    elif 9 <= month <= 11:
        season_name = "Autumn"
        dominant_tree = "Autumn Foliage Trees"
        undergrowth = 0.5
        palette = ["#FF8C00", "#A52A2A", "#DEB887"] # Autumn colors
    else:  # December, January, February
        season_name = "Winter"
        dominant_tree = "Deciduous" if year % 2 == 0 else "Coniferous"
        undergrowth = 0.2
        palette = ["#FFFFFF", "#E0E0E0", "#B0B0B0"] # Snowy colors

    seasonal_params = SeasonalParams(
        season=season_name,
        dominant_tree_species=dominant_tree,
        undergrowth_density=undergrowth,
        color_palette=palette
    )

    # Determine time of day (simplified)
    if 5 <= hour < 12:
        time_of_day_name = "Morning"
        light_intensity_val = 0.7
        light_color_val = "#FFFACD" # LemonChiffon
    elif 12 <= hour < 17:
        time_of_day_name = "Midday"
        light_intensity_val = 1.0
        light_color_val = "#FFFFFF" # White
    elif 17 <= hour < 20:
        time_of_day_name = "Evening"
        light_intensity_val = 0.5
        light_color_val = "#FFA07A" # LightSalmon
    else: # Night
        time_of_day_name = "Night"
        light_intensity_val = 0.1
        light_color_val = "#191970" # MidnightBlue

    diurnal_params = DiurnalParams(
        time_of_day=time_of_day_name,
        light_intensity=light_intensity_val,
        light_color=light_color_val
    )

    return EnvironmentalParamsResponse(
        seasonal=seasonal_params,
        diurnal=diurnal_params
    )

