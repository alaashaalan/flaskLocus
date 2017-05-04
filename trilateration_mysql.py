#!/usr/bin/env
# -*- coding:utf-8 -*-

from __future__ import division
import json
import math
from json import encoder
from helper_functions import rssi_to_meter
import csv
import MySQLdb
import config
import pandas as pd
# from pandas.io import sql  # Not sure if i need this 
from db import connection


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
	else
		center.x /= num
		center.y /= num
    return center

if __name__ == '__main__' :

    p1 = point(0.00, 0.00)                       #gateway coordinates here 
    p2 = point(4.00, 4.00)
    p3 = point(0.00, 4.00)
    
	conn, c = connection();                    # why is there a semi-coln here. 
    
   

	row_count =  c.execute('SELECT COUNT(*) FROM raw_data')
	df = pd.read_sql('SELECT * FROM raw_data', con=conn)
	

	conn.close()
	

	#x and y coordinate arrays 
    locationx=[]
    locationy=[]
    distance1=[]
    distance2=[]
    distance3=[]

	
    for i in range(row_count) : 
        d1= rssi_to_meter(df.iloc[i,1])
        d2= rssi_to_meter(df.iloc[i,2])
        d3= rssi_to_meter(df.iloc[i,3])

        c1 = circle(p1, d1)                       
        c2 = circle(p2, d2)
        c3 = circle(p3, d3)

        circle_list = [c1, c2, c3]

        inner_points = []
        for p in get_all_intersecting_points(circle_list):
         if is_contained_in_circles(p, circle_list):
             inner_points.append(p) 
        
		center = get_polygon_center(inner_points)
        
        locationx.append(center.x)
        locationy.append(center.y)
		distance1.append(d1)
		distance2.append(d2)
		distance3.append(d3)
		
    df['distance_1']=distance1
    df['distance_2']=distance2
    df['distance_3']=distance3
    df['location_x']=locationx
    df['location_y']=locationy
	
   # save new data frame to csv 
    pandas.DataFrame.to_sql
    df.to_sql(con=conn, name='Table', if_exits='replace', flavor= 'mysql')