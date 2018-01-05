# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DemConverterDockWidget
                                 A QGIS plugin
 Convert DEM file
                             -------------------
        begin                : 2017-01-23
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Salvatore Agosta
        email                : sagost@katamail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import numpy as np
from osgeo import gdal

def write_ply(filename, coordinates, triangles, binary=True):
    template = "ply\n"
    if binary:
        template += "format binary_" + sys.byteorder + "_endian 1.0\n"
    else:
        template += "format ascii 1.0\n"
    template += """element vertex {nvertices:n}
property float x
property float y
property float z
element face {nfaces:n}
property list int int vertex_index
end_header
"""

    context = {
     "nvertices": len(coordinates),
     "nfaces": len(triangles)
    }

    if binary:
        with  open(filename,'wb') as outfile:
            outfile.write(template.format(**context))
            coordinates = np.array(coordinates, dtype="float32")
            coordinates.tofile(outfile)

            triangles = np.hstack((np.ones([len(triangles),1], dtype="int") * 3,
                triangles))
            triangles = np.array(triangles, dtype="int32")
            triangles.tofile(outfile)
    else:
        with  open(filename,'w') as outfile:
            outfile.write(template.format(**context))
            np.savetxt(outfile, coordinates, fmt="%.3f")
            np.savetxt(outfile, triangles, fmt="3 %i %i %i")
        
def readraster(filename):
    raster = gdal.Open(filename)
    return raster


def createvertexarray(raster):
    transform = raster.GetGeoTransform()
    width = raster.RasterXSize
    height = raster.RasterYSize
    x = np.arange(0, width) * transform[1] + transform[0]
    y = np.arange(0, height) * transform[5] + transform[3]
    xx, yy = np.meshgrid(x, y)
    zz = raster.ReadAsArray()
    vertices = np.vstack((xx,yy,zz)).reshape([3, -1]).transpose()
    return vertices


def createindexarray(raster):
    width = raster.RasterXSize
    height = raster.RasterYSize

    ai = np.arange(0, width - 1)
    aj = np.arange(0, height - 1)
    aii, ajj = np.meshgrid(ai, aj)
    a = aii + ajj * width
    a = a.flatten()

    tria = np.vstack((a, a + width, a + width + 1, a, a + width + 1, a + 1))
    tria = np.transpose(tria).reshape([-1, 3])
    return tria