# Export Sentinel-2 image tile coordinates as Shapefile for a Given Point in Decimal Degrees

## Description:
This application enables users to export the corner coordinates of Sentinel-2 imagery tiles as a shapefile for a specified geographic location. By providing point coordinates in decimal degrees (longitude and latitude), along with parameters like date range and maximum cloud cover percentage, the tool identifies the intersecting Sentinel-2 tiles and generates shapefiles containing the bounding coordinates of these tiles.

The key features of this application include:

- **Input Flexibility**: Accepts geographic point coordinates in decimal degrees to specify the location of interest.
- **Cloud Cover Filtering**: Allows users to set a maximum acceptable cloud cover percentage to retrieve clearer images.
- **Date Range Selection**: Enables filtering of Sentinel-2 imagery based on a specified date range.
- **Shapefile Export**: Creates and downloads shapefiles with polygons representing the bounding boxes of intersecting Sentinel-2 tiles.
- **User-Friendly Interface**: Provides a simple and interactive web-based interface for seamless usage.
- **Integration with Google Earth Engine**: Uses the power of Google Earth Engine's Sentinel-2 data to retrieve and process images efficiently.

This tool is ideal for geospatial analysts, researchers, and planners who need quick access to Sentinel-2 imagery tile boundaries for their projects. By automating the shapefile creation process, the application simplifies workflows, saving significant time and effort.
