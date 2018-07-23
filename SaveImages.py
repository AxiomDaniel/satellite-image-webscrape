import urllib.request
import csv
from loginDetails import api_key


def scrubImage(latitude, longitude, size, zoom, meterID):
    query = "http://au0.nearmap.com/staticmap?center=" + latitude + "," + longitude + "&size=" + size + "x" + size + \
        "&zoom=" + zoom + api_key
    imageName = str(meterID) + ".jpg"
    urllib.request.urlretrieve(query, imageName)


if __name__ == "__main__":
    filename = input("Filename: ")
    zoom = input("Input zoom(e.g. 1-20): ")
    size = input("Size: ")

    # Open CSV file (e.g. longlat_df.csv)
    with open(filename) as file:
        csv_iter = csv.reader(file)
        next(csv_iter, None)
        for row in csv_iter:
            # Index based on longlat_df.csv
            scrubImage(row[1], row[2], size, zoom, row[0])
