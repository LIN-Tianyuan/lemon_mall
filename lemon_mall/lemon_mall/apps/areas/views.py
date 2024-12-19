from django.shortcuts import render
from django.views import View
from django import http
import logging
from django.core.cache import cache

from areas.models import Area
from lemon_mall.utils.response_code import RETCODE
# Create your views here.

logger = logging.getLogger('django')


class AreasView(View):
    """Province city district linkage"""
    def get(self, request):
        # Determine whether the current query is for provincial data or urban data
        area_id = request.GET.get('area_id')
        if not area_id:
            # Get and determine if there is a cache
            province_list = cache.get('province_list')
            if not province_list:
                # Query provincial data
                # Area.objects.filter(Attribute Name__Conditional Expression=Value)
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)
                    # Need to convert model list to dictionary list
                    province_list = []
                    for province_model in province_model_list:
                        province_dict = {
                            'id': province_model.id,
                            'name': province_model.name
                        }
                        province_list.append(province_dict)
                    # Cache province dictionary list data: Stored by default in a configuration with the alias “default”.
                    cache.set('province_list', province_list, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Error in querying province data'})
            # Responding to Provincial JSON Data
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'province_list': province_list})
        else:
            # Determine if there is a cache
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                # Query city or county data
                try:
                    parent_model = Area.objects.get(id=area_id)
                    # sub_model_list = parent_model.area_set.all()
                    sub_model_list = parent_model.subs.all()
                    # Converting a list of sub-level models to a dictionary list
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            'id': sub_model.id,
                            'name': sub_model.name
                        }
                        subs.append(sub_dict)
                    # Constructing sub-level JSON data
                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs
                    }
                    # Cache City or District
                    cache.set('sub_area_' + area_id, sub_data, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'Query city or county data error'})
            # Responding to city or district JSON data
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'sub_data': sub_data})
