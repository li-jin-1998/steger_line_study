# Steger algorithm for edge/line extraction
# Author : Munch Quentin, 2020

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# General and computer vision lib
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib import pyplot

def computeDerivative(img, sigmaX, sigmaY):
    # blurr the image
    # img = cv2.GaussianBlur(img, ksize=(0,0), sigmaX=sigmaX, sigmaY=sigmaY)
    img=np.array(img,np.float32)/255
    # create filter for derivative calulation
    dxFilter = np.array([[1],[0],[-1]])
    dyFilter = np.array([[1,0,-1]])
    dxxFilter = np.array([[1],[-2],[1]])
    dyyFilter = np.array([[1,-2,1]])
    dxyFilter = np.array([[1,-1],[-1,1]])
    # compute derivative
    dx = cv2.filter2D(img,-1, dxFilter)
    dy = cv2.filter2D(img,-1, dyFilter)
    dxx = cv2.filter2D(img,-1, dxxFilter)
    dyy = cv2.filter2D(img,-1, dyyFilter)
    dxy = cv2.filter2D(img,-1, dxyFilter)
    return dx, dy, dxx, dyy, dxy

def computeMagnitude(dxx, dyy):
    # convert to float
    dxx = dxx.astype(float)
    dyy = dyy.astype(float)
    # calculate magnitude and angle
    mag = cv2.magnitude(dxx, dyy)
    phase = mag*180./np.pi
    return mag, phase

def computeHessian(dx, dy, dxx, dyy, dxy):
    # create empty list
    point=[]
    direction=[]
    value=[]
    alphas=[]
    # for the all image
    for x in range(0, img.shape[1]): # column
        for y in range(0, img.shape[0]): # line
            # if superior to certain threshold
            if dxy[y,x] > 0:
                # compute local hessian
                hessian = np.zeros((2,2))
                hessian[0,0] = dxx[y,x]
                hessian[0,1] = dxy[y,x]
                hessian[1,0] = dxy[y,x]
                hessian[1,1] = dyy[y,x]
                # compute eigen vector and eigne value
                ret, eigenVal, eigenVect = cv2.eigen(hessian)
                # print(eigenVal[0,0],eigenVal[1,0])
                if np.abs(eigenVal[0,0]) >= np.abs(eigenVal[1,0]):
                    nx = eigenVect[0,0]
                    ny = eigenVect[0,1]
                else:
                    nx = eigenVect[1,0]
                    ny = eigenVect[1,1]
                # calculate denominator for the taylor polynomial expension
                denom = dxx[y,x]*nx*nx + dyy[y,x]*ny*ny + 2*dxy[y,x]*nx*ny
                alpha = np.arctan2(ny, nx) / np.pi * 180
                # print(alpha,ny,nx)
                # verify non zero denom
                if denom != 0:
                    T = -(dx[y,x]*nx + dy[y,x]*ny)/denom
                    # update point
                    if np.abs(T*nx) <= 0.5 and np.abs(T*ny) <= 0.5:
                        point.append((x,y))
                        direction.append((nx,ny))
                        value.append(np.abs(dxy[y,x]+dxy[y,x]))

                        # alpha=np.arctan2(ny,nx)/np.pi*180
                        # print(alpha)
                        alphas.append(alpha)

                        # if alpha/np.pi<0.5*180:
                        #     pyplot.arrow(x, y, x+0.5*nx, x+0.5*ny, head_width=0.5, head_length=0.5, fc='b', ec='b')
    return point, direction, value,alphas

# resize, grayscale and blurr
img = cv2.imread("stripe_image.png")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# img = cv2.resize(img, (640,480))
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# compute derivative
dx, dy, dxx, dyy, dxy = computeDerivative(gray_img, 3, 3)
normal, phase = computeMagnitude(dxx, dyy)
print("normal : ", normal)
pt, dir, val ,alphas= computeHessian(dx, dy, dxx, dyy, dxy)

# take the first n max value
nMax =6000
idx = np.argsort(val)
idx = idx[::-1][:nMax]
# plot resulting point
for i in range(0, len(idx)):
    print(alphas[i])
    if alphas[i]<90 and alphas[i]>0:
        img[pt[idx[i]][0], pt[idx[i]][1], :]=(0, 0, 255*alphas[i]/180)
        # print(img[pt[idx[i]][0], pt[idx[i]][1],:])
        # img = cv2.circle(img, (pt[idx[i]][0], pt[idx[i]][1]), 1, (0, 0, 255), -1)
    else:
        img[pt[idx[i]][0], pt[idx[i]][1], :] = (0, 255*alphas[i]/180,0)
        # img = cv2.circle(img, (pt[idx[i]][0], pt[idx[i]][1]), 1, (0, 255, 0), -1)
cv2.imwrite('result.png',img)

# plot the result
# plt.imshow(dx)
# plt.show()
# plt.imshow(dy)
# plt.show()
# plt.imshow(dxx)
# plt.show()
# plt.imshow(dyy)
# plt.show()
# plt.imshow(dxy)
# plt.show()
# plt.imshow(normal)
# plt.show()
# plt.imshow(phase)
# plt.show()
plt.imshow(img)
plt.show()