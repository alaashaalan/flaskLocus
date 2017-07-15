#!/usr/bin/env
# -*- coding:utf-8 -*-

# from https://github.com/noomrevlis/trilateration

from __future__ import division
import json
import math
from json import encoder
import helper_functions
import db
from datetime import date, datetime, timedelta
import optimization_trilateration

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

    def to_array(self):
        return [self.x, self.y]

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
    diff = get_two_points_distance(p1, p2) - r1 - r2

    if d <= math.fabs(r1 -r2):          # Need to come up with better solution for this. 
        print("small")
        if r1<r2: 
            x0=p1.x 
            y0=p1.y
        else: 
            x0=p2.x
            y0=p2.y
        return [point(x0 , y0)]
        
    if d >= (r1 + r2): 
        print("no touch")
        if r1 > r2: 
            r2 = r2 + diff + 0.15
            c2.radius = r2 
        else: 
            r1 = r1 + diff + 0.15
            c1.radius = r1 

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
            else:
                print("something wrong")
    return points

def is_contained_in_circles(point, circles):
    for i in range(len(circles)):
        if (get_two_points_distance(point, circles[i].center) > ((circles[i].radius)+.1)):
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

def trilateration(points, distances):
    circle_list = []
    for point, distance in zip(points, distances):
        print point.x
        circle_list.append(circle(point, distance))

    # print(circle_list[1].center)
    # gw1= circle_list[1].center
    # print type(gw1)
    # print(gw1[0])



    inner_points = []
    all_points = []
    i = 0
    for p in get_all_intersecting_points(circle_list):
        if is_contained_in_circles(p, circle_list):
            i += 1
            inner_points.append(p) 
        all_points.append(p)       
    
    # if (i==0):
    #     center = optimization_trilateration.trilaterate(points, distances)
    #     return center
    
    center = get_polygon_center(inner_points)
    return center  

if __name__ == '__main__' :

    p1 = point(0.81, 1.2)
    p2 = point(1.21, 0.69)
    p3 = point(0.87, 0.84)

    c1 = 0.70
    c2 = 0.51
    c3 = 0.63

    intersect = trilateration([p1,p2,p3],[c1,c2,c3])
    print intersect.x, intersect.y
    # p1 = point(0.81, 1.2)
    # p2 = point(1.21, 0.69)
    # p3 = point(0.87, 0.84)

    # c1 = circle(p1, 0.70)
    # c2 = circle(p2, 0.51)
    # c3 = circle(p3, 0.63)

    # circle_list = [c1, c2, c3]

    # inner_points = []
    # for p in get_all_intersecting_points(circle_list):
    #     if is_contained_in_circles(p, circle_list):
    #         inner_points.append(p) 
    


    # center = get_polygon_center(inner_points)


    # print center.x, center.y
