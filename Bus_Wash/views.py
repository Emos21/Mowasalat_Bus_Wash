from django.shortcuts import render

# Create your views here.
from multiprocessing import context
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views import View
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import *
from .forms import *
from .decorators import *
from . import models, forms
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from collections import defaultdict
from django.db.models import Sum
from datetime import timedelta, date, datetime
from django.core.mail import EmailMessage, send_mail
import pytz
import math
from django.template.loader import render_to_string
import os
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  
from .logo import getLogoBase64
import cv2
import base64



@login_required
def profile(request):
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile is updated successfully")
            return redirect(to="profile")
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(
        request,
        "dashboard/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = "dashboard/profile.html"
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy("profile")


@login_required
@allowed_users(allowed_roles=["Level1"])
def HomeDashboard(request):
    damagenotifications = WorkDoneDamages.objects.all().count()
    totalsites = 0
    totaltask = Task.objects.all().count()
    totaltsites = Site.objects.all().count()
    totaltlocations = Location.objects.all().count()

    context = {
        "damagenotifications": damagenotifications,
        "totalsites": totalsites,
        "totaltask": totaltask,
        "totaltsites": totaltsites,
        "totaltlocations": totaltlocations,
    }

    return render(request, "dashboard/dashboard.html", context)


def context_data():
    context = {
        "page_name": "",
        "page_title": "Chat Room",
        "system_name": "Qr Code Bus Wash",
        "topbar": True,
    }

    return context


@unauthenticated_user
def login_page(request):
    return render(request, "auth/login.html")


def login_user(request):
    logout(request)
    resp = {"status": "failed", "msg": ""}
    username = ""
    password = ""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp["status"] = "success"
            else:
                resp["msg"] = "Incorrect username or password"
        else:
            resp["msg"] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type="application/json")


def logout_user(request):
    logout(request)
    return redirect("login-page")


@login_required
def site_list(request):
    context = context_data()
    context["page"] = "employee_list"
    context["page_title"] = "Employee List"
    context["employees"] = models.Site.objects.all().order_by("-date_added")

    return render(request, "site_list.html", context)


# @login_required
# def managesite(request, pk=None):
#     context = context_data()
#     if pk is None:
#         context["page"] = "add_employee"
#         context["page_title"] = "Add New Employee"
#         context["employee"] = {}
#     else:

#         context["employee"] = models.Site.objects.get(id=pk)

#     return render(request, "manage-task.html", context)


# @login_required
# def save_employee(request):
#     resp = {"status": "failed", "msg": ""}
#     if not request.method == "POST":
#         resp["msg"] = "No data has been sent into the request."

#     else:
#         if request.POST["id"] == "":
#             form = forms.CreateNewSite(request.POST, request.FILES)
#         else:
#             employee = models.Site.objects.get(id=request.POST["id"])
#             form = forms.CreateNewSite(request.POST, request.FILES, instance=employee)
#         if form.is_valid():
#             form.save()
#             if request.POST["id"] == "":
#                 messages.success(
#                     request,
#                     f"{request.POST['site_code']} has been added successfully.",
#                 )
#             else:
#                 messages.success(
#                     request,
#                     f"{request.POST['site_code']} has been updated successfully.",
#                 )
#             resp["status"] = "success"
#         else:
#             for field in form:
#                 for error in field.errors:
#                     if not resp["msg"] == "":
#                         resp["msg"] += str("<br />")
#                     resp["msg"] += str(f"[{field.label}] {error}")

#     return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_card(request, pk=None):
    if pk is None:
        return HttpResponse("Invalid QR")
    else:
        context = context_data()
        context["employee"] = models.Site.objects.get(id=pk)
        return render(request, "view_id.html", context)


@login_required
def view_scanner(request, task_id=0):
    context = context_data()
    context["task_id"] = task_id
    return render(request, "scanner.html", context)


@login_required
def view_details(request, code=None, task_id=0):
    if code is None:
        return HttpResponse("Qr Invalid")
    else:
        site = models.Site.objects.get(site_code=code)
        print(task_id)
        if task_id > 0:
            task = Task.objects.get(id=task_id)
            task.site_id = site
            task.is_scanned = True
            task.save()
        context = context_data()
        context["task"] = task_id
        context["employee"] = site
        return render(request, "view_details.html", context)


