from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import (
    CreateView, ListView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown


class BirthdayDeleteView(LoginRequiredMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Birthday, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BirthdayUpdateView(LoginRequiredMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Birthday, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BirthdayListView(ListView):
    model = Birthday
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    ordering = 'id'
    paginate_by = 10


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


@login_required
def add_comment(request, pk):
    birthday = get_object_or_404(Birthday, pk=pk)
    form = CongratulationForm(request.POST)
    if form.is_valid():
        congratulation = form.save(commit=False)
        congratulation.author = request.user
        congratulation.birthday = birthday
        congratulation.save()
    return redirect('birthday:detail', pk=pk)


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        context['form'] = CongratulationForm()
        context['congratulations'] = (
            self.object.congratulations.select_related('author')
        )
        return context
