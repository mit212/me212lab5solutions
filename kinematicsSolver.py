#!/usr/bin/python
#All units are in mm
from math import sqrt
from scipy.optimize import fsolve
import numpy as np
arctan = np.arctan
pi = np.pi
sin = np.sin
cos = np.cos

RAD2DEG = 180.0/pi
DEG2RAD = pi/180.0

# POSITIVE MOTION OF THETA MOVES ARM DOWN! This is opposite the ODrive convention!

class position(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class deltaRobot(object):
	def __init__(self, sb = 220.332, sp = 109.1625, L = 304.8, l = 609.5144, h = 42.8475, tht0 = (0, 0, 0)):
		
		(self.currTheta1, self.currTheta2, self.currTheta3) = tht0
		self.vel1 = 0
		self.vel2 = 0
		self.vel3 = 0
		#base equilateral triangle side (sb)
		#platform equilateral triangle side (sp)
		#upper legs length (L)
		#lower legs parallelogram length (l)
		#lower legs parallelogram width (h)
		self.sb = sb
		self.sp = sp
		self.L = L
		self.l = l
		self.h = h

		#planar distance from {0} to near base side (wb)
		#planar distance from {0} to a base vertex (ub)
		#planar distance from {p} to a near platform side (wp)
		#planar distance from {p} to a platform vertex (up)
		self.wb = (sqrt(3)/6) * self.sb
		self.ub = (sqrt(3)/3) * self.sb
		self.wp = (sqrt(3)/6) * self.sp
		self.up = (sqrt(3)/3) * self.sp
		
		self.a = self.wb - self.up
		self.b = self.sp/2 - (sqrt(3)/2) * self.wb
		self.c = self.wp - self.wb/2

		#Solve for endposition
		#x^2 + y^2 + z^2 = l^2 - 2*y*a -L^2 - a^2 - 2*L*(y+a)
		#x^2 + y^2 + z^2 = -b^2 - c^2 -L^2 - 2*x*b - 2*y*c + l^2 + L*(sqrt(3)*(x+b) + y+c)
		#x^2 + y^2 + z^2 = -c^2 - L^2 -L*(sqrt(3)*(x-b) - y -c) + 2*x*b + l^2 - 2*y*c
		#REWRITTEN
		#x^2 + y^2 + z^2 = m^2 - 2*y*a -L^2 - a^2 - 2*L*(y+a)
		#x^2 + y^2 + z^2 = -b^2 - c^2 -L^2 - 2*x*b - 2*y*c + m^2 + L*(sqrt(3)*(x+b) + y+c)
		#x^2 + y^2 + z^2 = -c^2 - L^2 -L*(sqrt(3)*(x-b) - y -c) + 2*x*b + m^2 - 2*y*c
		(xx, yy, zz)=self.FK((self.currTheta1, self.currTheta2, self.currTheta3))
		print(xx, yy, zz)
		self.x = xx
		self.y = yy
		self.z = zz

		(th1, th2, th3) = self.IK((self.x, self.y, self.z))
		print(RAD2DEG*th1, RAD2DEG*th2, RAD2DEG*th3)
	
	def FK(self,thts):
		#	Works regardless of length unit. Angle units are in radians. 
		th1, th2, th3 = thts
		def simulEqns(inp):
			(x, y, z) = inp
			l = self.l
			L = self.L
			a = self.a
			b = self.b
			c = self.c
			eq1 = 2*z*L*sin(th1) + x*x + y*y + z*z - l*l + L*L + a*a + 2*y*a + 2*L*(y+a)*cos(th1) 
			eq2 = 2*z*L*sin(th2) + x*x + y*y + z*z - l*l + L*L + b*b + c*c + 2*x*b + 2*y*c - L*(sqrt(3)*(x+b)+y+c)*cos(th2) 
			eq3 = 2*z*L*sin(th3) + x*x + y*y + z*z - l*l + L*L + b*b + c*c - 2*x*b + 2*y*c + L*(sqrt(3)*(x-b)-y-c)*cos(th3)
			return (eq1, eq2, eq3)
		return fsolve(simulEqns,(0,0,-100))
	
	def IK(self, endPos):
		x, y, z = endPos		
		def simulEqns(inp):
			(th1, th2, th3) = inp
			l = self.l
			L = self.L
			a = self.a
			b = self.b
			c = self.c
			eq1 = 2*z*L*sin(th1) + x*x + y*y + z*z - l*l + L*L + a*a + 2*y*a + 2*L*(y+a)*cos(th1) 
			eq2 = 2*z*L*sin(th2) + x*x + y*y + z*z - l*l + L*L + b*b + c*c + 2*x*b + 2*y*c - L*(sqrt(3)*(x+b)+y+c)*cos(th2) 
			eq3 = 2*z*L*sin(th3) + x*x + y*y + z*z - l*l + L*L + b*b + c*c - 2*x*b + 2*y*c + L*(sqrt(3)*(x-b)-y-c)*cos(th3)
			return (eq1, eq2, eq3)
		return fsolve(simulEqns,(0,0,0))
		

	def solveTheta1(self, position):
		#Takes in an argument that is position class
		#Solves for Theta1
		E1 = 2*self.L*(position.y+self.a)
		F1 = 2*position.z*self.L
		G1 = position.x**2 + position.y**2 + position.z**2 + self.a**2 + self.L**2 + 2*position.y*self.a - self.l**2

		return self.angleSolver(E1, F1, G1, 1)

	def solveTheta2(self, position):
		E2 = -self.L*(sqrt(3) * (position.x + self.b) + position.y + self.c)
		F2 = 2*position.z*self.L
		G2 = position.x**2 + position.y**2 + position.z**2 + self.b**2 + self.c**2 + self.L**2 + 2*(position.x*self.b + position.y*self.c) - self.l**2

		return self.angleSolver(E2, F2, G2, 2)

	def solveTheta3(self, position):
		E3 = self.L * (sqrt(3) * (position.x - self.b) - position.y - self.c)
		F3 = 2*position.z*self.L
		G3 = position.x**2 + position.y**2 + position.z**2 + self.b**2 + self.c**2 + self.L**2 + 2*(-position.x*self.b + position.y*self.c) - self.l**2

		return self.angleSolver(E3, F3, G3, 3)

	def angleSolver(self, E, F, G, thetaID):
		t1 = (-F + sqrt(E**2 + F**2 - G**2))/(G - E)
		t2 = (-F - sqrt(E**2 + F**2 - G**2))/(G - E)
		thetaPossible1 = 2*arctan(t1)
		thetaPossible2 = 2*arctan(t2)

		if(thetaID == 1):
			currTheta = self.currTheta1
		
		elif(thetaID == 2):
			currTheta = self.currTheta2

		elif(thetaID == 3):
			currTheta = self.currTheta3

		#calculate the difference between the possible angles that solves the quadratic with current angle. 
		thetaDiff1 = thetaPossible1 - self.currTheta1
		thetaDiff2 = thetaPossible2 - self.currTheta2

		#return the theta that is closest to the current theta
		if(abs(thetaDiff1) < abs(thetaDiff2)):
			return thetaPossible1

		else:
			return thetaPossible2
	
	def velIKSolver(self, inputVec):
		#inputVec is a vector in meters per second. [xdot, ydot, zdot]
		a11 = self.x
		a12 = self.y+self.a + self.L*cos(self.currTheta1)
		a13 = self.z + self.L*sin(self.currTheta1)

		a21 = 2*(self.x+self.b) - sqrt(3)*self.L*cos(self.currTheta2)
		a22 = 2*(self.y + self.c) - self.L*cos(self.currTheta2)
		a23 = 2*(self.z + self.L*sin(self.currTheta2))

		a31 = 2*(self.x - self.b) + sqrt(3)*self.L*cos(self.currTheta3)
		a32 = 2*(self.y + self.c) - self.L*cos(self.currTheta3)
		a33 = 2*(self.z + self.L*sin(self.currTheta3))
		A = np.matrix([[a11, a12, a13], 
			 [a21, a22, a23], 
			 [a31, a32, a33]])
		b11 = L*((self.y + self.a)*sin(self.currTheta1) - self.z*cos(self.currTheta1))
		b22 = -L*((sqrt(3)*(self.x + self.b) + self.y + self.c)*sin(self.currTheta2) + 2*self.z*cos(self.currTheta2))
		b33 = L*((sqrt(3)*(self.x-self.b) - self.y - self.c)*sin(self.currTheta3) - 2*self.z*cos(self.currTheta3))
		B = np.matrix([[b11, 0, 0], 
			[0,b22,0], 
			[0,0, b33]])
		AB = np.matmul(A,B)
		thetadot = np.matmul(AB, inputVec)

		#return a vector of the angle velocities. [omega1, omega2, omega3]
		return thetadot
	
			



