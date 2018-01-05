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

import os
from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QCursor, QPixmap, QColor,  QFileDialog
from qgis.core import *
from qgis.gui import QgsRubberBand
from RectByExtent import RectByExtentTool
import PLYExporter 
import numpy
from osgeo import gdal,osr
import subprocess
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dem_converter_dockwidget_base.ui'))


class DemConverterDockWidget( QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(DemConverterDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        
        self.rb = None
        self.Layer = None
        self.ClippingExtent = None
        self.EExtent = 0
        #self.rectbyextenttool = RectByExtentTool( self.iface.mapCanvas(),Layer )
        
        self.ExportButton.setEnabled(False)
        self.SelectAreaButton.setEnabled(False)
        self.SelectDEMExtentButton.setEnabled(False)
        
        self.LoadButton.clicked.connect(self.LoadLayer)
        self.SelectAreaButton.clicked.connect(self.SelectArea)
        self.SelectDEMExtentButton.clicked.connect(self.SelectRasterArea)
        self.ExportButton.clicked.connect(self.Export)
        self.rectbyextenttool = RectByExtentTool( self.iface.mapCanvas(),self.Layer , self)
    
    def LoadLayer(self):
        self.comboBox.clear()
        LayerRegistryItem = QgsMapLayerRegistry.instance().mapLayers()
        for id, layer in LayerRegistryItem.iteritems():
            if layer.type() == QgsMapLayer.RasterLayer:
                self.comboBox.addItem(layer.name(), id)
                
        if self.comboBox.count() > 0:
                self.SelectAreaButton.setEnabled(True)
                self.SelectDEMExtentButton.setEnabled(True)
    
    def SelectRasterArea(self):
        
        self.ClippingExtent = None
        self.EExtent = 1  
        if self.rb != None:
            self.rb.reset(True)  
            self.rb=None
            self.iface.mapCanvas().refresh() 
              
        LayerName = self.comboBox.itemData(self.comboBox.currentIndex())
        self.Layer = QgsMapLayerRegistry.instance().mapLayer(LayerName)
        pixelSizeX = self.Layer.rasterUnitsPerPixelX()
        pixelSizeY = self.Layer.rasterUnitsPerPixelY()
        self.minRes = min(pixelSizeX,pixelSizeY)
        self.doubleSpinBox.setMinimum(self.minRes) 
        self.doubleSpinBox.setValue(self.minRes) 
        
        
        geom = QgsGeometry.fromRect(self.Layer.extent())
        self.ClippingExtent = QgsGeometry.fromRect(self.Layer.extent())
        
        
        self.DrawRubber(geom,1) 
              
    def SelectArea(self):
        
        self.ClippingExtent = None
        self.EExtent = 0
        
        if self.rb != None:
            self.rb.reset(True)  
            self.rb=None
            self.iface.mapCanvas().refresh() 
              
        LayerName = self.comboBox.itemData(self.comboBox.currentIndex())
        self.Layer = QgsMapLayerRegistry.instance().mapLayer(LayerName)
        pixelSizeX = self.Layer.rasterUnitsPerPixelX()
        pixelSizeY = self.Layer.rasterUnitsPerPixelY()
        self.minRes = min(pixelSizeX,pixelSizeY)
        self.doubleSpinBox.setMinimum(self.minRes) 
        self.doubleSpinBox.setValue(self.minRes) 
        
        self.rectbyextenttool = RectByExtentTool( self.iface.mapCanvas(),self.Layer , self)
        self.SelectAreaButton.setEnabled(False)
        self.SelectDEMExtentButton.setEnabled(False)
        self.iface.mapCanvas().setMapTool(self.rectbyextenttool)
        
    #   skip to DrawRubber passing geom 
     #   ^
    #    |
     #   |
        
    def DrawRubber(self,geom,numero):
        
        renderer = self.iface.mapCanvas().mapRenderer()
        layerCRSSrsid = self.Layer.crs()
        projectCRSSrsid = renderer.destinationCrs()
        
        if numero == 0:
            
            color = QColor(255,0,0,70)
            self.rb = QgsRubberBand(self.iface.mapCanvas(), True)
            self.rb.setColor(color)
            self.rb.setWidth(1)
            self.rb.setToGeometry(geom, None)
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
            self.ClippingExtent = geom
            
        elif numero == 1:
            
            geom.transform(QgsCoordinateTransform(layerCRSSrsid, projectCRSSrsid))
            color = QColor(255,0,0,70)
            self.rb = QgsRubberBand(self.iface.mapCanvas(), True)
            self.rb.setColor(color)
            self.rb.setWidth(1)
            self.rb.setToGeometry(geom, None)

        self.ExportButton.setEnabled(True)  
        
    
    
    def Export(self):
        
        
        ExportType = self.comboBox_2.currentText()
        
        
        self.OutputFile = QFileDialog.getSaveFileName(caption = 'Save Export file')
        
        if not self.OutputFile == '':
            
            if self.EExtent == 0:
                
                ulx = str(self.ClippingExtent.asPolygon()[0][0][0])
                uly = str(self.ClippingExtent.asPolygon()[0][0][1])
                lrx = str(self.ClippingExtent.asPolygon()[0][2][0])
                lry = str(self.ClippingExtent.asPolygon()[0][2][1])
            else:
                ulx = str(self.ClippingExtent.asPolygon()[0][3][0])
                uly = str(self.ClippingExtent.asPolygon()[0][3][1])
                lrx = str(self.ClippingExtent.asPolygon()[0][1][0])
                lry = str(self.ClippingExtent.asPolygon()[0][1][1])
    
            #self.iface.messageBar().pushMessage('Dem Converter: running...')            
            if self.OutputFile == None:
                pass
            else:
                resize = 0
                if self.radioButton_2.isChecked()==True:
                    resolution = float(self.doubleSpinBox.value())
                    resize = 1
                    translate = ('gdalwarp -tr '+str(resolution)+' '+str(resolution)+' '+ str(self.Layer.dataProvider().dataSourceUri())+
                             ' '+ str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverterResize.tif')
                    
                    #os.system(translate)
                    cmd = os.popen(translate)
                    cmd.close()
                
                if resize == 0:    
                    translate = ('gdal_translate -projwin ' + ulx+' ' + 
                                 uly+' '+ lrx +' '+lry+' '+ str(self.Layer.dataProvider().dataSourceUri())+
                                 ' '+ str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif')
                else:
                    translate = ('gdal_translate -projwin ' +ulx+' ' + 
                                 uly+' '+lrx
                                 +' '+lry+' '+ str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverterResize.tif'+
                                 ' '+ str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif')
                    
                #os.system(translate)
                cmd = os.popen(translate)
                cmd.close()
                
            
                if ExportType == '.PLY':
                    self.PlyExporter()
                elif ExportType == '.dat':
                    self.DatExporter(0,ulx,uly,lrx,lry)
                elif ExportType == '.dat (flipped)':
                    self.DatExporter(1,ulx,uly,lrx,lry)
            
            os.remove(str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif')
            try:
                os.remove(str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif.aux.xml')
            except:
                pass
            
            if resize == 1:
                os.remove(str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverterResize.tif')
                try:
                    os.remove(str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverterResize.tif.aux.xml')
                except:
                    pass
                
            self.iface.messageBar().pushMessage('Dem Converter: conversion complete!')
            self.ExportButton.setEnabled(False)
            
    def DatExporter(self, flipped,ulx,uly,lrx,lry):
        
        ds = gdal.Open(str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif')
        myarray = numpy.array(ds.GetRasterBand(1).ReadAsArray())
        
        if flipped == 1:
            myarray = numpy.flipud(myarray)
        
        delimiter= ' '
        fmt= '%.d'
        
        with open(self.OutputFile+'.dat', 'w') as fh:
            for row in myarray:
                line = delimiter.join("0" if value == 0 else fmt % value for value in row)
                fh.write(line + '\n')
                
        EPSG = self.Layer.dataProvider().crs().authid()
        
        
        with open(self.OutputFile+'.dat.GCP','w') as txt:
            if flipped == 0:
                txt.write(EPSG+'\n'+'ulx = '+ulx+'\n'+'uly = '+uly+'\n'+'lrx = '+lrx+'\n'+'lry = '+lry)
            else:
                txt.write(EPSG+' Flipped Data\n'+'llx = '+ulx+'\n'+'lly = '+uly+'\n'+'urx = '+lrx+'\n'+'ury = '+lry)
                
        #numpy.savetxt(self.OutputFile+'.dat',myarray,fmt='%.d',delimiter = ' ')
        ds = None
        

        
    def PlyExporter(self): 
        
        
        inputfile = str(self.Layer.dataProvider().dataSourceUri()).split('.')[0]+'DemConverter_tmp.tif'
        outputfile = self.OutputFile+'.ply'
    
        raster = PLYExporter.readraster(inputfile)
        #print raster
        vertices = PLYExporter.createvertexarray(raster)
        triangles = PLYExporter.createindexarray(raster)
        #del raster
        
        PLYExporter.write_ply(outputfile, vertices, triangles, binary=True)
        self.ExportButton.setEnabled(False)
        
        
    def closeEvent(self, event):
        
        self.comboBox.clear()
        self.doubleSpinBox.setValue(0)
        self.iface.mapCanvas().unsetMapTool(self.rectbyextenttool)
        self.EExtent = 0
        self.ClippingExtent = None
        self.SelectAreaButton.setEnabled(False)
        self.SelectDEMExtentButton.setEnabled(False)
        
        if self.rb != None:
            self.rb.reset(True)  
            self.rb=None
            self.iface.mapCanvas().refresh() 
            
        self.Layer = None    
        self.closingPlugin.emit()
        event.accept()

