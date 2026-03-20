import os
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


def generate_handles(labels, colors, edge='k', alpha=1):
    """
    Generate matplotlib patch handles to create a legend of each of the features in the map.

    Parameters
    ----------

    labels : list(str)
        the text labels of the features to add to the legend

    colors : list(matplotlib color)
        the colors used for each of the features included in the map.

    edge : matplotlib color (default: 'k')
        the color to use for the edge of the legend patches.

    alpha : float (default: 1.0)
        the alpha value to use for the legend patches.

    Returns
    -------

    handles : list(matplotlib.patches.Rectangle)
        the list of legend patches to pass to ax.legend()
    """
    lc = len(colors)  # get the length of the color list
    handles = [] # create an empty list
    for ii in range(len(labels)): # for each label and color pair that we're given, make an empty box to pass to our legend
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[ii % lc], edgecolor=edge, alpha=alpha))
    return handles

# adapted this question: https://stackoverflow.com/q/32333870
# answered by SO user Siyh: https://stackoverflow.com/a/35705477
def scale_bar(ax, location=(0.82, 0.95)):
    """
    Create a scale bar in a cartopy GeoAxes.

    Parameters
    ----------

    ax : cartopy.mpl.geoaxes.GeoAxes
        the cartopy GeoAxes to add the scalebar to.

    length : int, float (default 20)
        the length of the scalebar, in km

    location : tuple(float, float) (default (0.92, 0.95))
        the location of the center right corner of the scalebar, in fractions of the axis.

    Returns
    -------
    ax : cartopy.mpl.geoaxes.GeoAxes
        the cartopy GeoAxes object

    Create a scale bar with divisions at 1, 5, and 10 km.
    """
    
    x0, x1, y0, y1 = ax.get_extent()
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    start = sbx
    end = sbx + 10000  # 10 km in metres

    # alternating bar segments: 0-1, 1-5, 5-10 km
    ax.plot([start, start + 1000], [sby, sby], color='k', linewidth=4, transform=ax.projection)
    ax.plot([start + 1000, start + 5000], [sby, sby], color='w', linewidth=4, transform=ax.projection)
    ax.plot([start + 5000, end], [sby, sby], color='k', linewidth=4, transform=ax.projection)

    # outline over the top so the white segment is visible
    ax.plot([start, end], [sby, sby], color='k', linewidth=1, transform=ax.projection)

    # ticks
    for d in [0, 1000, 5000, 10000]:
        x = start + d
        ax.plot([x, x], [sby - 250, sby + 250], color='k', linewidth=1, transform=ax.projection)

    # labels
    ax.text(start, sby - 1200, '0', ha='right', va='top', transform=ax.projection, fontsize=6)
    ax.text(start + 1000, sby - 1200, '1 km', ha='left', va='top', transform=ax.projection, fontsize=6)
    ax.text(start + 5000, sby - 1200, '5 km', ha='center', va='top', transform=ax.projection, fontsize=6)
    ax.text(end, sby - 1200, '10 km', ha='center', va='top', transform=ax.projection, fontsize=6)

    return ax

# load the datasets
outline = gpd.read_file(os.path.abspath('data_files/NI_outline.shp'))
towns = gpd.read_file(os.path.abspath('data_files/Towns.shp'))
water = gpd.read_file(os.path.abspath('data_files/Water.shp'))
rivers = gpd.read_file(os.path.abspath('data_files/Rivers.shp'))
counties = gpd.read_file(os.path.abspath('data_files/Counties.shp'))

ni_utm = ccrs.UTM(29)  # create a Universal Transverse Mercator reference system to transform our data.
# NI is in UTM Zone 29, so we pass 29 to ccrs.UTM()

fig = plt.figure(figsize=(8, 8))  # create a figure of size 8x8 (representing the page size in inches)
ax = plt.axes(projection=ni_utm)  # create an axes object in the figure, using a UTM projection,
# where we can actually plot our data.

# first, we just add the outline of Northern Ireland using cartopy's ShapelyFeature
outline_feature = ShapelyFeature(outline['geometry'], ni_utm, edgecolor='k', facecolor='w')
ax.add_feature(outline_feature) # add the features we've created to the map.

xmin, ymin, xmax, ymax = outline.total_bounds
# using the boundary of the shapefile features, zoom the map to our area of interest
ax.set_extent([xmin-5000, xmax+5000, ymin-5000, ymax+5000], crs=ni_utm)  # because total_bounds
# gives output as xmin, ymin, xmax, ymax,
# but set_extent takes xmin, xmax, ymin, ymax, we re-order the coordinates here.

