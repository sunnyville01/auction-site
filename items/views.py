from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    View, ListView, DetailView,
    TemplateView, CreateView, UpdateView,
    DeleteView, FormView,
)

from . import models
from . import forms
from . import mixins


class MakeAvailableView(LoginRequiredMixin, mixins.DenyNonAuthorMixin, UpdateView):
    model = models.Item
    fields = ['status',]
    template_name = 'items/make_available.html'

    @transaction.atomic
    def form_valid(self, form):

        form.instance.status = 'available'
        form.instance.completed_with = None

        # Add a record in Activity
        models.Activity.objects.create(item=form.instance, user=None, change_type='available')

        return super().form_valid(form)


class ChooseUserView(LoginRequiredMixin, mixins.DenyNonAuthorMixin, UpdateView):
    form_class = forms.ChooseUserForm
    template_name = 'items/choose_user.html'
    model = models.Item

    @transaction.atomic
    def form_valid(self, form):

        # Mark Item as completed along with the user
        username=self.kwargs['username']
        completed_with = User.objects.get(username=username)
        form.instance.completed_with = completed_with

        # Get Submitted Value
        status = form.cleaned_data['status']

        # Add a record in Activity
        models.Activity.objects.create(item=form.instance, user=completed_with, change_type=status)

        return super().form_valid(form)


class ItemListView(ListView):
    queryset = models.Item.objects.filter(
        Q(post_type='free') & ( Q(status='available') | Q(status='awaiting'))
    )
    paginate_by = 12


class ItemWantedListView(ListView):
    template_name = "items/item_wanted_list.html"
    queryset = models.Item.objects.filter(
        Q(post_type='wanted') & Q(status='available')
    )
    paginate_by = 12


class ItemDetailView(DetailView):
    model = models.Item

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        item_user = models.Item.objects.values_list('user', flat=True).get(pk=self.kwargs['pk'])

        free_items_count = models.Item.objects.filter(user=item_user).filter(post_type='free').filter(status='completed').count()
        wanted_items_count = models.Item.objects.filter(user=item_user).filter(post_type='wanted').filter(status='completed').count()

        context['free_items_count'] = free_items_count
        context['wanted_items_count'] = wanted_items_count

        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = models.Item
    form_class = forms.ItemCreateForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ItemCreateView, self).get_context_data(**kwargs)

        context['page_title'] = 'Create New Item'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ItemUpdateView(LoginRequiredMixin, mixins.DenyNonAuthorMixin, UpdateView):
    model = models.Item
    form_class = forms.ItemCreateForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ItemUpdateView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        item_name = self.object.name

        context['page_title'] = 'Update ' + item_name.title()
        return context


class ItemDeleteView(LoginRequiredMixin, mixins.DenyNonAuthorMixin, DeleteView):
    model = models.Item
    success_url = reverse_lazy("items:home")


