from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Count, Avg, Min, Max, Sum

from cities.models import City
from regions.models import Region
from hotels.models import Hotel
from .serializers import CitySerializer, RegionSerializer, HotelSerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.all()

        population_min = self.request.query_params.get('population_min')
        population_max = self.request.query_params.get('population_max')
        if population_min:
            queryset = queryset.filter(population__gte=population_min)
        if population_max:
            queryset = queryset.filter(population__lte=population_max)

        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)

        city_type = self.request.query_params.get('city_type')
        if city_type:
            queryset = queryset.filter(city_type=city_type)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        features = []
        for item in serializer.data:
            if item.get('geometry'):
                features.append({
                    "type": "Feature",
                    "geometry": item['geometry'],
                    "properties": {k: v for k, v in item.items() if k != 'geometry'}
                })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        return Response(geojson)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        distance_km = request.query_params.get('distance', 50)

        if not lat or not lng:
            return Response(
                {'error': 'lat and lng parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            point = Point(float(lng), float(lat), srid=4326)
            distance_m = float(distance_km) * 1000

            nearby_cities = City.objects.filter(
                location__distance_lte=(point, distance_m)
            ).annotate(
                distance=Distance('location', point)
            ).order_by('distance')

            serializer = self.get_serializer(nearby_cities, many=True)
            
            features = []
            for item in serializer.data:
                if item.get('geometry'):
                    features.append({
                        "type": "Feature",
                        "geometry": item['geometry'],
                        "properties": {k: v for k, v in item.items() if k != 'geometry'}
                    })

            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            return Response(geojson)

        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinates or distance'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def get_queryset(self):
        queryset = Region.objects.all()

        area_min = self.request.query_params.get('area_min')
        area_max = self.request.query_params.get('area_max')
        if area_min:
            queryset = queryset.filter(area_km2__gte=area_min)
        if area_max:
            queryset = queryset.filter(area_km2__lte=area_max)

        population_min = self.request.query_params.get('population_min')
        population_max = self.request.query_params.get('population_max')
        if population_min:
            queryset = queryset.filter(total_population__gte=population_min)
        if population_max:
            queryset = queryset.filter(total_population__lte=population_max)

        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)

        region_type = self.request.query_params.get('region_type')
        if region_type:
            queryset = queryset.filter(region_type=region_type)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        features = []
        for item in serializer.data:
            if item.get('geometry'):
                features.append({
                    "type": "Feature",
                    "geometry": item['geometry'],
                    "properties": {k: v for k, v in item.items() if k != 'geometry'}
                })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        return Response(geojson)

    @action(detail=True, methods=['get'])
    def cities(self, request, pk=None):
        """Get all cities within a region using PostGIS ST_Within spatial query"""
        region = self.get_object()
        cities_in_region = City.objects.filter(location__within=region.geometry)
        
        serializer = CitySerializer(cities_in_region, many=True)
        
        features = []
        for item in serializer.data:
            if item.get('geometry'):
                features.append({
                    "type": "Feature",
                    "geometry": item['geometry'],
                    "properties": {k: v for k, v in item.items() if k != 'geometry'}
                })

        return Response({
            "type": "FeatureCollection",
            "features": features,
            "region_info": {
                "name": region.name,
                "country": region.country,
                "total_cities": len(features)
            }
        })


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_queryset(self):
        queryset = Hotel.objects.all()

        city_name = self.request.query_params.get('city')
        if city_name:
            queryset = queryset.filter(city__name__icontains=city_name)

        star_rating = self.request.query_params.get('star_rating')
        if star_rating:
            queryset = queryset.filter(star_rating=star_rating)

        price_range = self.request.query_params.get('price_range')
        if price_range:
            queryset = queryset.filter(price_range=price_range)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        features = []
        for item in serializer.data:
            if item.get('geometry'):
                features.append({
                    "type": "Feature",
                    "geometry": item['geometry'],
                    "properties": {k: v for k, v in item.items() if k != 'geometry'}
                })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        return Response(geojson)
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find hotels near a location"""
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 50))  # km
            
            point = Point(lng, lat, srid=4326)
            
            # Convert radius to meters
            radius_m = radius * 1000
            
            hotels = Hotel.objects.annotate(
                distance=Distance('location', point)
            ).filter(
                distance__lte=radius_m
            ).order_by('distance')
            
            serializer = self.get_serializer(hotels, many=True)
            
            features = []
            for item in serializer.data:
                if item.get('geometry'):
                    features.append({
                        "type": "Feature",
                        "geometry": item['geometry'],
                        "properties": {k: v for k, v in item.items() if k != 'geometry'}
                    })
            
            return Response({
                "type": "FeatureCollection",
                "features": features
            })
        except (ValueError, TypeError) as e:
            return Response(
                {"error": "Invalid parameters. Provide lat, lng, and radius (optional)"},
                status=400
            )