# @login_required
# def delete_employee(request, pk=None):
#     resp = {"status": "failed", "msg": ""}
#     if pk is None:
#         resp["msg"] = "No data has been sent into the request."
#     else:
#         try:
#             models.Site.objects.get(id=pk).delete()
#             resp["status"] = "success"
#             messages.success(request, "Employee has been deleted successfully.")
#         except:
#             resp["msg"] = "Employee has failed to delete."

#     return HttpResponse(json.dumps(resp), content_type="application/json")


def sendmailHtml(subject, html_body, to_email):
    body = ""
    res = send_mail(
        subject,
        body,
        "emosmwangi@gmail.com",
        [to_email],
        html_message=html_body,
        fail_silently=False,
    )
    return res


######### TASK #########


@login_required
def new(request):
    new_task = Site.objects.all()
    shelter_types = Configurations.objects.filter(config_type="shelter_type")
    
    users = User.objects.filter(is_staff=False)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            try:

                form.save()
                return redirect("/show_tasks")
            except:
                pass
    else:
        form = TaskForm()
    return render(
        request,
        "task/add_task.html",
        {"form": form, "new_task": new_task, "users": users, "shelter_types": shelter_types},
    )


@login_required
def show_tasks(request, status=False):
    if status:
        tasks = (
            Task.objects.filter(user__id=request.user.id)
            if request.user.is_superuser == False
            else Task.objects.all().order_by("-createdat")
        )
    else:
        tasks = (
            Task.objects.filter(user__id=request.user.id, createdat__gte=datetime.now())
            if request.user.is_superuser == False
            else Task.objects.filter(createdat__gte=datetime.now())
        )
    return render(request, "task/show_tasks.html", {"tasks": tasks})


# show edit task page
@login_required
def edit_task(request, id):

    task = Task.objects.get(id=id)
    # task.is_scanned = False
    # task.save()
    type_wash = (
        TypeofWash.objects.filter(location__id=task.site_id.location.id)
        if task.is_scanned
        else []
    )
    total_odo = (
        task.odometerafter - task.odometerbefore
        if task.odometerbefore and task.odometerafter
        else "-"
    )

    damages = Configurations.objects.filter(config_type='damages')
    damage_data = WorkDoneDamages.objects.filter(task_id = id)
    

    return render(
        request,
        "task/edit_task.html",
        {"task": task, "total_odo": total_odo, "type_wash": type_wash, "damages":damages,'damage_data':damage_data},
    )


# def update_task(request, id):
#     tasks = Task.objects.get(id=id)
#     if request.method == "POST":
#         form = UpdateTaskForm(request.POST, instance=tasks)
#         if form.is_valid():
#             try:
#                 form.save()
#                 return redirect("/show_tasks")
#             except:
#                 pass
#     else:
#         form = UpdateTaskForm(
#             initial={
#                 "task_name": tasks.task_name,
#                 "task_description": tasks.task_description,
#                 "status": tasks.status,
#             }
#         )
#     return render(request, "task/edit_task.html", {"tasks": tasks, "form": form})


# delete task
# def kill_task(request, id):
#     task = Task.objects.get(id=id)
#     task.delete()
#     return redirect("/show_tasks")


def task_delete(request, id):
    obj = get_object_or_404(Task, id=id)
    if request.method == "POST":
        obj.delete()
        return redirect("/show_tasks")
    context = {"object": obj}
    return render(request, "task/delete_task.html", context)


@login_required
def maintainOdoMeter(request):
    task = Task.objects.get(id=request.POST["task_id"])
    if "before_odo" in request.POST:
        task.odometerbefore = request.POST["before_odo"]
    else:
        if int(request.POST["after_odo"]) <= int(task.odometerbefore):
            messages.info(request, "Invalid final odo readings")
            return redirect(request.META["HTTP_REFERER"])
        task.odometerafter = request.POST["after_odo"]
    task.save()

    return redirect(request.META["HTTP_REFERER"])


