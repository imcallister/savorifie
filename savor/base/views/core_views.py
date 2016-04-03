import json
from collections import OrderedDict
import logging

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse


from accountifie.gl.models import Company
import accountifie.gl.api
import accountifie.toolkit.utils as utils

import base.apiv1

logger = logging.getLogger('default')



def get_resource(request, resource):
    api_method = getattr(base.apiv1, resource)
    qs = request.GET.copy()
    return HttpResponse(json.dumps(api_method(qs), cls=DjangoJSONEncoder), content_type="application/json")

def get_item(request, resource, item):
    api_method = getattr(base.apiv1, resource)
    qs = request.GET.copy()
    return HttpResponse(json.dumps(api_method(item, qs), cls=DjangoJSONEncoder), content_type="application/json")


def company_context(request):
    """Context processor referenced in settings.
    This puts the current company ID into any request context, 
    thus allowing templates to refer to it

    This is not a view.
    """
    
    company_id = utils.get_company(request)
    data = {'company_id': company_id, 'logo': settings.LOGO, 'site_title': settings.SITE_TITLE}
    data['admin_site_title'] = settings.SITE_TITLE
    data['company_color'] = accountifie.gl.api.get_company_color({'company_id': company_id})
    
    data['menu_items'] = OrderedDict([('Reports', "/reports/"),
                                     ('Daily', "/daily/"),
                                     ('Inventory', '/inventory'),
                                     ('Forecasting', '/forecasts'),
                                     ('Snapshots', '/snapshot/glsnapshots')
                                    ])

    data['company_list'] = [x['id'] for x in accountifie.gl.api.companies({})]
    
    if company_id:
        try:
            company = Company.objects.get(pk=company_id)
            data.update({'company':company})
        except Company.DoesNotExist:
            pass 
    return data




    
