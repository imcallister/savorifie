import json
from collections import OrderedDict
import logging

from django.conf import settings

from accountifie.gl.models import Company
import accountifie.toolkit.utils as utils
from accountifie.common.api import api_func


logger = logging.getLogger('default')


def company_context(request):
    """Context processor referenced in settings.
    This puts the current company ID into any request context, 
    thus allowing templates to refer to it

    This is not a view.
    """

    company_id = utils.get_company(request)
    data = {'company_id': company_id,
            'logo': settings.LOGO,
            'site_title': settings.SITE_TITLE}

    data['admin_site_title'] = settings.SITE_TITLE
    data['DJANGO_18'] = settings.DJANGO_18
    data['DJANGO_19'] = settings.DJANGO_19

    data['company_color'] = api_func('gl', 'company', company_id)['color_code']

    data['menu_items'] = OrderedDict([('Reports', "/reports/"),
                                     ('Daily', "/daily/"),
                                     ('Inventory', '/inventory'),
                                     ('Snapshots', '/snapshot/glsnapshots')
                                      ])

    data['power_menu_items'] = OrderedDict([('Admin', "/admin/"),
                                            ('Maintenance', "/admin/"),
                                            ('Dashboard', "/dashboard/"),
                                            ('Logs', "/dashboard/logs/")
                                            ])

    data['company_list'] = [x['id'] for x in api_func('gl', 'company')]

    if company_id:
        try:
            company = Company.objects.get(pk=company_id)
            data.update({'company':company})
        except Company.DoesNotExist:
            pass
    return data
