# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SplitLinesByPoints
                                 A QGIS plugin
 Split Lines By Points
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-11-09
        copyright            : (C) 2024 by Giulio Fattori
        email                : giulio.fattori@tin.it
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

__author__ = 'Giulio Fattori'
__date__ = '2024-11-09'
__copyright__ = '(C) 2024 by Giulio Fattori'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
        
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDefinition,
                       QgsCoordinateReferenceSystem,
                       QgsFeatureRequest,
                       QgsFeature,
                       QgsGeometry,
                       QgsPoint,
                       QgsProject,
                       QgsWkbTypes,
                       QgsVectorLayer)
from qgis import processing

import math
import pathlib
import os              
import inspect
from qgis.PyQt.QtGui import QIcon
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]                                                                   

from PyQt5 import QtGui
from PyQt5 import QtCore


class SplitLinesByPointsAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_LINES = 'INPUT_LINES'
    INPUT_POINTS = 'INPUT_POINTS'
    INPUT_MAX_DISTANCE = 'INPUT_MAX_DISTANCE'
    INPUT_MIN_DISTANCE = 'INPUT_MIN_DISTANCE'
    INPUT_MIN_BUFFER_DISTANCE = 'INPUT_MIN_BUFFER_DISTANCE'
    INPUT_MAX_BUFFER_DISTANCE = 'INPUT_MAX_BUFFER_DISTANCE'
    
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SplitLinesByPointsAlgorithm()
    
    def icon(self):
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'icon.png')))
        return icon
        
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'SplitLinesByPoints'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SplitLinesByPoints')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        header = '''<img src="'''+ os.path.join(os.path.join(cmd_folder, 'icon.png')) + '''" width="50" height="50" style="float:right">'''
        # print(os.path.join(pathlib.Path(__file__).parent.resolve(),'README.html'))
        tutorial_link = '''<a href="file:///''' + os.path.join(pathlib.Path(__file__).parent.resolve(),'help','help.html') + '''">README FOR MORE DETAILS</a>'''
        
        return self.tr(header + "Breaks the line at the distance of the points that fall within the defined buffer<p>\
            <strong>Default Parameters:\
            <p><mark style='color:blue'>maximum distance from the line to points\
            <strong><p>Optional Parameters:\
            <ul>\
            <p>AREAL BUFFER\
            <li><mark style='color:blue'>minimum distance from the line to points</li>\
            <p>LINEAR BUFFER\
            <li><mark style='color:blue'>minimum distance between split points</li>\
            <li><mark style='color:blue'>maximum distance between split points</li>\
            </ul><p><b><mark style='color:red'>NOTE: " + tutorial_link)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LINES,
                self.tr('Input line layer'),
                [QgsProcessing.SourceType.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                self.tr('Input points layer'),
                [QgsProcessing.SourceType.TypeVectorPoint]
            )
        )
        
        self.addParameter(
        QgsProcessingParameterNumber(
            self.INPUT_MAX_BUFFER_DISTANCE,
            self.tr('maximum distance from line'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue = 1.0
            )
        )
        
        param = QgsProcessingParameterNumber('INPUT_MIN_BUFFER_DISTANCE', 'minimum distance from line', optional=True, type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1e+20, defaultValue=0.0)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        
        param = QgsProcessingParameterNumber('INPUT_MIN_DISTANCE', 'minimum distance between split points', optional=True, type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1e+20, defaultValue=0)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
       
        param = QgsProcessingParameterNumber('INPUT_MAX_DISTANCE', 'maximum distance between split points', optional=True, type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1e+20, defaultValue=0.0)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
            
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Segments'),
                optional = True,
                createByDefault = True
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        line_layer = self.parameterAsSource(
            parameters,
            self.INPUT_LINES,
            context
        )

        point_layer = self.parameterAsSource(
            parameters,
            self.INPUT_POINTS,
            context
        )

        ext_point_layer = self.parameterAsLayer(
            parameters,
            self.INPUT_POINTS,
            context)

        min_distance = self.parameterAsDouble(
            parameters,
            self.INPUT_MIN_DISTANCE,
            context)

        max_distance = self.parameterAsDouble(
            parameters,
            self.INPUT_MAX_DISTANCE,
            context)
            
        min_buffer_distance = self.parameterAsDouble(
            parameters,
            self.INPUT_MIN_BUFFER_DISTANCE,
            context)
        
        max_buffer_distance = self.parameterAsDouble(
            parameters,
            self.INPUT_MAX_BUFFER_DISTANCE,
            context)

        fields = line_layer.fields()
        (split_lines, dest_id) = self.parameterAsSink(
                parameters,
                self.OUTPUT,
                context, fields, QgsWkbTypes.LineString, line_layer.sourceCrs()
            )

        if min_distance > max_distance:
            feedback.reportError(f"min distance from line > MAX distance from line")
        
        # max ipotetic distance between points
        if max_distance == 0.0:
            point_layer_ext = ext_point_layer.extent()
            x_dim = point_layer_ext.xMaximum()- point_layer_ext.xMinimum()
            y_dim = point_layer_ext.yMaximum()- point_layer_ext.yMinimum()
            max_dim = math.ceil(math.sqrt((math.pow(x_dim,2)+math.pow(y_dim,2))))
            # feedback.pushInfo(f"point layer diag: {max_dim}")
            max_distance = max_dim

        def distance_between_points(point1, point2):
            return ((point1.x() - point2.x())**2 + (point1.y() - point2.y())**2)**0.5

        # feedback.pushInfo(f"Line layer: {line_layer.sourceName()}, feature count: {line_layer.featureCount()}")
        # feedback.pushInfo(f"Point layer: {point_layer.sourceName()}, feature count: {point_layer.featureCount()}")
        # feedback.pushInfo("--------------------")

        # Iterate through each line feature
        for line_feature in line_layer.getFeatures():
            line_geom = line_feature.geometry()
            if not line_geom:
                feedback.pushInfo(f"Invalid geometry for feature ID: {line_feature.id()}")
                continue

            # Create buffers around the line
            max_buffer_geom = line_geom.buffer(max_buffer_distance, 5)
            min_buffer_geom = line_geom.buffer(min_buffer_distance, 5)

            # Get all points within the buffer range
            request = QgsFeatureRequest().setFilterRect(max_buffer_geom.boundingBox())
            nearby_points = [
                point.geometry().asPoint() for point in point_layer.getFeatures(request) if max_buffer_geom.intersects(
                    point.geometry()) and not min_buffer_geom.intersects(
                    point.geometry())]

            # feedback.pushInfo(f"Feature ID: {line_feature.id()}, Nearby points: {len(nearby_points)}")

            # If there are nearby points, filter and split the line
            if nearby_points:
                try:
                    # Project points onto the line and sort them
                    projected_points = []
                    for point in nearby_points:
                        projected_point = line_geom.nearestPoint(
                            QgsGeometry.fromPointXY(point))
                        distance_along_line = line_geom.lineLocatePoint(projected_point)
                        projected_points.append(
                            (projected_point.asPoint(), distance_along_line))

                    sorted_points = sorted(projected_points, key=lambda x: x[1])

                    # Filter points based on minimum and maximum distance
                    filtered_points = []
                    last_point = None
                    for point, _ in sorted_points:
                        if last_point is None or min_distance <= distance_between_points(
                                last_point, point) <= max_distance:
                            filtered_points.append(point)
                            last_point = point

                    feedback.pushInfo(f"Filtered points: {len(filtered_points)}")

                    # Split the line
                    split_geoms = [line_geom]
                    for point in filtered_points:
                        new_split_geoms = []
                        for geom in split_geoms:
                            result, new_geometries, _ = geom.splitGeometry(
                                [point], False)
                            if result == 0:
                                new_split_geoms.append(geom)
                                if new_geometries:
                                    new_split_geoms.extend(new_geometries)
                            else:
                                new_split_geoms.append(geom)
                        split_geoms = new_split_geoms

                    feedback.pushInfo(f"Total split geometries: {len(split_geoms)}")

                    # Add the split geometries to the new layer
                    for split_geom in split_geoms:
                        new_feature = QgsFeature()
                        new_feature.setGeometry(split_geom)
                        new_feature.setAttributes(line_feature.attributes())
                        split_lines.addFeature(new_feature, QgsFeatureSink.FastInsert)
                except Exception as e:
                    feedback.reportError(f"Error splitting feature ID: {line_feature.id()}, Error: {str(e)}")
            else:
                # If no nearby points, add the original line to the new layer
                split_lines.addFeature(new_feature, QgsFeatureSink.FastInsert)


        return {self.OUTPUT: dest_id}

