# Imports
####################################################################################################
import sys
sys.path.append(r"C:\Users\2021e\Desktop\Research\montana_wui_mapping\new\scripts")
from wui_config import *


# Main
#############################################################################################################
if __name__ == "__main__":
    # .shp file that each year's aggregations will be added to
    county_polygons = space + "county_level_data\\County.shp"

    for year in range(2012, 2025):
        print("Tabulating wildland for year " + str(year))

        # object paths
        wildland_raster = space + "point_and_raster_data\\wui_intermediary\\" + str(year) + "\\wildveg.tif"
        curr_tabulated_areas_table = os.path.join(env.scratchGDB, "tabulated_wildland_table_" + str(year))

        # snap raster
        arcpy.env.snapRaster = wildland_raster

        # aggregate intermix and interface WUI by county
        TabulateArea(
            in_zone_data = county_polygons,
            zone_field = "COUNTYNUMB",
            in_class_data = wildland_raster,
            class_field = "Value",
            out_table = curr_tabulated_areas_table,
            processing_cell_size = arcpy.env.cellSize
        )

        # create renamed fields
        arcpy.management.AddField(curr_tabulated_areas_table, "wild_" + str(year), "DOUBLE")
        arcpy.management.CalculateField(
            curr_tabulated_areas_table, "wild_" + str(year), "!VALUE_1!", "PYTHON3"
        )

        # join aggregations back to main table
        arcpy.management.JoinField(
            in_data=county_polygons,
            in_field="COUNTYNUMB",
            join_table=curr_tabulated_areas_table,
            join_field="COUNTYNUMB",
            fields = ["wild_" + str(year)]
        )
        
        print("Finished tabulating " + str(year) + ".")