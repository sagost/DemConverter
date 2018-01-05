# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DemConverter
                                 A QGIS plugin
 Convert DEM file
                             -------------------
        begin                : 2017-01-23
        copyright            : (C) 2017 by Salvatore Agosta
        email                : sagost@katamail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DemConverter class from file DemConverter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dem_converter import DemConverter
    return DemConverter(iface)
