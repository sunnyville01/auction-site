from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Item, Category, UserMessage, Activity, Profile


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'user', 'posted_on', 'status')
    search_fields = ('name', 'details')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'posted_on'
    ordering = ['status', 'posted_on']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'item',  'date')
    search_fields = ('UserMessage', 'from_user', 'to_user', 'item')
    date_hierarchy = 'date'
    ordering = ['-date']

class ProfileInline(admin.StackedInline):
    model = Profile
    # can_delete = False

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('item', 'user', 'date', 'change_type')
    date_hierarchy = 'date'
    ordering = ['-date']

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(Activity, ActivityAdmin)
