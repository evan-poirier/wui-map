# About
#############################################################################################################

# Script adapted from original code by Dr. Dapeng Li in the Department of Geography and the Environment at the University of Alabama.
# This script generates WUI maps using the moving window method introduced by Bar-Massada, et. al.
# Inputs: NLCD raster data, building polygon or point data, and a boundary polygon.
# See 'settings' and 'paths' sections before running program.

# Imports
####################################################################################################
import sys
sys.path.append(r"C:\Users\2021e\Desktop\Research\montana_wui_mapping\new\scripts")
from wui_config import *

# Paths
####################################################################################################
# main folders
all_outputs = space + "wui_map_output\\" 
intermediary = space + "wui_intermediary\\"
prepared = space + "prepared_input_data\\"

# yearly folders
temp = intermediary + "2012\\"
output = all_outputs + "2012\\"

# ketchpaw test
kp_test_prepared = prepared + "ketchpaw_test_prepared\\"


# Preparation functions
#############################################################################################################
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


# WUI generation functions
#############################################################################################################
def waterRaster(map_name, curr_nlcd):
    outRas = Con(curr_nlcd, 0, 1, "Value = 11")
    outRas.save(temp + "waterRaster.tif")
    print(f"{map_name}: water raster completed.")
   

def wildlandBaseRaster(map_name, curr_nlcd):
    outRas = Con(curr_nlcd, 1, 0, "Value = 41 OR Value = 42 OR Value = 43 OR Value = 52 OR Value = 71 OR Value = 90 OR Value = 95")
    outRas.save(temp + "wildveg.tif")
    print(f"{map_name}: wildland base raster completed.")

 
def findWildlandAreas(map_name):
    inRas = temp + "wildveg.tif"
    polys = arcpy.RasterToPolygon_conversion(inRas, temp + "wildLandPoly" + map_name, "NO_SIMPLIFY", "Value")
    
    polys2 = polys
    arcpy.AddField_management(polys, "value", "SHORT")
    
    arcpy.AddGeometryAttributes_management(polys, "AREA", "METERS", "SQUARE_METERS")
    
    with arcpy.da.UpdateCursor(temp + "wildLandPoly" + map_name + ".shp", ["POLY_AREA", "gridcode", "value"]) as cursor:
        for row in cursor:
            if (row[0] > 5000 and str(row[1]) == "1"):
                row[2] = 1
            else:
                row[2] = 0
            cursor.updateRow(row)
    
    arcpy.PolygonToRaster_conversion(polys, "value",temp + "wildlandAreas.tif")
    
    ftLayer = arcpy.MakeFeatureLayer_management(polys2, temp + "polys2Feat")
    arcpy.SelectLayerByAttribute_management(ftLayer, "NEW_SELECTION", 'POLY_AREA > 5000000 AND gridcode = 1')
    
    arcpy.CopyFeatures_management(ftLayer, temp + "preBuffer.shp")

    # this is the line where there was an error "ERROR 002836: An error occurred during the buffer operation. Failed to execute (Buffer)."
    # fixed by first creating non-dissolved layer (last param = "NONE"), then dissolving seperately
    buffPolys = arcpy.Buffer_analysis(temp + "preBuffer.shp", temp + "bufferNoDissolve.shp", "2400 meters", "FULL", "ROUND", "NONE")
    arcpy.Dissolve_management(temp + "bufferNoDissolve.shp", temp + "bufferPolys.shp")

    
    arcpy.AddField_management(temp + "bufferPolys.shp", "value", "SHORT")
    
    with arcpy.da.UpdateCursor(temp + "bufferPolys.shp", ["id", "value"]) as cursor:
        for row in cursor:
            row[1] = 1
            cursor.updateRow(row)
    
    arcpy.PolygonToRaster_conversion(temp + "bufferPolys.shp", "value", temp + "farcover")
    
    farcover = temp + "farcover"
    outcon = Con(IsNull(farcover), 0, temp + "farcover")
    outcon.save(temp + "wildveg_buffer.tif")
    
    print(f"{map_name}: Wildland areas completed.")


def footprintCentroids(map_name, curr_address_points):
    arcpy.FeatureToPoint_management(curr_address_points, temp + "housesCentroids.shp")
    print(f"{map_name}: footprint centroids completed.")


def makeNeighborhoods(map_name, buffer):
    nbrHouses = PointStatistics(temp + "housesCentroids.shp", "value1", 30, NbrCircle(buffer, "MAP"), "SUM")
    nbrHouses.save(temp + "nbrHouses" + str(buffer) + ".tif")
    print(f"{map_name}: house counting completed.")
    

def neighborhoodDensity(map_name, buffer):
    houseDen = ((arcpy.Raster(temp + "nbrHouses" + str(buffer) + ".tif") / (3.14 * float(buffer) * float(buffer))) * 1000000) > 6.17
    houseDen.save(temp + "houseDen" + str(buffer) + ".tif")
    print(f"{map_name}: neighborhood density completed.")
    

def replaceNoData(map_name, buffer):
    outCon = Con(IsNull(temp + "houseDen" + str(buffer) + ".tif"), 0, temp + "houseDen" + str(buffer) + ".tif")
    outCon.save(temp + "outCon" + str(buffer) + ".tif")
    print(f"{map_name}: finished replacing nulls in neigborhood density.")
    

