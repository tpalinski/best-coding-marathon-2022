import math
import sqlite3
import database
import os

DB_FILENAME = "city.db"
SOURCE_DIR  = os.path.dirname(os.path.realpath(__file__)) + "\\"

db = database.connect(SOURCE_DIR + DB_FILENAME)
cursor = db.cursor() 

# https://stackoverflow.com/a/12997900
def calculateDerivedPosition(point, range, bearing):
        EarthRadius = 6371000

        latA = math.radians(point[0])
        lonA = math.radians(point[1])
        angularDistance = range / EarthRadius
        trueCourse = math.radians(bearing)

        lat = math.asin(
                math.sin(latA) * math.cos(angularDistance) +
                        math.cos(latA) * math.sin(angularDistance)
                        * math.cos(trueCourse))

        dlon = math.atan2(
                math.sin(trueCourse) * math.sin(angularDistance)
                        * math.cos(latA),
                math.cos(angularDistance) - math.sin(latA) * math.sin(lat))

        lon = ((lonA + dlon + math.pi) % (math.pi * 2)) - math.pi

        lat = math.degrees(lat)
        lon = math.degrees(lon)

        newPoint = (lat, lon)

        return newPoint

def getDistanceBetweenTwoPoints(p1, p2):
        R = 6371000 # earth radius
        dLat = math.radians(p2[0] - p1[0])
        dLon = math.radians(p2[1] - p1[1])
        lat1 = math.radians(p1[0])
        lat2 = math.radians(p2[0])

        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.sin(dLon / 2) * math.sin(dLon / 2) * math.cos(lat1) * math.cos(lat2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c

        return d

def pointIsInCircle(pointForCheck, center, radius):
        if (getDistanceBetweenTwoPoints(pointForCheck, center) <= radius):
            return True
        else:
            return False

def queryPlaces(center):
    mult = 1.1 # to be sure each place is considered
    radius = 1500 # in meters
    # calculate rectangle which will be used to filter places 
    p1 = calculateDerivedPosition(center, mult * radius, 0) # top
    p2 = calculateDerivedPosition(center, mult * radius, 90); # right
    p3 = calculateDerivedPosition(center, mult * radius, 180); # down
    p4 = calculateDerivedPosition(center, mult * radius, 270); # left
 
    inRectangleCondition =  " WHERE " + \
        "lat" + " > " + str(p3[0]) + " AND " + \
        "lat" + " < " + str(p1[0]) + " AND " + \
        "lon" + " < " + str(p2[1]) + " AND " + \
        "lon" + " > " + str(p4[1])

    categories = ("edukacja", "zdrowie", "rozrywka", "jedzenie", "sport", "kultura", "dzieci", "kawiarnie", "natura", "biznes", "uslugi", "transport_publiczny", "sklepy")

    for category in categories:
        selectString = f"SELECT * FROM {category}" + inRectangleCondition
        
        cursor.execute(selectString)
        rows = cursor.fetchall()

        for row in rows:
            placeCoords = (row[0], row[1])
            if pointIsInCircle(placeCoords, center, radius):
                print(row)


if __name__ == "__main__":
    # DIRTY TESTING
    # print(getDistanceBetweenTwoPoints((54.370892, 18.6132158), (54.3893330823781, 18.609979311308994)))

    # res = cursor.execute("SELECT name FROM sqlite_master")
    # print(cursor.fetchall())

    queryPlaces((54.36996991475207, 18.60749250801278))
    database.close(cursor, db)