# pick colors, add features to the map
county_colors = ['#003f5c', '#444e86', '#955196', '#dd5182', '#ff6e54', '#ffa600']

# get a list of unique names for the county boundaries
county_names = list(counties.CountyName.unique())
county_names.sort() # sort the counties alphabetically by name

# next, add the municipal outlines to the map using the colors that we've picked.
# here, we're iterating over the unique values in the 'CountyName' field.
# we're also setting the edge color to be black, with a line width of 0.5 pt. 
# Feel free to experiment with different colors and line widths.
for ii, name in enumerate(county_names):
    feat = ShapelyFeature(counties.loc[counties['CountyName'] == name, 'geometry'], # first argument is the geometry
                          ccrs.CRS(counties.crs), # second argument is the CRS
                          edgecolor='k', # outline the feature in black
                          facecolor=county_colors[ii], # set the face color to the corresponding color from the list
                          linewidth=1, # set the outline width to be 1 pt
                          alpha=0.8) # set the alpha (transparency) to be 0.4 (out of 1)
    ax.add_feature(feat) # once we have created the feature, we have to add it to the map using ax.add_feature()

# here, we're setting the edge color to be the same as the face color. Feel free to change this around,
# and experiment with different line widths.
water_feat = ShapelyFeature(water['geometry'], # first argument is the geometry
                            ccrs.CRS(water.crs), # second argument is the CRS
                            edgecolor='mediumblue', # set the edgecolor to be mediumblue
                            facecolor='mediumblue', # set the facecolor to be mediumblue
                            linewidth=1) # set the outline width to be 1 pt
ax.add_feature(water_feat) # add the collection of features to the map

river_feat = ShapelyFeature(rivers['geometry'], # first argument is the geometry
                            ccrs.CRS(rivers.crs), # second argument is the CRS
                            edgecolor='royalblue', # set the edgecolor to be royalblue
                            linewidth=0.2) # set the linewidth to be 0.2 pt
ax.add_feature(river_feat) # add the collection of features to the map

# split the dataset into Towns and Cities
town_points = towns.loc[towns['STATUS'] == 'Town']
city_points = towns.loc[towns['STATUS'] == 'City']

# ShapelyFeature creates a polygon, so for point data we can just use ax.plot().  Plot Towns as grey squares
town_handle = ax.plot(town_points.geometry.x, town_points.geometry.y, 's', color='0.5', ms=6, transform=ccrs.PlateCarree())

# ShapelyFeature creates a polygon, so for point data we can just use ax.plot().  Plot Cities as black triangles
city_handle = ax.plot(city_points.geometry.x, city_points.geometry.y, '^', color='k', ms=7, transform=ccrs.PlateCarree())

# generate a list of handles for the county datasets
# first, we add the list of names, then the list of colors, and finally we set the transparency
# (since we set it in the map)
county_handles = generate_handles(counties.CountyName.unique(), county_colors, alpha=0.8)

# note: if you change the color you use to display lakes, you'll want to change it here, too
water_handle = generate_handles(['Lakes'], ['mediumblue'])

# note: if you change the color you use to display rivers, you'll want to change it here, too
river_handle = [mlines.Line2D([], [], color='royalblue')]

# update county_names to take it out of uppercase text
nice_names = [name.title() for name in county_names]

# ax.legend() takes a list of handles and a list of labels corresponding to the objects 
# you want to add to the legend
handles = county_handles + water_handle + river_handle + town_handle + city_handle # use '+' to concatenate (combine) lists
labels = nice_names + ['Lakes', 'Rivers', 'Towns', 'Cities']

leg = ax.legend(handles, labels, title='Legend', title_fontsize=12, 
                 fontsize=10, loc='upper left', frameon=True, framealpha=1)

gridlines = ax.gridlines(draw_labels=True, # draw  labels for the grid lines
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5], # add longitude lines at 0.5 deg intervals
                         ylocs=[54, 54.5, 55, 55.5]) # add latitude lines at 0.5 deg intervals
gridlines.right_labels = False # turn off the right-side labels
gridlines.top_labels = False # turn off the top labels

# add the text labels for the towns
for ind, row in towns.iterrows(): # towns.iterrows() returns the index and row
    x, y = row.geometry.x, row.geometry.y # get the x,y location for each town
    ax.text(x, y, row['TOWN_NAME'].title(), fontsize=7, transform=ccrs.PlateCarree()) # use plt.text to place a label at x,y

# add the scale bar to the axis
scale_bar(ax)

# save the figure as map.png, cropped to the axis (bbox_inches='tight'), and a dpi of 300
fig.savefig('map.png', bbox_inches='tight', dpi=300)
