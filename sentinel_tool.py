import os
import sys
import subprocess

# Ensure required modules are installed
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import ee
except ImportError:
    install_package("earthengine-api")
    import ee  # Retry import after installation

try:
    import geopandas as gpd
except ImportError:
    install_package("geopandas")
    import geopandas as gpd

try:
    from shapely.geometry import Polygon
except ImportError:
    install_package("shapely")
    from shapely.geometry import Polygon

# Other imports
import streamlit as st
import json


# Load GEE credentials from Streamlit secrets
service_account = json.loads(st.secrets["service_account_json"])
credentials = ee.ServiceAccountCredentials(
    service_account["client_email"], key_data=json.dumps(service_account)
)
ee.Initialize(credentials)

# Function to process Sentinel-2 data
def process_sentinel(input_coordinates, start_date, end_date, max_cloud_cover, output_folder):
    try:
        # Create a point geometry for the input coordinates
        input_geometry = ee.Geometry.Point(input_coordinates)

        # Retrieve Sentinel-2 ImageCollection for the given location and time
        collection = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
            .filterBounds(input_geometry) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover))

        # Get the list of images, including names and cloud cover percentages
        image_list = collection.toList(collection.size())
        image_metadata = []

        for i in range(image_list.size().getInfo()):
            img = ee.Image(image_list.get(i))
            image_id = img.get("system:index").getInfo()  # Image name
            cloud_cover = img.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()  # Cloud cover percentage
            acquisition_date = ee.Date(img.get("system:time_start")).format("YYYY-MM-dd").getInfo()  # Date
            image_metadata.append((image_id, acquisition_date, cloud_cover))

        # Display image metadata
        st.write("### Sentinel-2 Images")
        for image_id, date, cloud_cover in image_metadata:
            st.write(f"**Image ID**: {image_id}, **Date**: {date}, **Cloud Cover**: {cloud_cover}%")

        # Get the unique tile IDs
        tile_ids = collection.aggregate_array("MGRS_TILE").distinct().getInfo()

        for tile_id in tile_ids:
            try:
                # Query the tile geometry using the ImageCollection
                tile_geometry = collection.filter(ee.Filter.eq("MGRS_TILE", tile_id)).geometry()
                coords = tile_geometry.bounds().coordinates().get(0).getInfo()

                # Convert the tile geometry into a Polygon
                polygon = Polygon([(coord[0], coord[1]) for coord in coords])

                # Create a GeoDataFrame
                gdf = gpd.GeoDataFrame(
                    {"tile_id": [tile_id]},  # Add tile ID as an attribute
                    geometry=[polygon],
                    crs="EPSG:4326"  # Set the coordinate reference system to WGS84
                )

                # Save the GeoDataFrame as a shapefile
                shapefile_name = os.path.join(output_folder, f"{tile_id}.shp")
                gdf.to_file(shapefile_name, driver="ESRI Shapefile")
                st.write(f"Shapefile created for Tile: {tile_id}")

            except Exception as e:
                st.error(f"Error processing tile {tile_id}: {e}")

        # Zip the shapefiles
        zip_filename = os.path.join(output_folder, "Sentinel_Tile_Shapefiles.zip")
        with ZipFile(zip_filename, "w") as zipf:
            for root, _, files in os.walk(output_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.join(os.path.basename(root), file))

        return zip_filename

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Streamlit Interface
st.title("Sentinel-2 Data Tool")

# Input fields
longitude = st.number_input("Longitude", value=76.692, format="%.6f")
latitude = st.number_input("Latitude", value=14.322, format="%.6f")
start_date = st.date_input("Start Date", value="2024-01-01").strftime("%Y-%m-%d")
end_date = st.date_input("End Date", value="2024-12-31").strftime("%Y-%m-%d")
max_cloud_cover = st.slider("Max Cloud Cover (%)", 0, 100, 10)

# Output folder selection
output_folder = st.text_input("Output Folder Path", value="Sentinel_Tile_Shapefiles")
os.makedirs(output_folder, exist_ok=True)

# Run the tool
if st.button("Run"):
    with st.spinner("Processing..."):
        zip_file = process_sentinel([longitude, latitude], start_date, end_date, max_cloud_cover, output_folder)
        if zip_file:
            st.success("Processing completed!")
            st.write("Download the shapefiles:")
            st.download_button("Download Zip", open(zip_file, "rb"), file_name="Sentinel_Tile_Shapefiles.zip")

