# Imports
#############################################################################################################
import os
import shutil
import sys, string 
import arcpy
import gc
from arcpy import env
from arcpy.sa import *


# Settings
#############################################################################################################
arcpy.CheckOutExtension("Spatial")                                                                      # Check out ArcGIS Spatial Analyst extension license
arcpy.env.addOutputsToMap = False                                                                       # Don't let script add layers to map
arcpy.env.cellSize = 30                                                                                 # Set default raster cell size to 30m
arcpy.env.overwriteOutput = True                                                                        # Allow files to be overwritten
arcpy.env.workspace = "C:\\Users\\2021e\\Desktop\\Research\\montana_wui_mapping\\new\\point_and_raster_data"  # Make sure all input files are in this folder


# Variables
#############################################################################################################
space = "C:\\Users\\2021e\\Desktop\\Research\\montana_wui_mapping\\new\\point_and_raster_data\\"        # Make sure all other input files are in this folder!
NAD_1983_2011_SP_Montana = arcpy.SpatialReference(6514)                              # Spatial reference object for the NAD 1983 (2011) StatePlane Montana FIPS 2500 (Meters) projection
study_years = range(2012, 2025)
projection_factory_code = 6514         # Factory code for the NAD 1983 (2011) StatePlane Montana FIPS 2500 (Meters) projection

print("executed config file")