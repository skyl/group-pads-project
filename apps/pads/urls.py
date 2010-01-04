from django.conf.urls.defaults import *

urlpatterns = patterns('pads.views',
    url(r'^new/$', 'new', name='pads_new'),
    # can get the pad with the user:
    url(r'^(?P<creator>[-\w]+)/(?P<slug>[-\w]+)/$', 'detail', name='pads_detail'),
    # or with the guid:
    url(r'^(?P<guid>[-\w]+)$', 'detail', name='pads_detail'),
    # add a pad TO a contenttype (group):
    url(r'^(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<id>\d+)/$',\
            view='add', name='pads_add'),
)
