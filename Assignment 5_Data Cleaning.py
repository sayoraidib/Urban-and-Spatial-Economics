
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import statsmodels.formula.api as smf

# ---------------------------------------------------------
# 1. LOAD BUSINESS DATA + CREATE GEOMETRY
# ---------------------------------------------------------
biz = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Chicago_cleaned_business_data.csv")

# Create point geometry
biz["geometry"] = biz.apply(lambda r: Point(r["LONGITUDE"], r["LATITUDE"]), axis=1)
points = gpd.GeoDataFrame(biz, geometry="geometry", crs="EPSG:4326")

# ---------------------------------------------------------
# 2. LOAD TRACTS SHAPEFILE
# ---------------------------------------------------------
tracts = gpd.read_file("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Census_20Tracts/Census_Tracts.shp")
tracts = tracts.to_crs("EPSG:4326")

# Keep only GEOID + geometry
tracts = tracts[["CENSUS_T_1", "geometry"]]
tracts["CENSUS_T_1"] = tracts["CENSUS_T_1"].astype(str).str.zfill(11)

# ---------------------------------------------------------
# 3. SPATIAL JOIN: ASSIGN BUSINESSES TO TRACTS
# ---------------------------------------------------------
joined = gpd.sjoin(points, tracts, how="left", predicate="within")

# Count businesses per tract
business_counts = (
    joined.groupby("CENSUS_T_1")
    .size()
    .reset_index(name="business_count")
)

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. LOAD BUSINESS DATA + QUICK INSPECTION
# ---------------------------------------------------------
biz = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Chicago_cleaned_business_data.csv")

print("Columns in biz:")
print(biz.columns)

print("\nSample rows:")
print(biz.head())

# Look at a few likely columns for business type
possible_cols = ["BUSINESS_TYPE", "LICENSE_DESCRIPTION", "BUSINESS_ACTIVITY", "BUSINESS_CATEGORY"]
for c in possible_cols:
    if c in biz.columns:
        print(f"\nValue counts for {c}:")
        print(biz[c].value_counts().head(20))


import matplotlib.pyplot as plt

# ---------------------------------------------------------
# HISTOGRAM / BAR CHART OF BUSINESS ACTIVITY
# ---------------------------------------------------------

# Use the correct column
business_col = "BUSINESS ACTIVITY"

# Count categories
activity_counts = (
    biz[business_col]
    .dropna()
    .value_counts()
)

# Choose how many categories to show
top_n = 20
activity_top = activity_counts.head(top_n)

plt.figure(figsize=(12, 8), dpi=150)

activity_top.sort_values().plot(
    kind="barh",
    color="steelblue"
)

plt.title(f"Top {top_n} Business Activities in Chicago", fontsize=15)
plt.xlabel("Number of Businesses", fontsize=13)
plt.ylabel("Business Activity", fontsize=13)
plt.tight_layout()
plt.show()

# Identify top 5 business activities
top5 = (
    biz["BUSINESS ACTIVITY"]
    .dropna()
    .value_counts()
    .head(5)
)

print("Top 5 business types:")
print(top5)

import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Identify top 5 business types
# ---------------------------------------------------------
top5 = (
    biz["BUSINESS ACTIVITY"]
    .dropna()
    .value_counts()
    .head(5)
)

top5_list = list(top5.index)
print("Top 5 business types:", top5_list)

# ---------------------------------------------------------
# 2. Define symbols + colors for each type
# ---------------------------------------------------------
markers = ["o", "^", "s", "P", "X"]   # circle, triangle, square, plus, X
colors = ["red", "blue", "green", "purple", "orange"]

# ---------------------------------------------------------
# 3. Plot everything on one map
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# Plot Chicago tracts
tracts.plot(
    ax=ax,
    color="lightgrey",
    edgecolor="white",
    linewidth=0.3
)

# Plot each business type with a unique symbol + color
for i, activity in enumerate(top5_list):
    subset = joined[joined["BUSINESS ACTIVITY"] == activity]

    subset.plot(
        ax=ax,
        markersize=25,
        marker=markers[i],
        color=colors[i],
        alpha=0.7,
        label=activity
    )

plt.title("Top 5 Business Types in Chicago", fontsize=16)
plt.legend(title="Business Activity", fontsize=10)
plt.axis("off")
plt.show()



