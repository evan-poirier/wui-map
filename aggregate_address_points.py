# Imports
####################################################################################################
import sys
sys.path.append(r"C:\Users\espoirier\Desktop\Research\Mapping\Montana\scripts\wui-map")
from wui_config import *


# Main
#############################################################################################################
if __name__ == "__main__":
    # .shp file that each year's aggregations will be added to
    county_polygons = r"C:\Users\espoirier\Desktop\Research\Mapping\Montana\county_level_data\County.shp"

    for year in range(2012, 2025):
        print("Tabulating address point count for year " + str(year))

        # object paths
        ap_shp = space + "prepared_input_data\\" + str(year) + "\\ap_f_" + str(year) + ".shp"
        curr_tabulated_areas_table = os.path.join(env.scratchGDB, "tabulated_ap_table_" + str(year))

        # count the number of address points within each county polygon
        arcpy.analysis.SummarizeWithin(
            in_polygons=county_polygons,
            in_sum_features=ap_shp,
            out_feature_class=curr_tabulated_areas_table,
            keep_all_polygons="KEEP_ALL" # Keep all counties, even those with 0 points
        )

        # create renamed fields
        arcpy.management.AddField(curr_tabulated_areas_table, "ap_f_" + str(year), "DOUBLE")
        arcpy.management.CalculateField(
            curr_tabulated_areas_table, "ap_f_" + str(year), "!Point_Count!", "PYTHON3"
        )

        # join aggregations back to main table
        arcpy.management.JoinField(
            in_data=county_polygons,
            in_field="COUNTYNUMB",
            join_table=curr_tabulated_areas_table,
            join_field="COUNTYNUMB",
            fields = ["ap_f_" + str(year)]
        )
        
        print("Finished tabulating " + str(year) + ".")