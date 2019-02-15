#!/usr/bin/python3
import matplotlib.pyplot as plt 
from matplotlib.patches import Ellipse, Circle, Polygon
import matplotlib.animation as animation
from math import pi
import numpy as np
from random import random 
import serial

# https://www.robot-electronics.co.uk/htm/srf05tech.htm

angle = 0

R_MAX = 120

ANGLE_RES = np.deg2rad(15)
DIST_RES = 0.3

VAR_R = DIST_RES ** 2
VAR_T = ANGLE_RES ** 2

ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flushInput()

fig = plt.figure()
ax = plt.axes()
ax.axis('scaled')
ax.set_ylim((-50, 50))  
ax.set_xlim( (0, 100))

resolution = Polygon([
    (0, 0),
    (R_MAX * np.cos(ANGLE_RES + angle), R_MAX * np.sin(ANGLE_RES + angle)),
    (R_MAX * np.cos(-ANGLE_RES + angle), R_MAX * np.sin(-ANGLE_RES + angle)),
    (0, 0)
], alpha=0.05, facecolor='r', zorder=1)

ellipse99 = Ellipse((0, 0), 0, 0, 0, zorder=2, fill=False, ec='g', alpha=1)
ellipse95 = Ellipse((0, 0), 0, 0, 0, zorder=2, fill=False, ec='b', alpha=1)
ellipse1s = Ellipse((0, 0), 0, 0, 0, zorder=2, fill=False, ec='r', alpha=1)
circle = Circle((0, 0), 0.5, color='b', zorder=3, alpha=1)
distance = ax.text(10, 40, "R: ", fontsize=16)

def init():
    global circle
    ax.add_patch(circle)
    ax.add_patch(resolution)
    ax.add_patch(ellipse95)
    ax.add_patch(ellipse1s)
    ax.add_patch(ellipse99)

def update(frameNum, circle, distance, ellipse95, ellipse1s):
    global ser, angle
    try:
        line = ser.readline()
        data = np.fromstring(line.decode('ascii', errors='replace'),sep=',')
        if (len(data) > 0):
            r = data[0]
        else:
            r = 0

        if (r > 0 or 1):

            distance.set_text("R: %.1f cm" % r)


            c = np.cos(angle)
            s = np.sin(angle)
            var_rr = VAR_R * c * c + VAR_T * (r ** 2) * (s ** 2)
            var_tr = VAR_R * c * s - VAR_T * (r ** 2) * c * s
            var_tt = VAR_R * s * s + VAR_T * (r ** 2) * (c ** 2)
            cov = np.array([
                [var_rr, var_tr],
                [var_tr, var_tt]
            ])

            eigenvalues, eigenvectors = np.linalg.eig(cov)

            # Get index of the smallest and largest eigenvalues
            largest = eigenvalues.argmax()
            smallest = eigenvalues.argmin()

            largest_eigenvec = eigenvectors[largest]
            #print(largest_eigenvec)
            #print(np.arctan2(largest_eigenvec[1], largest_eigenvec[0]))

            circle.center = (r*c, r*s)
            ellipse99.center = circle.center
            ellipse95.center = circle.center
            ellipse1s.center = circle.center

            a = np.rad2deg(np.arctan2(largest_eigenvec[1], largest_eigenvec[0]))
            if a < 0:
                a += 360

            # Total length
            ellipse95.angle = a
            ellipse95.width = 2 * np.sqrt(eigenvalues[largest] * 3.841)
            ellipse95.height = 2 * np.sqrt(eigenvalues[smallest] * 3.841)

            ellipse1s.angle = a
            ellipse1s.width = 2 * np.sqrt(eigenvalues[largest])
            ellipse1s.height = 2 * np.sqrt(eigenvalues[smallest])

            ellipse99.angle = a
            ellipse99.width = 2 * np.sqrt(eigenvalues[largest] * 6.635)
            ellipse99.height = 2 * np.sqrt(eigenvalues[smallest] * 6.635)


            #print(ellipse95.width, ellipse95.height)
            #print("COV:", cov)
            print("EV:", eigenvectors)
            print ("Eval: ", eigenvalues, smallest, largest)



    except Exception as e:
        print(e)
        quit()

if __name__ == "__main__":
    anim = animation.FuncAnimation(fig, update, fargs=(circle, distance, ellipse95, ellipse1s), init_func=init, interval=20)
    plt.show()