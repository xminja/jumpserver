# -*- coding: utf-8 -*-
#

from django.views.generic import ListView, UpdateView, DeleteView, DetailView, TemplateView
from django.views.generic.edit import SingleObjectMixin
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from users.utils import AdminUserRequiredMixin
from common.mixins import DatetimeSearchMixin
from ..models import Session, Command, Terminal
from ..backends import get_command_store
from .. import utils


__all__ = [
    'SessionOnlineListView', 'SessionOfflineListView',
    'SessionDetailView',
]

command_store = get_command_store()


class SessionListView(AdminUserRequiredMixin, DatetimeSearchMixin, ListView):
    model = Session
    template_name = 'terminal/session_list.html'
    context_object_name = 'session_list'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    user = asset = system_user = ''
    date_from = date_to = None

    def get_queryset(self):
        self.queryset = super().get_queryset()
        self.user = self.request.GET.get('user')
        self.asset = self.request.GET.get('asset')
        self.system_user = self.request.GET.get('system_user')

        filter_kwargs = dict()
        filter_kwargs['date_start__gt'] = self.date_from
        filter_kwargs['date_start__lt'] = self.date_to
        if self.user:
            filter_kwargs['user'] = self.user
        if self.asset:
            filter_kwargs['asset'] = self.asset
        if self.system_user:
            filter_kwargs['system_user'] = self.system_user
        if filter_kwargs:
            self.queryset = self.queryset.filter(**filter_kwargs)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'user_list': utils.get_user_list_from_cache(),
            'asset_list': utils.get_asset_list_from_cache(),
            'system_user_list': utils.get_system_user_list_from_cache(),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'user': self.user,
            'asset': self.asset,
            'system_user': self.system_user,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionOnlineListView(SessionListView):

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_finished=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Terminal'),
            'action': _('Session online list'),
            'now': timezone.now(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionOfflineListView(SessionListView):

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_finished=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Terminal'),
            'action': _('Session offline list'),
            'now': timezone.now(),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class SessionDetailView(SingleObjectMixin, ListView):
    template_name = 'terminal/session_detail.html'
    model = Session
    object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return command_store.filter(session=self.object.id)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Terminal'),
            'action': _('Session detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

