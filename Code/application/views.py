from django.shortcuts import render, redirect
from django.http import HttpResponse
from application.models import *
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .serializers import enquiry_tableSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse

import requests
from django.shortcuts import render
from django.http import JsonResponse

from django.contrib.auth.models import User
import re


# Create your views here.

def home(request):
    return render(request, 'index.html')

def aboutus(request):
    
    return render(request, 'about.html')

def problem_statement(request):
    return render(request, 'problem-statement.html')

def reg(request):
    
    if request.method == "POST":
        a = request.POST.get('name')
        b = request.POST.get('email')
        c = request.POST.get('phone')
        d = request.POST.get('message')
        e = request.POST.get('dropdown')
        f = request.POST.get('education')
        g = request.POST.get('skills')
        enquiry = enquiry_table(name = a, email = b, phone = c, message = d, dropdown = e, education = f, skills = g)
        enquiry.save()

        messages.success(request, 'Enquiry Form Submitted Successfully...')

    return render(request, 'registration.html')


def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            
            login(request, user)
            request.session['username'] = username
            
            # Redirect to a success page.
            return redirect('dashboarddemo')
            
        else:
            # display 'invalid login' error message
            messages.error(request, 'In-correct username or password!..')
        
    
    return render(request, 'login.html')

@login_required(login_url='login')
def dashboard(request):

    # print('Hi, the User Name is: ',request.session.get('username_id'))

    username = request.session.get('username')

    return render(request, 'dashboard/index.html', {'username':username})

@login_required(login_url='login')
def enquiry_details(request):

    data = enquiry_table.objects.all()

    records = { 'abc':data }

    return render(request, 'dashboard/tables.html', records)

def delete_record(request, id):
    if request.method=='POST':
        data = enquiry_table.objects.get(pk=id)
        data.delete()
    return HttpResponseRedirect('/enquiry-details/')

def edit_record(request, id):
    info = enquiry_table.objects.filter(pk=id)
    
    data = {'abc':info}

    return render(request, 'dashboard/editrecord.html', data)

def update_record(request, id):
    info = enquiry_table.objects.get(pk=id)
    
    info.name = request.POST.get('name')
    info.email = request.POST.get('email')
    info.phone = request.POST.get('phone')
    info.education = request.POST.get('education')
    info.skills = request.POST.get('skills')
    info.message = request.POST.get('message')
    info.dropdown = request.POST.get('dropdown')
    info.date_field = request.POST.get('date')
    info.save()
    
    return HttpResponseRedirect('/enquiry-details/')

def logout_user(request):
    logout(request)
    return redirect('/')

def reports(request):

    data = None
    
    if request.method=='POST':

        # from date and to date store into variable from form field data.
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
     
        # Convert the date strings to datetime objects
        
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()


        # Fetch the data from the table based on the date range
        searchresult = enquiry_table.objects.filter(date_field__range=[from_date, to_date])

        data = {"abc":searchresult}
    
    return render(request, 'dashboard/reports.html', data)


class student_data(APIView):
    def get(self, request, format=None):
        data = enquiry_table.objects.all()
        serializer = enquiry_tableSerializer(data, many=True)
        return Response(serializer.data)


def add_location(request):
    
    if request.method == 'POST':
        a = request.POST.get('name')

        info = DropdownOption(name = a)
        info.save()

    return render(request, 'dashboard/add_location.html')


def dropdown_view(request):
    info = DropdownOption.objects.all()
    data = {'options': info}
    return render(request, 'contact.html', data)


def signup(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        surname = request.POST.get('surname')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Password match check
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        # Password strength validation
        # Import RE - This module provides regular expression matching operations similar to those found in Perl.
        # Regular expressions can contain both special and ordinary characters. Most ordinary characters, like "A", "a", or "0", are the simplest regular expressions;
        if (len(password) < 8 or
            not re.search(r'[A-Z]', password) or
            not re.search(r'[0-9]', password) or
            not re.search(r'[\W_]', password)):  # \W matches any non-alphanumeric character
            messages.error(
                request,
                'Password must be at least 8 characters long and include at least one uppercase letter, one number, and one symbol.'
            )
            return redirect('signup')

        myuser = User.objects.create_user(username, email, password)
        myuser.username = username
        
        myuser.save()

        messages.success(request, 'Congratulations, You are sign-up successfully, Now you can sign-in.. ')

        
    return render(request, 'signup.html')


def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        
        
        user = User.objects.get(username=request.user.username)
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('/change_password/')
        
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Your password was successfully updated!')
        return redirect('/change_password/')
    
    return render(request, 'dashboard/change_password.html')


def freelancer_login(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            
            login(request, user)
            request.session['username'] = username
            
            # Redirect to a success page.
            return redirect('freelancer_dashboard')
            
        else:
            # display 'invalid login' error message
            messages.error(request, 'In-correct username or password!..')
    
    return render(request, 'freelancer_login.html')


@login_required(login_url='freelancer_login')
def freelancer_dashboard(request):

    # print('Hi, the User Name is: ',request.session.get('username_id'))

    username = request.session.get('username')

    return render(request, 'dashboard/freelancer_index.html', {'username':username})


def freelancer_change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        
        
        user = User.objects.get(username=request.user.username)
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('/freelancer_change_password/')

        if new_password != confirm_new_password:
            messages.error(request, 'Passwords do not match')
            return redirect('/freelancer_change_password/')
        
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Your password was successfully updated!')
        return redirect('/freelancer_change_password/')
    
    return render(request, 'dashboard/freelancer_change_password.html')


def company_work(request):
    
    if request.method == "POST":
        a = request.POST.get('name')
        b = request.POST.get('address')
        c = request.POST.get('email')
        d = request.POST.get('phone')
        e = request.POST.get('requirement')
        f = request.POST.get('payment')
        enquiry = company_work_details(company_name = a, address = b, email = c, phone = d, requirement = e, payment = f)
        enquiry.save()

        messages.success(request, 'Company Work details Submitted Successfully...')

    return render(request, 'company_work_details.html')


@login_required(login_url='freelancer_login')
def freelancer_work_page(request):

    data = company_work_details.objects.all()

    records = { 'abc':data }

    return render(request, 'dashboard/freelancer_work_page.html', records)

@login_required(login_url='login')
def admin_work_page(request):

    data = company_work_details.objects.all()

    records = { 'abc':data }

    return render(request, 'dashboard/admin_work_page.html', records)


def company_login(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            
            login(request, user)
            request.session['username'] = username
            
            # Redirect to a success page.
            return redirect('company_dashboard')
            
        else:
            # display 'invalid login' error message
            messages.error(request, 'In-correct username or password!..')
    
    return render(request, 'company_login.html')


@login_required(login_url='company_login')
def company_dashboard(request):

    username = request.session.get('username')

    return render(request, 'dashboard/company_index.html', {'username':username})


@login_required(login_url='company_login')
def company_freelancer_details(request):

    data = enquiry_table.objects.all()

    records = { 'abc':data }

    return render(request, 'dashboard/company_freelancer_details.html', records)