def maintainTask(request):
    task = Task.objects.get(id=request.POST["task_id"])
    if request.FILES:
        if "beforewashing" in request.FILES:
            task.beforewash_task_img = request.FILES["beforewashing"]
            task.start_time = datetime.now()
        if "afterwashing" in request.FILES:
            task.afterwash_task_img = request.FILES["afterwashing"]
            task.stop_time = datetime.now()
            task.status = "Completed"
    task.save()
    if "damage_id" in request.POST:
        task.has_damage = True
        task.save()
        damages_id = request.POST.getlist("damage_id")
        count = 0
        damages = []
        for id in damages_id:
            damage = (
                WorkDoneDamages.objects.get(id=id)
                if WorkDoneDamages.objects.filter(id=id).first()
                else WorkDoneDamages()
            )
            damage.comment = request.POST.getlist("comment")[count]
            # damage.name = request.POST.getlist("name")[count]
            damage.user = request.user
            damage.task_id = task
            if request.FILES:
                damage.avatar = request.FILES.getlist("avatar")[count]
            
            
            damage.damage = Configurations.objects.filter(id=request.POST['config_damage']).first()
            damage.save()
            
            ++count
            if damage.comment:
                damages.append(damage.comment)

        msg_html = render_to_string(
            "emails/damages_notification.html",
            {"name": "Amos", "damages": damages, "task": task.task_name},
        ).strip()
        subject = "[Bus Shelter] Damage Notification"
        sendmailHtml(subject, msg_html, "brownsattar@gmail.com")

    return redirect(request.META["HTTP_REFERER"])


def getMonthTaskAjax(request):
    data = []
    labels = []
    config_types = Configurations.objects.filter(config_type='shelter_type')
    for config in config_types :
        labels.append(config.code)
        data.append(Task.objects.filter(shelter_type = config.id).count())
    res = {
        "data":data,
        "labels":labels
    }
    return JsonResponse(res, safe=False)


def getDamageTaskCountAjax(request):
    data = []
    data.append(
        Task.objects.filter(has_damage=True, createdat__year=date.today().year).count()
    )
    data.append(
        Task.objects.filter(has_damage=False, createdat__year=date.today().year).count()
    )

    return JsonResponse(data, safe=False)


def maintainconfigrations(request):
    config = (
        Configurations.objects.filter(id=request.POST["config_id"]).first()
        if Configurations.objects.filter(id=request.POST["config_id"]).first()
        else Configurations()
    )

    config.name = request.POST["name"]
    config.code = request.POST["code"]
    config.config_type = request.POST["config_type"]

    config.save()

    return redirect(request.META["HTTP_REFERER"])

def getTaskByDateRange(request,start_date,end_date):
    data = []
    labels = []
    config_types = Configurations.objects.filter(config_type='shelter_type')
    for config in config_types :
        labels.append(config.code)
        data.append(Task.objects.filter(shelter_type = config.id,createdat__gte = start_date,createdat__lte = end_date).count())
    res = {
        "data":data,
        "labels":labels
    }
    return JsonResponse(res, safe=False)

def reportIndex(request):
    if request.method =='POST':
        q1 = Q()
        q2 =Q()
        q3 = Q()
        q4 = Q()
        q5 = Q()
        
        if 'from_date' in request.POST and request.POST['from_date'] != '':
            q1 = Q(createdat__gte = request.POST['from_date'])
        if 'to_date' in request.POST and request.POST['to_date'] != '':
            q2 = Q(createdat__lte = request.POST['to_date'])
        if 'status' in request.POST and  request.POST['status'] != 'all' :
            q3 = Q(status = request.POST['status'])
        if 'user_id' in request.POST and request.POST['user_id'] != 'all':
            q4 = Q(user__id =request.POST['user_id'])
        if 'shelter_type' in request.POST and request.POST['shelter_type'] != 'all':
            q5 = Q(shelter_type__id = request.POST['shelter_type'])
        records = Task.objects.filter(q1 , q2 , q3 , q4 , q5)
    else:
        records = []
    shelter_types = Configurations.objects.filter(config_type = 'shelter_type')
    users = User.objects.filter(is_staff = False)
    
    filter_data = {
        "from_date" : request.POST['from_date'] if request.method == 'POST' and 'from_date' in  request.POST else '' ,
        "to_date": request.POST['to_date'] if request.method == 'POST' and 'from_date' in request.POST else '' ,
        "status" : request.POST['status'] if request.method == 'POST' and 'status' in request.POST else '' ,
        "user_id" :request.POST['user_id'] if request.method == 'POST' and 'user_id' in request.POST else '' ,
        "shelter_type" : request.POST['shelter_type'] if request.method == 'POST' and 'shelter_type' in request.POST else '' ,
    }
    context = {"records":records,'shelter_types':shelter_types,'users':users,'filter_data':filter_data}
    
    
    return render(request, "reports.html", context)


