from authentication import messages, constants
from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth import authenticate, login

from .forms import LoginForm, RegistrationForm


# Create your views here.

class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'register_form.html'

    def post(self, request, *args, **kwargs):
        context = {}
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.save()
            self.template_name = 'register_success.html'
        else:
            context.update({'form': form})

        return render(request, self.template_name, context)
