from django.conf.urls import patterns, include, url

urlpatterns = patterns('polls.views',
    url(r'^$',
        'poll_landing',
        name='polls_poll_landing'),
        
    url(r'^create/$',
        'poll_edit', 
        name='polls_poll_create'),
        
    url(r'^(?P<poll_id>\d+)/edit/$',
        'poll_edit',
        name='polls_poll_edit'),
        
    url(r'^(?P<poll_id>\d+)/$', 
        'ajax_poll_detail',
        name='polls_ajax_poll_detail'),
        
    url(r'^(?P<poll_id>\d+)/results/$', 
        'poll_results',
        name='polls_poll_results'),
        
    url(r'^(?P<poll_id>\d+)/report/$', 
        'poll_report',
        name='polls_poll_report'),
        
    url(r'^(?P<poll_id>\d+)/delete/$',
        'poll_delete',
        name='polls_poll_delete'),
        
    url(r'^(?P<poll_id>\d+)/reset/$',
        'poll_reset',
        name='polls_poll_reset'),  
        
    url(r'^(?P<poll_id>\d+)/export_csv/$',
        'poll_export_csv',
        name='polls_poll_export_csv'),
)