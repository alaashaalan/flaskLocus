#!/usr/bin/env
# -*- coding:utf-8 -*-

from __future__ import division
import json
import math
from json import encoder
import helper_functions
# from pandas.io import sql  # Not sure if i need this 
import db
from datetime import date, datetime, timedelta

encoder.FLOAT_REPR = lambda o: format(o, '.2f')

class base_station(object):
    def __init__(self, lat, lon, dist):
        self.lat = lat
        self.lon = lon
        self.dist = dist

class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class circle(object):
    def __init__(self, point, radius):
        self.center = point
        self.radius = radius

class json_data(object):
    def __init__(self, circles, inner_points, center):
        self.circles = circles
        self.inner_points = inner_points
        self.center = center
    
def serialize_instance(obj):
    d = {}
    d.update(vars(obj))
    return d

def get_two_points_distance(p1, p2):
    return math.sqrt(pow((p1.x - p2.x), 2) + pow((p1.y - p2.y), 2))

def get_two_circles_intersecting_points(c1, c2):
    p1 = c1.center 
    p2 = c2.center
    r1 = c1.radius
    r2 = c2.radius

    d = get_two_points_distance(p1, p2)
    # if to far away, or self contained - can't be done
    if d >= (r1 + r2) or d <= math.fabs(r1 -r2):
        return None

    a = (pow(r1, 2) - pow(r2, 2) + pow(d, 2)) / (2*d)
    h  = math.sqrt(pow(r1, 2) - pow(a, 2))
    x0 = p1.x + a*(p2.x - p1.x)/d 
    y0 = p1.y + a*(p2.y - p1.y)/d
    rx = -(p2.y - p1.y) * (h/d)
    ry = -(p2.x - p1.x) * (h / d)
    return [point(x0+rx, y0-ry), point(x0-rx, y0+ry)]

def get_all_intersecting_points(circles):
    points = []
    num = len(circles)
    for i in range(num):
        j = i + 1
        for k in range(j, num):
            res = get_two_circles_intersecting_points(circles[i], circles[k])
            if res:
                points.extend(res)
    return points

def is_contained_in_circles(point, circles):
    for i in range(len(circles)):
        if (get_two_points_distance(point, circles[i].center) > (circles[i].radius)):
            return False
    return True

def get_polygon_center(points):
    center = point(0, 0)
    num = len(points)
    for i in range(num):
        center.x += points[i].x
        center.y += points[i].y
		
	if (num==0): 
		center.x=0
		center.y=0
	else:
		center.x /= num
		center.y /= num
    return center

def perdelta(start, end, delta):
    """
    helper to generate time range
    """
    curr = start
    while curr < end:
        yield curr
        curr += delta


def timestamp_matching(start_time, end_time, beacon, gateway_ids):

    p1 = point(0.00, 0.00)                       #gateway coordinates here 
    p2 = point(3.53, 3.66)
    p3 = point(0.00, 7.35)

    # create a new table
    database, cursor = db.connection();

    drop_statement = (
        "DROP TABLE IF EXISTS matched_timestamps;")
    cursor.execute(drop_statement)
    cursor.fetchall()

    create_table_statement = (
        "CREATE TABLE matched_timestamps (id INT NOT NULL AUTO_INCREMENT, time_stamp DATETIME(6), rssi1 FLOAT, rssi2 FLOAT, rssi3 FLOAT, dist1 FLOAT, dist2 FLOAT, dist3 FLOAT, locx FLOAT, locy FLOAT, PRIMARY KEY (id));"
        )
    cursor.execute(create_table_statement)
    cursor.fetchall()

    cursor.execute("SELECT * FROM raw_data;")
    results = cursor.fetchall()

    # iterate over all timestamps, look for rssis for the timestamp, add to the new table
    for timestamp in perdelta(start_time, end_time, timedelta(seconds=1)):
        rssi1 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[0])
        rssi2 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[1])
        rssi3 = db.find_avg_rssi(timestamp, timestamp, beacon, gateway_ids[2])

        d1= helper_functions.rssi_to_meter(rssi1)
        d2= helper_functions.rssi_to_meter(rssi2)
        d3= helper_functions.rssi_to_meter(rssi3)

        c1 = circle(p1, d1)                       
        c2 = circle(p2, d2)
        c3 = circle(p3, d3)

        circle_list = [c1, c2, c3]

        inner_points = []
        for p in get_all_intersecting_points(circle_list):
         if is_contained_in_circles(p, circle_list):
             inner_points.append(p) 
        
        center = get_polygon_center(inner_points)

        insert_statement = "INSERT INTO matched_timestamps (time_stamp, rssi1, rssi2, rssi3, dist1, dist2, dist3, locx, locy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (str(timestamp), rssi1, rssi2, rssi3, d1, d2, d3, center.x, center.y)

        cursor.execute(insert_statement, data)
        database.commit()
    
    select_statement = ("SELECT * FROM matched_timestamps;")
    cursor.execute(select_statement)
    results = cursor.fetchall()
    database.close()
    return results



if __name__ == '__main__' :
    pass
