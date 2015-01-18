from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'aco_portfolio.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'portfolio.views.home', name='home'),
    url(r'^portfolio/', include('portfolio.urls')),
    url(r'^solution/', include('solution.urls')),
    url(r'^d3', 'portfolio.views.d3', name="d3"),

)