def html_to_pdf(request):
    q1 = Q()
    q2 =Q()
    q3 = Q()
    q4 = Q()
    q5 = Q()
    
    if 'from_date' in request.POST and request.POST['from_date'] != '':
        q1 = Q(createdat__gte = request.POST['from_date'])
    if 'to_date' in request.POST and request.POST['to_date'] != '':
        q2 = Q(createdat__lte = request.POST['to_date'])
    if 'status' in request.POST and  request.POST['status'] != 'all' and request.POST['status'] != '' :
        q3 = Q(status = request.POST['status'])
    if 'user_id' in request.POST and request.POST['user_id'] != 'all' and request.POST['user_id']  != '':
        q4 = Q(user__id =request.POST['user_id'])
    if 'shelter_type' in request.POST and request.POST['shelter_type'] != 'all' and request.POST['shelter_type'] != '':
        q5 = Q(shelter_type__id = request.POST['shelter_type'])
    tasks = Task.objects.filter(q1 , q2 , q3 , q4 , q5)
    filter_data = {
        "from_date" : request.POST['from_date'] if request.method == 'POST' and 'from_date' in  request.POST else '' ,
        "to_date": request.POST['to_date'] if request.method == 'POST' and 'to_date' in request.POST else '' ,
        "status" : request.POST['status'] if request.method == 'POST' and 'status' in request.POST else '' ,
        "user_id" :request.POST['user_id'] if request.method == 'POST' and 'user_id' in request.POST else '' ,
        "shelter_type" : request.POST['shelter_type'] if request.method == 'POST' and 'shelter_type' in request.POST else '' ,
    }
    
    base64Imgs = {}
    base64AfterImgs = {}
    for task in tasks:
        if task.afterwash_task_img:
            url_name = task.afterwash_task_img.url.split('.')
            mimecode_after = f'.{url_name[len(url_name)-1]}'
            encodedurl  = task.afterwash_task_img.url.split('/')
            del encodedurl[0]
            img = cv2.imread('/'.join(encodedurl))
            jpg_img = cv2.imencode(mimecode_after, img)
            b64_string = base64.b64encode(jpg_img[1]).decode('utf-8')
            base64AfterImgs[task.id] = f'data:image/{url_name[len(url_name)-1]};base64,{b64_string}'
            
        if task.beforewash_task_img:
            url_before = task.beforewash_task_img.url.split('.')
            mimecode_before = f'.{url_before[len(url_before)-1]}'
            beforeUrl = task.beforewash_task_img.url.split('/')
            del beforeUrl[0]
            img2 = cv2.imread('/'.join(beforeUrl))
            jpg_img2 = cv2.imencode(mimecode_before, img2)
            b64_string2 = base64.b64encode(jpg_img2[1]).decode('utf-8')
            base64Imgs[task.id] = f'data:image/{url_before[len(url_before)-1]};base64,{b64_string2}'
    context_dict = {
        "tasks": tasks,
        "logo" : getLogoBase64(),
        'base64Imgs':base64Imgs,
        'base64AfterImgs':base64AfterImgs,
        'filter_data':filter_data
    }       
    
    template = get_template('pdfgenarate.html')
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
    

