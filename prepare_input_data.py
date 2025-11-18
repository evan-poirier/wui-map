# About
####################################################################################################

# This script takes raw downloaded polygon and raster files and standardizes them for use in another
# WUI script.


# Imports
####################################################################################################
from config import *

# Paths
####################################################################################################

# raw data
raw_data = space + "raw_input_data\\"

# temp
temp = space + "temp\\"

# prepared data
prepared_data = space + "prepared_input_data\\"



# Previously used functions
####################################################################################################
def bufferBoundary(input_boundary, buffered_boundary):
    buffer_distance = "100 meters"
    arcpy.Buffer_analysis(
        in_features=input_boundary,
        out_feature_class=buffered_boundary,
        buffer_distance_or_field=buffer_distance,
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="ALL",
        dissolve_field=""
    )
    print("Boundary buffer completed.")

def projectNLCDRaster(input_raster_path, output_raster_path):
    arcpy.management.ProjectRaster(
        in_raster=input_raster_path,
        out_raster=output_raster_path,
        out_coor_system='PROJCS["NAD_1983_2011_StatePlane_Montana_FIPS_2500",GEOGCS["GCS_NAD_1983_2011",DATUM["D_NAD_1983_2011",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",600000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-109.5],PARAMETER["Standard_Parallel_1",45.0],PARAMETER["Standard_Parallel_2",49.0],PARAMETER["Latitude_Of_Origin",44.25],UNIT["Meter",1.0]]',
        resampling_type="NEAREST",
        cell_size="30 30",
        geographic_transform="WGS_1984_(ITRF08)_To_NAD_1983_2011",
        Registration_Point=None,
        in_coor_system='PROJCS["AEA_WGS84",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],UNIT["Meter",1.0]]',
        vertical="NO_VERTICAL"
    )

def clipNLCD(map_name):
    clipped_NLCD_raster = ExtractByMask(curr_nlcd, study_area)
    clipped_NLCD_raster.save(nlcd_projected_clipped + "nlcd_" + str(map_name) + "_pc.tif")
    print(f"{map_name}: NLCD raster clipping completed.")


# Data preparation functions
####################################################################################################
def clearTempDirectory():
    print("Clearing temp directory.")
    for filename in os.listdir(temp):
        curr_file = os.path.join(temp, filename)
        try:
            if os.path.isfile(curr_file) or os.path.islink(curr_file):
                os.remove(curr_file)
            elif os.path.isdir(curr_file):
                shutil.rmtree(curr_file)
            print(f"Deleted: {curr_file}")
        except Exception as e:
            print(f"Failed to delete {curr_file}: {e}")


# Make sure that NLCD raster, boundary, and house polygons/points are using the desired projection
def checkProjections(map_name, curr_nlcd, curr_address_points, curr_study_area):
    projected_objects = [curr_address_points, curr_study_area, curr_nlcd]
    print(f"{map_name}: checking object projections.")
    for projected_object in projected_objects:
        description = arcpy.Describe(projected_object)
        spatial_ref = description.spatialReference
        if spatial_ref.factoryCode != projection_factory_code:
            print("\t" + description.name + " has factory code of " + str(spatial_ref.factoryCode) + " and needs to be reprojected.")
        else:
            print("\t" + description.name + " does not need to be reprojected.")


# Ensure proper 'value1' field for housing file
def addValue1(map_name, curr_address_points):
    print(f"{map_name}: managing value1 field in housing .shp file.")
    # Check if 'value1' field already exists, add it if not
    fields = [field.name for field in arcpy.ListFields(curr_address_points)]
    if "value1" not in fields:
        arcpy.AddField_management(curr_address_points, "value1", "SHORT")
        print("\tHousing shapefile did not have value1 field, it has been added.")
    else:
        print("\tHousing shapefile already had value1 field.")

    # Set value1 = 1 for all rows
    with arcpy.da.UpdateCursor(curr_address_points, ["value1"]) as cursor:
        for row in cursor:
            row[0] = 1
            cursor.updateRow(row)
    print("\tSet value1 = 1 for all rows in housing shapefile.")


# Main
#############################################################################################################
if __name__ == "__main__":



    projectNLCDRaster(nlcd_path, nlcd_output_path)
    bufferBoundary(study_area, buffered_study_area)
    

    # main process
    for year in study_years:
        print("placeholder")
