from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from .models import Company
from .forms import CompanyForm

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'companies/list.html'
    context_object_name = 'companies'

class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/edit.html'
    success_url = reverse_lazy('company_list')

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'companies/edit.html'
    success_url = reverse_lazy('company_list')

class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'companies/confirm_delete.html'
    success_url = reverse_lazy('company_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return redirect(self.success_url)
        except ProtectedError:
            return render(request, self.template_name, {
                'object': self.object,
                'error': 'This company cannot be deleted because it is referenced by other records.'
            })