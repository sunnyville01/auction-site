from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap

from .sitemaps import ItemSitemap
from . import views

sitemaps = {
    'items': ItemSitemap()
}

urlpatterns = [

    # Sitemap
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Messages Actions
    url(r'^action/request-item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.RequestItemView.as_view(), name='request'),
    url(r'^action/offer-item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.OfferItemView.as_view(), name='offer'),
    url(r'^action/ask-question/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.AskQuestionView.as_view(), name='ask'),
    url(r'^action/reply/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.ReplyView.as_view(), name='reply'),
    url(r'^action/report-item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.ReportItemView.as_view(), name='report'),

    # Item CRUD Actions
    url(r'^action/create-item/$', views.ItemCreateView.as_view(), name='create'),
    url(r'^action/update-item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.ItemUpdateView.as_view(), name='update'),
    url(r'^action/delete-item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.ItemDeleteView.as_view(), name='delete'),

    # Item Completion Process
    url(r'^action/choose-user/(?P<pk>\d+)/(?P<username>[\w-]+)/$', views.ChooseUserView.as_view(), name='choose_user'),
    url(r'^action/make-available/(?P<pk>\d+)/$', views.MakeAvailableView.as_view(), name='make_available'),

    # Categories Views
    url(r'^item/category/(?P<pk>\d+)/(?P<slug>[\w-]+)/wanted-items/$', views.CategoryItemsWantedView.as_view(), name='category_items_wanted'),
    url(r'^item/category/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.CategoryItemsView.as_view(), name='category_items'),

    # Profile View
    url(r'^user/(?P<username>\w+)/wanted/$', views.ProfileWantedView.as_view(), name='profile_wanted'),
    url(r'^user/(?P<username>\w+)/$', views.ProfileView.as_view(), name='profile'),

    # Tos
    url(r'^tos/$', views.TosTemplateView.as_view(), name='tos'),

    # Generic Views
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^messages/$', views.profile_messages, name='profile_messages'),
    url(r'^item/(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.ItemDetailView.as_view(), name='detail'),
    url(r'^wanted-items/$', views.ItemWantedListView.as_view(), name='home_wanted'),
    url(r'^$', views.ItemListView.as_view(), name='home'),
]