class RequestItemView(LoginRequiredMixin, CreateView):
    model = models.Item
    form_class = forms.RequestForm
    template_name = 'items/messages/request_item.html'
    success_url = reverse_lazy("items:profile_messages")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user:
            messages.add_message(self.request, messages.WARNING, 'Action not allowed.')
            return HttpResponseRedirect(reverse('items:home'))
        return super(RequestItemView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(RequestItemView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        context['item_name'] = item.name
        context['to_user'] = item.user
        context['from_user'] = self.request.user

        return context

    def form_valid(self, form):

        # self.args[0]
        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        item_name = item.name
        to_user = item.user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'request'

        # Send email if User has enabled it
        email_subject = 'Request for your offered item: {}'.format(item_name)
        email_body = 'The user: {} has requested for your offered item: {}, with the following message:\r\n\r\n'.format(self.request.user.username, item_name.title())

        if form.cleaned_data['pickup_time']:
            email_body = email_body + 'Pickup Time:\r\n{}\r\n\r\nMessage:\r\n{}'.format(form.cleaned_data['pickup_time'], form.cleaned_data['message'])
        else:
            email_body = email_body +  'Message:\r\n{}'.format(form.cleaned_data['message'])
        email_body = email_body + '\r\n\r\nPlease visit: http://127.0.0.1:8000/messages/ to view your messages.\r\nThank you for using the site!\r\n - AuctionSite team.'
        # Send it
        send_mail(
            email_subject,
            email_body,
            'AuctionSite <noreply@auctionsite.com>', # From
            [to_user.email,] #To
        )

        # Add a record in Activity
        models.Activity.objects.create(item=item, user=self.request.user, change_type='requested')
        messages.add_message(self.request, messages.SUCCESS, 'Your message of the request has been sent.')

        return super().form_valid(form)


class OfferItemView(LoginRequiredMixin, CreateView):
    model = models.Item
    form_class = forms.OfferForm
    template_name = 'items/messages/request_item.html'
    success_url = reverse_lazy("items:profile_messages")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user:
            messages.add_message(self.request, messages.WARNING, 'Action not allowed.')
            return HttpResponseRedirect(reverse('items:home'))
        return super(OfferItemView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(OfferItemView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        context['item_name'] = item.name
        context['to_user'] = item.user
        context['from_user'] = self.request.user

        return context

    def form_valid(self, form):

        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        item_name = item.name
        to_user = item.user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'offer'

        # Send email
        email_subject = 'Offer for your requested item: {}'.format(item_name)
        email_body = 'The user: {} has offered your requested item: {}, with the following message:\r\n\r\n'.format(self.request.user.username, item_name)
        email_body = email_body +  'Message:\r\n{}'.format(form.cleaned_data['message'])
        email_body = email_body + '\r\n\r\nPlease visit: http://127.0.0.1:8000/messages/ to view your messages.\r\nThank you for using the site!\r\n - AuctionSite team.'
        # Send it
        send_mail(
            email_subject,
            email_body,
            'AuctionSite <noreply@auctionsite.com>', # From
            [to_user.email,] #To
        )

        # Add a record in Activity
        models.Activity.objects.create(item=item, user=self.request.user, change_type='offered')

        # Show a popup message
        messages.add_message(self.request, messages.SUCCESS, 'Your message of the offer has been sent.')

        return super().form_valid(form)


class ReplyView(LoginRequiredMixin, CreateView):
    form_class = forms.ReplyForm
    template_name = 'items/messages/reply.html'
    success_url = reverse_lazy("items:profile_messages")

    def dispatch(self, request, *args, **kwargs):
        original_message = get_object_or_404(models.UserMessage, pk=self.kwargs['pk'])
        item = original_message.item
        from_user = original_message.from_user
        to_user = original_message.to_user

        if from_user == request.user or to_user != request.user:
            messages.add_message(self.request, messages.WARNING, 'Action not allowed.')
            return HttpResponseRedirect(reverse('items:home'))
        return super(ReplyView, self).dispatch(
            request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReplyView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        original_message = get_object_or_404(models.UserMessage, pk=self.kwargs['pk'])
        item = original_message.item

        context['original_message'] = original_message.message
        context['item_name'] = item.name
        context['to_user'] = original_message.from_user
        context['from_user'] = self.request.user

        return context

    def form_valid(self, form):

        # self.args[0]
        original_message = get_object_or_404(models.UserMessage, pk=self.kwargs['pk'])

        item = original_message.item
        item_name = item.name
        to_user = original_message.from_user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.related_to = original_message
        form.instance.from_user = self.request.user
        form.instance.tag = 'reply'

        # Send email
        email_subject = '{} has replied to your message'.format(self.request.user.username)
        email_body = 'The user: {} has replied to your message regarding the item: {}.\r\n\r\n'.format(self.request.user.username, item_name)
        email_body = email_body +  'Your message:\r\n{}\r\n\r\n'.format(original_message.message)
        email_body = email_body +  'Reply:\r\n{}'.format(form.cleaned_data['message'])
        email_body = email_body + '\r\n\r\nPlease visit: http://127.0.0.1:8000/messages/ to view your messages.\r\nThank you for using the site!\r\n - AuctionSite team.'
        # Send it
        send_mail(
            email_subject,
            email_body,
            'AuctionSite <noreply@auctionsite.com>', # From
            [to_user.email,] #To
        )

        # Show popup Message
        messages.add_message(self.request, messages.SUCCESS, 'Your message has been sent.')

        return super().form_valid(form)


class AskQuestionView(LoginRequiredMixin, CreateView):
    model = models.UserMessage
    form_class = forms.AskQuestionForm
    template_name = 'items/messages/request_item.html'
    success_url = reverse_lazy("items:profile_messages")

    def dispatch(self, request, *args, **kwargs):
        item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        author = item.user

        if author == request.user:
            messages.add_message(self.request, messages.WARNING, 'Action not allowed.')
            return HttpResponseRedirect(reverse('items:home'))
        return super(AskQuestionView, self).dispatch(
            request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AskQuestionView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        context['item_name'] = item.name
        context['to_user'] = item.user
        context['from_user'] = self.request.user

        return context

    def form_valid(self, form):

        # self.args[0]
        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        item_name = item.name
        to_user = item.user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'question'

        # Send email
        email_subject = 'Question for your offered item: {}'.format(item_name)
        email_body = 'The user: {} has asked a question regarding your offered item: {}:\r\n\r\n'.format(self.request.user.username, item_name)

        email_body = email_body + 'Question message:\r\n{}'.format(form.cleaned_data['message'])
        email_body = email_body + '\r\n\r\nPlease visit: http://127.0.0.1:8000/messages/ to view your messages.\r\nThank you for using the site!\r\n - AuctionSite team.'
        # Send it
        send_mail(
            email_subject,
            email_body,
            'AuctionSite <noreply@auctionsite.com>', # From
            [to_user.email,] #To
        )

        # Show popup message
        messages.add_message(self.request, messages.SUCCESS, 'Your message has been sent.')

        return super().form_valid(form)


class ReportItemView(LoginRequiredMixin, CreateView):
    form_class = forms.ReportItemForm
    template_name = 'items/messages/report.html'
    success_url = reverse_lazy("items:profile_messages")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ReportItemView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        item = get_object_or_404(models.Item, pk=self.kwargs['pk'])
        context['item_name'] = item.name
        context['from_user'] = self.request.user

        return context

    def form_valid(self, form):

        # self.args[0]
        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        to_user = get_object_or_404(models.User, username='admin')

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'report'

        messages.add_message(self.request, messages.SUCCESS, 'Thank you for helping the community!')

        return super().form_valid(form)


class CategoryItemsView(ListView):
    """Displays a list of Items in a Category"""
    model = models.Item
    template_name = "items/category_items.html"
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        return  models.Item.objects.filter(category__pk = self.kwargs['pk']).filter(post_type = 'free')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryItemsView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        category = get_object_or_404(models.Category, pk=self.kwargs['pk'])
        context['category'] = category

        return context


class CategoryItemsWantedView(ListView):
    """Displays a list of Wanted Items in a Category"""
    model = models.Item
    template_name = "items/category_items_wanted.html"
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        return  models.Item.objects.filter(category__pk = self.kwargs['pk']).filter(post_type = 'wanted')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CategoryItemsWantedView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        category = get_object_or_404(models.Category, pk=self.kwargs['pk'])
        context['category'] = category

        return context


class ProfileView(ListView):
    model = models.Item
    template_name = "items/user_profile.html"
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        return  models.Item.objects.filter(user__username = self.kwargs['username']).filter(post_type = 'free')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        profile_user = get_object_or_404(User, username=self.kwargs['username'])

        free_items_count = models.Item.objects.filter(user=profile_user).filter(post_type='free').filter(status='completed').count()
        wanted_items_count = models.Item.objects.filter(user=profile_user).filter(post_type='wanted').filter(status='completed').count()

        context['profile_user'] = profile_user
        context['free_items_count'] = free_items_count
        context['wanted_items_count'] = wanted_items_count

        return context

    def form_valid(self, form):

        # self.args[0]
        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        to_user = item.user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'request'

        messages.add_message(self.request, messages.SUCCESS, 'Your message of the request has been sent.')

        return super().form_valid(form)


class ProfileWantedView(ListView):
    model = models.Item
    template_name = "items/user_profile_wanted.html"
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        return  models.Item.objects.filter(user__username = self.kwargs['username']).filter(post_type = 'wanted')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileWantedView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        profile_user = get_object_or_404(User, username=self.kwargs['username'])

        free_items_count = models.Item.objects.filter(user=profile_user).filter(post_type='free').filter(status='completed').count()
        wanted_items_count = models.Item.objects.filter(user=profile_user).filter(post_type='wanted').filter(status='completed').count()

        context['profile_user'] = profile_user
        context['free_items_count'] = free_items_count
        context['wanted_items_count'] = wanted_items_count

        return context

    def form_valid(self, form):

        # self.args[0]
        item_pk = self.kwargs['pk']
        item = get_object_or_404(models.Item, pk=item_pk)
        to_user = item.user

        form.instance.item = item
        form.instance.to_user = to_user
        form.instance.from_user = self.request.user
        form.instance.tag = 'request'

        messages.add_message(self.request, messages.SUCCESS, 'Your message of the request has been sent.')

        return super().form_valid(form)


class TosTemplateView(TemplateView):
    template_name = "tos.html"


@login_required
@transaction.atomic
def dashboard(request):

    # Items Giving and Wanted
    items_giving = models.Item.objects.filter(user=request.user).filter(post_type='free')
    items_wanted = models.Item.objects.filter(user=request.user).filter(post_type='wanted')
    items_completed = models.Item.objects.filter(user=request.user).filter(post_type='completed')

    # Item Offered
    items_offered = models.Item.objects.filter(activity__user=request.user, activity__change_type='offered').distinct()

    # Items Requested
    items_requested = models.Item.objects.filter(activity__user=request.user, activity__change_type='requested').distinct()

    # Items Count
    free_items_count = models.Item.objects.filter(user=request.user).filter(post_type='free').filter(status='completed').count()
    wanted_items_count = models.Item.objects.filter(user=request.user).filter(post_type='wanted').filter(status='completed').count()

    # User Settings Form
    if request.method == 'POST':

        user_form = forms.UserForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('items:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = forms.UserForm(instance=request.user)

    return render(request, 'items/dashboard.html', {
        'user_form': user_form,
        'items_giving': items_giving,
        'items_wanted': items_wanted,
        'items_offered': items_offered,
        'items_requested': items_requested,
        'items_completed': items_completed,
        'free_items_count': free_items_count,
        'wanted_items_count': wanted_items_count,
    })


@login_required
def profile_messages(request):

    # Messages
    user_messages_to = models.UserMessage.objects.filter(to_user=request.user)
    user_messages_from = models.UserMessage.objects.filter(from_user=request.user)

    # Add a record in Activity
    models.Profile.objects.filter(user=request.user).update(last_message_check=timezone.now())

    # User Settings Form
    return render(request, 'items/messages/profile_messages.html', {
        'inbox_messages': user_messages_to,
        'sent_messages': user_messages_from,
    })
