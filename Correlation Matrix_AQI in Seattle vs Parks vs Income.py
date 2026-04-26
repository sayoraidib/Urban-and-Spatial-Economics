
#####
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# -----------------------------
# 1. Load Seattle AQI data
# -----------------------------
aq = pd.read_csv("/Users/sayidibekova/Desktop/AQ Data_Seattle Stockholm/Seattle /Seattle data/ad_viz_plotval_data (1).csv")

# -----------------------------
# 2. Load Seattle tracts
# -----------------------------
seattle = gpd.read_file(r"/Users/sayidibekova/Desktop/AQ Data_Seattle Stockholm/Seattle /Seattle data/2020_Census_Tracts_Seattle_2024002536843921598/tract20_king_county.shp")

# Standardize GEOID column
seattle = seattle.rename(columns={"GEOID20": "GEOID"})
seattle["GEOID"] = seattle["GEOID"].astype(str)

# -----------------------------
# 3. Load income
# -----------------------------
income = pd.read_csv("/Users/sayidibekova/Desktop/AQ Data_Seattle Stockholm/Seattle /Seattle_Income_Clean.csv")
income["GEOID"] = income["GEOID"].astype(str)

# -----------------------------
# 4. Prepare AQI GeoDataFrame
# -----------------------------
aq["Site Latitude"] = pd.to_numeric(aq["Site Latitude"], errors="coerce")
aq["Site Longitude"] = pd.to_numeric(aq["Site Longitude"], errors="coerce")
aq = aq.dropna(subset=["Site Latitude", "Site Longitude"])

aq["geometry"] = [Point(xy) for xy in zip(aq["Site Longitude"], aq["Site Latitude"])]
aq_gdf = gpd.GeoDataFrame(aq, geometry="geometry", crs="EPSG:4326")

# -----------------------------
# 5. Spatial join AQI → tracts
# -----------------------------
seattle = seattle.to_crs("EPSG:4326")

aq_joined = gpd.sjoin(aq_gdf, seattle, how="left", predicate="within")

aq_tract = (
    aq_joined.groupby("GEOID")["Daily AQI Value"]
    .mean()
    .reset_index(name="avg_aqi")
)
# -----------------------------
# LOAD PARKS SHAPEFILE
# -----------------------------
parks = gpd.read_file("/Users/sayidibekova/Desktop/AQ Data_Seattle Stockholm/Seattle /Parks Shapefile/Parks.shp")

# Convert parks to projected CRS for area calculation
parks_area = parks.to_crs("EPSG:3857")

# Compute area in acres
parks_area["area_m2"] = parks_area.geometry.area
parks_area["area_acres"] = parks_area["area_m2"] * 0.000247105

# Convert parks to same CRS as tracts
parks_join = parks_area.to_crs(seattle.crs)

# Spatial join: assign each park polygon to a tract
parks_joined = gpd.sjoin(parks_join, seattle, how="left", predicate="within")

# Aggregate total green space per tract
green_area = (
    parks_joined.groupby("GEOID")["area_acres"]
    .sum()
    .reset_index(name="green_acres")
)

# Merge into Seattle tracts
seattle = seattle.merge(green_area, on="GEOID", how="left")

# Fill tracts with no parks
seattle["green_acres"] = seattle["green_acres"].fillna(0)

# Compute % green space
seattle["green_pct"] = seattle["green_acres"] / seattle["LAND_ACRES"]

# -----------------------------
# 6. Build master dataset
# -----------------------------
master = seattle.copy()

# Merge income
master = master.merge(income[["GEOID", "median income"]], on="GEOID", how="left")

# Merge AQI
master = master.merge(aq_tract, on="GEOID", how="left")

# Keep only needed variables
master = master[[
    "GEOID",
    "median income",
    "green_acres",
    "green_pct",
    "avg_aqi"
]]

master = master[["GEOID", "median income", "green_acres", "green_pct", "avg_aqi"]]

import seaborn as sns
import matplotlib.pyplot as plt

# Select only the variables you want to correlate
corr_vars = ["avg_aqi", "median income", "green_acres", "green_pct"]

corr_df = master[corr_vars]

# Compute correlation matrix
corr_matrix = corr_df.corr()
print(corr_matrix)

# Visualize
plt.figure(figsize=(8,6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
plt.title("Correlation Matrix — Seattle AQI vs Income & Green Space")
plt.show()

