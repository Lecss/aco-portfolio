from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'toYou.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'solution.views.get_solution', name='solution'),
    url(r'^get_graph', 'solution.views.get_graph', name="get_graph"),
)