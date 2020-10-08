""" Common models """
import os

from django.contrib.gis.db import models
# Utilities
from scooter.utils.models.scooter import ScooterModel
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, WKTWriter


class Area(ScooterModel):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True)


class Zone(ScooterModel):
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    poly = models.GeometryField(blank=True, null=True, geography=True)
    area = models.ForeignKey(Area, on_delete=models.DO_NOTHING)


def run(verbose=True):
    kml_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '', 'tehuacan.kml'),
    )
    wkt_w = WKTWriter()
    source = DataSource(kml_file)
    for layer in source:
        for feat in layer:
            # Get the feature geometry.
            geom = feat.geom
            poly = GEOSGeometry(wkt_w.write(geom.geos))
            area, created = Area.objects.get_or_create(
                name="Tehuacán",
                description="Ciudad de tehuacán"
            )
            area.poly = poly
            area.save()
            # line = Line.objects.create(
            #     name=property['name'],
            #     description=property['description'],
            #     layer_name=feat.layer_name,
            #     # Make a GeosGeometry object
            #     geom=GEOSGeometry(wkt_w.write(geom.geos)),
            # )
