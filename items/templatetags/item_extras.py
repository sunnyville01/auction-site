from datetime import datetime,timedelta
from django import template
from django.db.models import Q, Count

from items import models


register = template.Library()

@register.inclusion_tag('items/tags/hero_search.html')
def hero_search():
    ''' Displays Search Bar common in many views '''
    return

@register.inclusion_tag('items/tags/hero_search_bg.html')
def hero_search_bg():
    ''' Displays Search Bar with Bg Image common in few views '''
    return

@register.inclusion_tag('items/tags/item_archive.html', takes_context=True)
def item_archive(context):
    ''' Shows List of Items on Archive Pages '''
    return {
        'page_obj': context['page_obj'],
        'item_list': context['item_list'],
        'paginator': context['paginator'],
        'is_paginated': context['is_paginated'],
        'MEDIA_URL': context['MEDIA_URL'],
    }

@register.simple_tag(takes_context=True)
def unread_messages(context):
    ''' Checks if there are any unread messages '''
    request = context['request']
    user_profile = models.Profile.objects.get(user=request.user)

    last_message_check = user_profile.last_message_check

    # Messages
    user_messages = models.UserMessage.objects.filter(
        Q(to_user=request.user) | Q(from_user=request.user)
    ).order_by('-id')

    if len(user_messages) > 0:
        last_message = user_messages[0]
    else:
        last_message = None

    if last_message_check is not None and last_message is not None:
        if last_message.date > last_message_check:
            return '<span class="gia-top-bar-messages unread">'

    return '<span class="gia-top-bar-messages">'

@register.inclusion_tag('items/tags/categories_list.html')
def categories_list():
    categories = models.Category.objects.all()[:5]

    ''' Shows List of Categories '''
    return {
        'categories': categories,
    }