def removeWater(map_name, buffer):
    denNoWater = Raster(temp + "outCon" + str(buffer) + ".tif") * Raster(temp + "waterRaster.tif")
    arcpy.management.CopyRaster(
        denNoWater,
        temp + "denNoWater" + str(buffer) + ".tif",
        pixel_type="32_BIT_FLOAT",      # May need to change this
        nodata_value="0",
        format="TIFF"
    )
    print(f"{map_name}: finished removing water areas from housing density raster.")
   

def calcWildlandCover(map_name, buffer):
    wildland_base = temp + "wildveg.tif"
    NbrCover = FocalStatistics(arcpy.Raster(wildland_base), NbrCircle(int(buffer), "MAP"), "SUM")
    NbrCover.save(temp + "nbrcover" + str(buffer) + ".tif")
    NbrCoverZero = FocalStatistics(EqualTo(arcpy.Raster(wildland_base),0), NbrCircle(int(buffer), "MAP"), "SUM")
    sumCover = NbrCover+NbrCoverZero
    sumCover.save(temp + "sumCover_" + str(buffer) + ".tif")
    wildcover = float(1)*NbrCover/(NbrCover+NbrCoverZero)
    wildcover50 = wildcover > 0.5
    wildcover50.save(temp+"wildcover50_" + str(buffer) + ".tif")
    print(f"{map_name}: finished calculating wildland cover.")
   

def calcWUI(map_name, buffer, curr_study_area):
    # calculate intermix
    IMWui = Con((Raster(temp+"denNoWater" + str(buffer) + ".tif") == 1) & (Raster(temp + "wildcover50_" + str(buffer) + ".tif") == 1), 1 , 0)
    # save intermix
    arcpy.management.CopyRaster(
        IMWui,
        output + map_name[:10] + "_im.tif",
        pixel_type="8_BIT_UNSIGNED",
        nodata_value="0",
        format="TIFF"
    )
    # calculate interface
    IFWui = Raster(temp+"denNoWater" + str(buffer) + ".tif") * Raster(temp + "wildveg_buffer.tif")
    # save interface
    IFWui.save(output + map_name[:10] + "_if.tif")
    # calculate overall map
    Wui = Con(IMWui == 1, 1, Con(IFWui == 1, 2 , 0))
    # save overall map raster
    arcpy.management.CopyRaster(
        Wui,
        output + map_name[:10] + ".tif",
        pixel_type="8_BIT_UNSIGNED",
        nodata_value="0",
        format="TIFF"
    )
    # save overall map as polygons
    arcpy.RasterToPolygon_conversion(output + map_name[:10] + ".tif", temp + "wui_polig_" + str(buffer) + ".shp", "NO_SIMPLIFY", "VALUE")
    arcpy.Clip_analysis(temp + "wui_polig_" + str(buffer) + ".shp", curr_study_area, output + map_name[:10] + "_p.shp")
    print (f"{map_name}: WUI map at " + str(buffer) + "m neighborhood buffer size completed.")


def createMaps(map_name, buffer):
    # create intermediary and output directories for given year
    os.makedirs(intermediary + map_name, exist_ok=True)
    os.makedirs(all_outputs + map_name, exist_ok=True)

    # decide which source data to use
    if (map_name == "ketchpaw-replication-test"):
        curr_address_points = kp_test_prepared + "SiteStructureAddressPoints.shp"
        curr_nlcd = kp_test_prepared + "ketchpaw_nlcd_projected_clipped_2.tif"
        curr_study_area = kp_test_prepared + "flathead_county.shp"
    else:
        curr_address_points = prepared +  map_name + "\\ap_" + map_name + ".shp"
        curr_nlcd = prepared +  map_name + "\\nlcd_" + map_name + ".tif"
        curr_study_area = prepared + "\\constant\\StateofMontana.shp"
        temp = intermediary + "\\" + map_name + "\\"
        output = all_outputs + "\\" + map_name + "\\"

    print(f"Creating map {map_name} using NLCD raster '{curr_nlcd}' and address points '{curr_address_points}'.")

    # generate centroids, water, and wildland areas - run for each year
    wildlandBaseRaster(map_name, curr_nlcd)
    waterRaster(map_name, curr_nlcd)
    addValue1(map_name, curr_address_points)
    footprintCentroids(map_name, curr_address_points)
    findWildlandAreas(map_name)

    # calculate WUI - run for each year and neighborhood buffer size
    makeNeighborhoods(map_name, buffer)
    neighborhoodDensity(map_name, buffer)
    replaceNoData(map_name, buffer)
    removeWater(map_name, buffer)
    calcWildlandCover(map_name, buffer)
    calcWUI(map_name, buffer, curr_study_area)


# Main
#############################################################################################################
if __name__ == "__main__":

    curr_maps = ["ketchpaw-replication-test"]
    curr_buffer = 500

    for curr_map in curr_maps:
        try:
            createMaps(curr_map, curr_buffer)
        except Exception as e:
            print(f"An error occurred while creating {curr_map} at {curr_buffer}m buffer distance: {e}")