# ---------------------------------------------------------
# 4. LOAD POPULATION, INCOME, POVERTY DATA
# ---------------------------------------------------------
pop = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Popullation Census Tract .csv")
pop = pop[pop["GEO_ID"] != "Geography"]
pop["TRACT_GEOID"] = pop["GEO_ID"].str[-11:].str.zfill(11)
pop["population"] = pd.to_numeric(pop["P1_001N"], errors="coerce")

income = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Household income data.csv")
income = income[income["GEO_ID"] != "Geography"]
income["TRACT_GEOID"] = income["GEO_ID"].str[-11:].str.zfill(11)
income["median_income"] = pd.to_numeric(income["S1901_C01_012E"], errors="coerce")

poverty = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/poverty status.csv")
poverty = poverty[poverty["GEO_ID"] != "Geography"]
poverty["TRACT_GEOID"] = poverty["GEO_ID"].str[-11:].str.zfill(11)
poverty["poverty_rate"] = pd.to_numeric(poverty["S1701_C02_001E"], errors="coerce")

# ---------------------------------------------------------
# 5. MERGE EVERYTHING INTO ONE TRACT-LEVEL DF
# ---------------------------------------------------------
df = tracts.merge(business_counts, on="CENSUS_T_1", how="left")
df["business_count"] = df["business_count"].fillna(0)

