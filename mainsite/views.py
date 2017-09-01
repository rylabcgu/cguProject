from django.shortcuts import render, redirect
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from .models import *

# Create your views here.
def index(request):
	template = 'index.html'
	args = {}
	return render(request, template, args)

@receiver(email_confirmed)
def createProfile(request, email_address, **kwargs):
	user = User.objects.get(email=email_address.email)
	profile = Profile.objects.create(user=user)
	profile.save()


def email_confirmation_success(request):
	template = 'email_confirmation_success.html'
	args = {}
	return render(request, template, args)