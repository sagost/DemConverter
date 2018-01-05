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

from qgis.gui import QgsMapTool
from PyQt4.QtGui import QCursor, QPixmap, QColor
from qgis.gui import QgsRubberBand
from qgis.core import QgsPoint, QgsGeometry

class RectByExtentTool(QgsMapTool):
    def __init__(self, canvas, layer,Parent):
        QgsMapTool.__init__(self,canvas)
        self.Parent = Parent
        self.canvas=canvas
        self.layer = layer
        self.geom = None
        self.rb = None
        self.x0 = None
        self.y0 = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                  
 
    def canvasPressEvent(self,event):
        layer = self.layer
        color = QColor(255,0,0,70)
        self.rb = QgsRubberBand(self.canvas, True)
        self.rb.setColor(color)
        self.rb.setWidth(1)
        x = event.pos().x()
        y = event.pos().y()
        point = self.toLayerCoordinates(layer,event.pos())        
        pointMap = self.toMapCoordinates(layer, point)
        self.x0 = pointMap.x()
        self.y0 = pointMap.y()        
        if self.rb:return
            
    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        self.rb.reset(True)
        pt1 = (self.x0, self.y0)
        pt2 = (self.x0, curry)
        pt3 = (currx, curry)
        pt4 = (currx, self.y0)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0],i[1]) for i in points]
        self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        #delete [self.rb.addPoint( point ) for point in polygon]                
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return        
        if self.rb.numberOfVertices() > 2:
            self.geom = self.rb.asGeometry()
            
            #self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        self.canvas.refresh()
        #self.button.setEnabled(True)
        self.Parent.SelectAreaButton.setEnabled(True)
        self.Parent.SelectDEMExtentButton.setEnabled(True)
        self.canvas.unsetMapTool(self)
        self.Parent.DrawRubber(self.geom,0)
        
    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True