df = df.merge(pop[["TRACT_GEOID", "population"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.merge(income[["TRACT_GEOID", "median_income"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.merge(poverty[["TRACT_GEOID", "poverty_rate"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.fillna(0)

# ---------------------------------------------------------
# 6. COMPUTE BUSINESS DENSITY
# ---------------------------------------------------------
df["business_density"] = df["business_count"] / df["population"].replace(0, np.nan)

#Distance from CBD 
from shapely.geometry import Point
import geopandas as gpd

cbd = Point(-87.632, 41.883)  # Chicago CBD

df = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
df["centroid"] = df.geometry.centroid
df = df.to_crs(epsg=3857)  # meters

cbd_gdf = gpd.GeoDataFrame(geometry=[cbd], crs="EPSG:4326").to_crs(epsg=3857)

df["dist_to_cbd_km"] = df.centroid.distance(cbd_gdf.geometry.iloc[0]) / 1000

#Adding crime rate




# ---------------------------------------------------------
# 7. REGRESSION
# ---------------------------------------------------------
df_reg = df[["business_density", "median_income", "poverty_rate", "population"]].replace({0: np.nan}).dropna()

model = smf.ols("business_density ~ median_income + poverty_rate + population", data=df_reg).fit()
print(model.summary())

###Logg-log model 
import numpy as np
import statsmodels.formula.api as smf

# Create log variables
df_reg = df.copy()

df_reg["log_bd"] = np.log(df_reg["business_density"].replace(0, np.nan))
df_reg["log_inc"] = np.log(df_reg["median_income"].replace(0, np.nan))
df_reg["log_pov"] = np.log(df_reg["poverty_rate"] + 1)  # +1 to avoid log(0)
df_reg["log_pop"] = np.log(df_reg["population"].replace(0, np.nan))

# Drop missing values
df_reg = df_reg[["log_bd", "log_inc", "log_pov", "log_pop"]].dropna()

# Log–log regression
loglog_model = smf.ols(
    "log_bd ~ log_inc + log_pov + log_pop",
    data=df_reg
).fit()

print(loglog_model.summary())

pd.set_option("display.max_columns", None)
df.head()
df_clean = df.drop(columns=["TRACT_GEOID_x", "TRACT_GEOID_y", "TRACT_GEOID"])
df_clean.head()

import statsmodels.api as sm
import statsmodels.formula.api as smf

# Use df_reg but with counts + predictors
df_pois = df.copy()
df_pois = df_pois[["business_count", "median_income", "poverty_rate", "population"]].replace({0: np.nan}).dropna()

# Poisson regression with population as exposure
poisson_model = smf.glm(
    formula="business_count ~ median_income + poverty_rate + population",
    data=df_pois,
    family=sm.families.Poisson(),
    exposure=df_pois["population"]
).fit()

print(poisson_model.summary())

#Only one variable income: 
m1 = smf.ols("business_density ~ median_income", data=df).fit()
print(m1.summary())

#add 



############
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm

# ---------------------------------------------------------
# 1. LOAD BUSINESS DATA + CREATE GEOMETRY
# ---------------------------------------------------------
biz = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Chicago_cleaned_business_data.csv")

biz["geometry"] = biz.apply(lambda r: Point(r["LONGITUDE"], r["LATITUDE"]), axis=1)
points = gpd.GeoDataFrame(biz, geometry="geometry", crs="EPSG:4326")

# ---------------------------------------------------------
# 2. LOAD TRACTS SHAPEFILE
# ---------------------------------------------------------
tracts = gpd.read_file("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Census_20Tracts/Census_Tracts.shp")
tracts = tracts.to_crs("EPSG:4326")

tracts = tracts[["CENSUS_T_1", "geometry"]]
tracts["CENSUS_T_1"] = tracts["CENSUS_T_1"].astype(str).str.zfill(11)

# ---------------------------------------------------------
# 3. SPATIAL JOIN: ASSIGN BUSINESSES TO TRACTS
# ---------------------------------------------------------
joined = gpd.sjoin(points, tracts, how="left", predicate="within")

business_counts = (
    joined.groupby("CENSUS_T_1")
    .size()
    .reset_index(name="business_count")
)

# ---------------------------------------------------------
# 4. LOAD POPULATION, INCOME, POVERTY DATA
# ---------------------------------------------------------
pop = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Popullation Census Tract .csv")
pop = pop[pop["GEO_ID"] != "Geography"]
pop["TRACT_GEOID"] = pop["GEO_ID"].str[-11:].str.zfill(11)
pop["population"] = pd.to_numeric(pop["P1_001N"], errors="coerce")

income = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/Household income data.csv")
income = income[income["GEO_ID"] != "Geography"]
income["TRACT_GEOID"] = income["GEO_ID"].str[-11:].str.zfill(11)
income["median_income"] = pd.to_numeric(income["S1901_C01_012E"], errors="coerce")

poverty = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/Vhicago final data/poverty status.csv")
poverty = poverty[poverty["GEO_ID"] != "Geography"]
poverty["TRACT_GEOID"] = poverty["GEO_ID"].str[-11:].str.zfill(11)
poverty["poverty_rate"] = pd.to_numeric(poverty["S1701_C02_001E"], errors="coerce")

# ---------------------------------------------------------
# 5. MERGE EVERYTHING INTO ONE TRACT-LEVEL DF
# ---------------------------------------------------------
df = tracts.merge(business_counts, on="CENSUS_T_1", how="left")
df["business_count"] = df["business_count"].fillna(0)

df = df.merge(pop[["TRACT_GEOID", "population"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.merge(income[["TRACT_GEOID", "median_income"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.merge(poverty[["TRACT_GEOID", "poverty_rate"]],
              left_on="CENSUS_T_1", right_on="TRACT_GEOID", how="left")

df = df.fillna(0)

# ---------------------------------------------------------
# 6. RESTORE GEOMETRY (IMPORTANT)
# ---------------------------------------------------------
df["geometry"] = tracts.set_index("CENSUS_T_1").loc[df["CENSUS_T_1"], "geometry"].values
df = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# ---------------------------------------------------------
# 7. COMPUTE BUSINESS DENSITY
# ---------------------------------------------------------
df["business_density"] = df["business_count"] / df["population"].replace(0, np.nan)

# ---------------------------------------------------------
# 8. COMPUTE POPULATION DENSITY
# ---------------------------------------------------------
df = df.to_crs(epsg=3857)
df["area_sqm"] = df.geometry.area
df["area_sqkm"] = df["area_sqm"] / 1_000_000
df["population_density"] = df["population"] / df["area_sqkm"]

# ---------------------------------------------------------
# 9. DISTANCE TO CBD
# ---------------------------------------------------------
cbd = Point(-87.632, 41.883)
cbd_gdf = gpd.GeoDataFrame(geometry=[cbd], crs="EPSG:4326").to_crs(epsg=3857)

df["centroid"] = df.geometry.centroid
df["dist_to_cbd_km"] = df.centroid.distance(cbd_gdf.geometry.iloc[0]) / 1000


# ---------------------------------------------------------
# 10. LOAD CRIME DATA (2024–2026) AND SPATIAL JOIN
# ---------------------------------------------------------
crime = pd.read_csv("/Users/sayidibekova/Desktop/Individual Project_Urban/crimes_2024_2026.csv")

# Use correct column names: Latitude + Longitude
crime_gdf = gpd.GeoDataFrame(
    crime,
    geometry=gpd.points_from_xy(crime["Longitude"], crime["Latitude"]),
    crs="EPSG:4326"
)

# Reproject to match df
crime_gdf = crime_gdf.to_crs(epsg=3857)

# Spatial join: assign each crime to a tract
crime_joined = gpd.sjoin(crime_gdf, df, how="inner", predicate="within")

# Count crimes per tract
crime_counts = (
    crime_joined.groupby("CENSUS_T_1")
    .size()
    .reset_index(name="crime_count")
)

# Merge into main df
df = df.merge(crime_counts, on="CENSUS_T_1", how="left")
df["crime_count"] = df["crime_count"].fillna(0)

# Crime rate
df["crime_rate"] = df["crime_count"] / df["population"].replace(0, np.nan)

# ---------------------------------------------------------
# 11. OLS REGRESSION WITH CRIME + DISTANCE
# ---------------------------------------------------------
df_reg = df[[
    "business_density", "median_income", "poverty_rate",
    "population", "crime_rate", "dist_to_cbd_km"
]].replace({0: np.nan}).dropna()

model = smf.ols(
    "business_density ~ median_income + poverty_rate + population + crime_rate + dist_to_cbd_km",
    data=df_reg
).fit()

print("\n=== OLS WITH CRIME + DISTANCE ===")
print(model.summary())

# ---------------------------------------------------------
# 12. LOG–LOG MODEL
# ---------------------------------------------------------
df_log = df.copy()

df_log["log_bd"] = np.log(df_log["business_density"].replace(0, np.nan))
df_log["log_inc"] = np.log(df_log["median_income"].replace(0, np.nan))
df_log["log_pov"] = np.log(df_log["poverty_rate"] + 1)
df_log["log_pop"] = np.log(df_log["population"].replace(0, np.nan))
df_log["log_crime"] = np.log(df_log["crime_rate"] + 1)
df_log["log_dist"] = np.log(df_log["dist_to_cbd_km"].replace(0, np.nan))

df_log = df_log[["log_bd", "log_inc", "log_pov", "log_pop", "log_crime", "log_dist"]].dropna()

loglog_model = smf.ols(
    "log_bd ~ log_inc + log_pov + log_pop + log_crime + log_dist",
    data=df_log
).fit()

print("\n=== LOG–LOG MODEL WITH CRIME + DISTANCE ===")
print(loglog_model.summary())

# ---------------------------------------------------------
# 13. POISSON MODEL WITH CRIME + DISTANCE
# ---------------------------------------------------------
df_pois = df[[
    "business_count", "median_income", "poverty_rate",
    "population", "crime_rate", "dist_to_cbd_km"
]].replace({0: np.nan}).dropna()

poisson_model = smf.glm(
    formula="business_count ~ median_income + poverty_rate + crime_rate + dist_to_cbd_km",
    data=df_pois,
    family=sm.families.Poisson(),
    exposure=df_pois["population"]
).fit()

print("\n=== POISSON MODEL WITH CRIME + DISTANCE ===")
print(poisson_model.summary())

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df_clean = df[[
    "CENSUS_T_1",
    "geometry",
    "business_count",
    "population",
    "median_income",
    "poverty_rate",
    "business_density",
    "population_density",
    "dist_to_cbd_km",
    "crime_rate"
]]

df_clean.head(3)

#Models
m1 = smf.ols(
    "business_density ~ median_income + poverty_rate + population",
    data=df
).fit()
print(m1.summary())

#Adding CBD 
m2 = smf.ols(
    "business_density ~ median_income + poverty_rate + population + dist_to_cbd_km+crime_count",
    data=df
).fit()
print(m2.summary())

#Log-log model 
df_log = df.copy()

df_log["log_bd"] = np.log(df_log["business_density"].replace(0, np.nan))
df_log["log_inc"] = np.log(df_log["median_income"].replace(0, np.nan))
df_log["log_crime"] = np.log(df_log["crime_rate"] + 1)
df_log["log_popdens"] = np.log(df_log["population_density"].replace(0, np.nan))

df_log = df_log[[
    "log_bd", "log_inc", "log_crime", "log_popdens", "dist_to_cbd_km"
]].dropna()

loglog_model = smf.ols(
    "log_bd ~ log_inc + log_crime + log_popdens + dist_to_cbd_km",
    data=df_log
).fit()

print(loglog_model.summary())


#Elasticity Log Log mode