from django.contrib.sitemaps import Sitemap
from django.db.models import Q

from .models import Item

class ItemSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Item.objects.filter(
                Q(status='available') | Q(status='awaiting')
            )
