
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
