# About
####################################################################################################

# This script takes raw downloaded polygon and raster files and standardizes them for use in another
# WUI script.


# Imports
####################################################################################################
import sys
sys.path.append(r"C:\Users\2021e\Desktop\Research\montana_wui_mapping\new\scripts") 
from wui_config import *

# Constants
#########################################################################################################
# raw data
raw_address_points = space + "raw_input_data\\address_points_raw\\"
raw_nlcd = space + "raw_input_data\\NLCD_raw\\"
raw_state_boundary = space + "raw_input_data\\state_boundary_raw\\StateofMontana.shp"

# prepared data
prepared_data = space + "prepared_input_data\\"

# best address point fc for east year
best_ap_fcs = {
    2012: "STR_Point",
    2013: "STR_Point",
    2014: "STR_Point",
    2015: "STR_Point",
    2016: "STR_Point",
    2017: "STR_Point",
    2018: "STR_Point",
    2019: "STR_Point",
    2020: "SiteStructureAddressPoints",
    2021: "SiteStructureAddressPoints",
    2022: "SiteStructureAddressPoints",
    2023: "SiteStructureAddressPoint",
    2024: "SiteStructureAddressPoint"
}

# Functions
####################################################################################################
# buffer the input boundary by 100m and save to specified path
def buffer_boundary(input_boundary, buffered_boundary):
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


# project input raster to NAD 1983 (2011) Montana (factory code 6514) and save to specified path
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
    print("Finished projecting " + input_raster_path + " saved to " + output_raster_path)


# reproject a feature class to the global specified factory code and store it in the scratch GDB
def reproject_fc_to_scratch(fc, output_name):
    target_sr = arcpy.SpatialReference(projection_factory_code)

    arcpy.management.Project(
        in_dataset=fc,
        out_dataset=arcpy.env.scratchGDB + "\\" + output_name,
        out_coor_system=projection_factory_code
    )

    print("Reprojected " + fc + " to factory code " + str(projection_factory_code))


# make sure directory for given year exists in prepared data folder
def prepare_curr_year_directory(year):
    os.makedirs(prepared_data + str(year), exist_ok=True)
    print("Prepared data directory for " + str(year) + " exists")


# prepare NLCD rasters and save to prepared data folder
def prepare_nlcds(year):
    # project NLCD raster and save in scratch GDB
    projectNLCDRaster(
        raw_nlcd + "Annual_NLCD_LndCov_" + str(year) + "_CU_C1V1.tif",
        arcpy.env.scratchGDB + "\\" + "temp_nlcd_projected_" + str(year) 
    )

    # clip projected NLCD
    curr_clipped_nlcd = ExtractByMask(
        arcpy.env.scratchGDB + "\\" + "temp_nlcd_projected_" + str(year),
        prepared_data + "constant\\state_buff.shp"
    )

    # save clipped NLCD to respective year folder
    curr_clipped_nlcd.save(
        prepared_data + str(year) + "\\" + "nlcd_" + str(year) + ".tif"
    )
    print("Finished preparing " + str(year) + " nlcd raster")


# prepare address points and save to prepared data folder
def prepare_address_points(year):
    # reproject address point feature classes; store in scratch GDB
    curr_ap_fc = raw_address_points + "Structures" + str(year) + ".gdb\\" + best_ap_fcs[year]
    proj_fc_new_name = "ap_" + str(year)
    reproject_fc_to_scratch(curr_ap_fc, proj_fc_new_name)

    # save address point fcs from scratch GDB to yearly directories
    arcpy.management.CopyFeatures(
        arcpy.env.scratchGDB + "\\ap_" + str(year),
        prepared_data + str(year) + "\\" + "ap_" + str(year) + ".shp"
    )
    print("Finished preparing " + str(year) + " address point shapefile")


# buffer state boundary
def buffer_state_boundary():
    buffer_boundary(
        raw_state_boundary,
        prepared_data + "constant\\state_buff.shp"
    )
    print("Finished buffering state boundary")


# # print contents of scratch GDB
# def print_scratch_gdb():
#     scratch_gdb = arcpy.env.scratchGDB

#     # Walk through the geodatabase
#     for dirpath, dirnames, filenames in arcpy.da.Walk(scratch_gdb, datatype=["FeatureClass", "RasterDataset", "Table", "FeatureDataset"]):
#         # Delete feature classes, rasters, tables
#         for name in filenames:
#             print(name)
        
#         # Delete feature datasets
#         for name in dirnames:
#             print(name)
#     print("Finished printing contents of scratch gdb")


# Main
#############################################################################################################
if __name__ == "__main__":
    print(arcpy.env.workspace)
    # buffer montana state boundary
    # buffer_state_boundary()

    # apply to all years
    for year in study_years:
        # make current year directory in 'prepared_data' directory
        # prepare_curr_year_directory(year)

        # prepare address points (done)
        # prepare_address_points(year)

        # prepare nlcds
        prepare_nlcds(year)
