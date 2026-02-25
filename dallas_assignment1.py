import pandas as pd
import geopandas as gpd # pip install geopandas
import matplotlib.pyplot as plt # pip install matplotlib
gdf = gpd.read_file(r"/Users/sayidibekova/Desktop/Assignment 1_Dallas /tl_2020_48113_tabblock20.shp")
gdf.info()
print(gdf.head())
gdf.columns
print(gdf.columns)
gdf.plot()
plt.show()#)#get a plot of seattle-map
#get a visualization of the map 

# Option 1
fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
gdf.plot(
ax=ax,
color="#dbe9f6", # lighter blue
edgecolor="#444444", # dark gray edges (less harsh than black)
linewidth=0.2, # thin but visible block boundaries
alpha=0.85 # slight transparency
)
ax.set_title("Dallas Census Blocks", fontsize=14, pad=12)
ax.set_axis_off()
# Zoom exactly to the city extent
minx, miny, maxx, maxy = gdf.total_bounds
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
plt.tight_layout()
plt.show() #make it transparent, and add teh roads-light blue color 

# Option 2
fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
gdf.boundary.plot(
ax=ax,
color="#2b2b2b",
linewidth=0.25
)
ax.set_title("Dallas Census Block Boundaries")
ax.set_axis_off()
plt.show()#remove the background and leave the lines 

#measuring the area of each block 
gdf.crs #get the Greenwhoch measurements
gdf = gdf.to_crs(2276) #use more accurate values
gdf["area_m2"] = gdf.geometry.area
gdf["area_acres"] = gdf["area_m2"] / 4046.8564224
gdf["area_acres"].describe()

#count    38180.000000 mean       163.891753 std        640.059787
#min          0.268074
#25%         25.345460
#50%         57.771337
#75%        108.443121
#max      33487.453601

#Save it as excel?
gdf_no_geom = gdf.drop(columns="geometry")
gdf_no_geom.to_csv(r"/Users/sayidibekova/Desktop/Assignment 1_Dallas /Assignment 1\test.csv", index=False)
# A CSV cannot store geometry (polygons). Drop geometry or convert geometry to text.


######## Calling the Census data for Total Population
df = pd.read_csv(r"/Users/sayidibekova/Desktop/Assignment 1_Dallas /Dallas Census Pop.csv")
df.info()
df.head()
df = df.drop(index=0).reset_index(drop=True) # drop the first row after title because it contains label info, not data
df.head()
df.mean() # cannot be interpreted

# convert P1_001N to numeric

df.columns.tolist()
gdf.columns
print(df.columns)
print(gdf.columns)


# Convert P1_001N to numeric
df["P1TotalPopulation"] = pd.to_numeric(df["P1TotalPopulation"], errors="coerce")

# Clean GEO_ID and extract 15-digit block GEOID
df["GEOID"] = df["GEOID"].astype(str)
df["BLOCK_GEOID"] = df["GEOID"].str.replace("^.*US", "", regex=True)

# Check cleaned GEOIDs
print(df["BLOCK_GEOID"].str.len().value_counts())

# Confirm shapefile GEOID column
print(gdf["GEOID20"].head())

# Merge (GeoDataFrame MUST be on the left)
gdf_census = gdf.merge(
    df,
    left_on="GEOID20",
    right_on="BLOCK_GEOID",
    how="left",
    indicator=True
)

# Check merge results
print(gdf_census["_merge"].value_counts())


gdf_census['_merge'].value_counts()

gdf_census.info()

# Viz 1
gdf_census.plot(
column='P1TotalPopulation',
cmap='cubehelix',
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#d9d9d9'}
)
plt.title("Population by 2020 Dallas Census Block")
plt.axis('off')
plt.show()

# Viz 2. Quantile classification. This makes low-population areas visible.
gdf_census.plot(
column='P1TotalPopulation',
cmap='viridis',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Population by 2020 Dallas Census Block (Quantiles)")
plt.axis('off')
plt.show()

# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps.
gdf_census.plot(
column='P1TotalPopulation',
cmap='Blues',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Population by 2020 Dallas Census Block (Quantiles)")
plt.axis('off')
plt.show()


# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps. White alone 
gdf_census.plot(
column='P1WhiateAlone',
cmap='Reds',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Population by 2020 Dallas Census Block /White Alone(Quantiles)")
plt.axis('off')
plt.show()



# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps. White alone 
gdf_census.plot(
column='P1WhiateAlone',
cmap='Reds',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("White Population by 2020 Dallas Census Block (Quantile Classification)")
plt.axis('off')
plt.show()

# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps. White alone 
gdf_census.plot(
column='P1BlackAlone',
cmap='Greens',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Black Population by 2020 Dallas Census Block (Quantile Classification)")
plt.axis('off')
plt.show()

# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps. White alone 
gdf_census.plot(
column='P1AsianAlone',
cmap='Reds',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Asian Population by 2020 Dallas Census Block (Quantile Classification)")
plt.axis('off')
plt.show()


# Viz 3. Quantile classification. This makes low-population areas visisble.
# Monochromatic color is helpful for heatmaps. White alone 
gdf_census.plot(
column='Hispanic',
cmap='Blues',
scheme='quantiles',
k=5,
legend=True,
figsize=(10, 10),
missing_kwds={'color': '#e0e0e0'}
)
plt.title("Hispanic Population by 2020 Dallas Census Block (Quantile Classification)")
plt.axis('off')
plt.show()

### Is census block area correlated with total population?
gdf_proj = gdf_census.to_crs(epsg=3857) # meters
gdf_proj['area_m2'] = gdf_proj.geometry.area # compute area
# Remove empty or missing population values
df_corr = gdf_proj[
(gdf_proj['P1TotalPopulation'].notna()) &
(gdf_proj['area_m2'] > 0)
]
# Pearson correlation (linear relationship) pearson_corr = df_corr['area_m2'].corr(df_corr['P1_001N'])
pearson_corr # ~0.06. Weak positive correlation between larger blocks and more people.
# Area alone is usually misleading. Density is more meaningful.
gdf_proj['pop_density'] = gdf_proj['P1_001N'] / gdf_proj['area_m2']
# Remove empty or missing density values
df_corr = gdf_proj[
(gdf_proj['pop_density'].notna()) &
(gdf_proj['area_m2'] > 0)
]
pearson_corr = df_corr['area_m2'].corr(df_corr['pop_density'])
pearson_corr # ~ -0.097 Magnitude is weak.
# A negative correlation suggests as census block area increases,
population density tends to decrease.
# This makes intuitive and geographic cense. Small blocks typically in
urban areas are associated with higher density.
# Large blocks typically in rural area are associated with lower density.


print(gdf.geometry.head())
print(gdf.crs)
print(gdf.total_bounds)