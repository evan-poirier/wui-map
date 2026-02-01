# Imports
####################################################################################################
import sys
sys.path.append(r"C:\Users\2021e\Desktop\Research\montana_wui_mapping\new\scripts")
from wui_config import *


# Main
#############################################################################################################
if __name__ == "__main__":
    # WUI rasters to compare
    old_raster = space + "point_and_raster_data\\wui_map_output\\2012\\2012.tif"
    new_raster = space + "point_and_raster_data\\wui_map_output\\2024\\2024.tif"

    # Reclassify 2012 Raster:
    old_raster_binary = Con(old_raster == 2, 1, old_raster)

    # Reclassify 2024 Raster:
    new_raster_binary = Con(new_raster == 2, 1, new_raster)

    # Find difference
    difference_raster = new_raster_binary - old_raster_binary

    # Save difference raster
    difference_raster.save(space + "point_and_raster_data\\total_wui_difference_output\\total_diff.tif")

