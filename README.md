## savorifie

An example accounting application using projects open sourced by [electronifie] (http://www.electronifie.com).
- [accountifie](https://github.com/electronifie/accountifie): containes core django app to configure General Ledger, reporting and interface to the GL.
- [financifie-svc](https://github.com/electronifie/financifie-svc): node application to create GL entries and manage querying

The original work was performed with [reportlab] (http://www.reportlab.com) using Andy Robinson's doubletalk app and now incorporating pieces of Reportlab's core docengine code, generously included by them.
The financifie-svc code was developed by Andrew McKenzie at electronifie.

### Setup

#### django app

1. Clone this repo.
2. Create virtualenv
3. activate virtualenv
4. pip install -r requirements.txt    --- included in here will be the accountifie django package
5. /update_dev_environment
6. ./manage.py runserver    -- you should have a working django app now with the basics

#### financifie service

1. Need node and mongo (see ansible scripts --- coming soon)
2. Clone financifie service
3. Configure port number
4. make run
 
The FINANCIFIE_SVC_URL needs to be configured in the django app (/admin/environment/variable/).
