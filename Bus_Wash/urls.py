from django.contrib import admin
from django.urls import path, include
from .views import *
from . import views
from . import api
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

from .views import ChangePasswordView

# API Router
router = DefaultRouter()
router.register(r'locations', api.LocationViewSet)
router.register(r'sites', api.SiteViewSet)
router.register(r'tasks', api.TaskViewSet)
router.register(r'damage-reports', api.DamageReportViewSet)

urlpatterns = [
    # REST API endpoints
    path('api/', include(router.urls)),
    path('api/dashboard/', api.api_dashboard_stats, name='api-dashboard'),
    path('api/tasks/location/<int:location_id>/', api.api_tasks_by_location, name='api-tasks-by-location'),
    path('api/tasks/status/<str:status>/', api.api_tasks_by_status, name='api-tasks-by-status'),
    path('api/tasks/<int:task_id>/update-status/', api.api_update_task_status, name='api-update-task-status'),
    path('api/notifications/', api.api_notifications, name='api-notifications'),
    path('api/notifications/<int:notification_id>/read/', api.api_mark_notification_read, name='api-mark-notification-read'),
    path('api/notifications/mark-all-read/', api.api_mark_all_notifications_read, name='api-mark-all-read'),
    path('api/performance/', api.api_performance_metrics, name='api-performance'),

    path("", views.HomeDashboard, name="home"),
    path("qr_code/", include("qr_code.urls", namespace="qr_code")),
    path("login", views.login_page, name="login-page"),
    path("user_login", views.login_user, name="login-user"),
    path("logout", views.logout_user, name="logout"),
    path("site_list", views.site_list, name="site_list"),
    # path("add_site", views.managesite, name="add_site"),
    # path("edit_employee/<int:pk>", views.managesite, name="edit-employee"),
    # path("save_employee", views.save_employee, name="save-employee"),
    path("view_card/<int:pk>", views.view_card, name="view-card"),
    path("view_details/<str:code>", views.view_details, name="view-details"),
    path("view_details/<str:code>/<int:task_id>", views.view_details, name="view-task-details"),
    path('maintain/Task',views.maintainTask,name="maintainTask"),
    path('get/Month/Task/Ajax',views.getMonthTaskAjax,name="getMonthTaskAjax"),
    path('get/Damage-Task/Count-Ajax',views.getDamageTaskCountAjax,name="getDamageTaskCountAjax"),
    path("view_details", views.view_details, name="scanned-code"),
    path("scanner", views.view_scanner, name="view-scanner"),
    path("scanner/<int:task_id>", views.view_scanner, name="view-scanner-task"),
    # path("delete_employee/<int:pk>", views.delete_employee, name="delete-employee"),
    path("add_task", views.new, name="add_task"),
    path("show_tasks", views.show_tasks, name="show_tasks"),
    path("show_tasks/<str:status>", views.show_tasks, name="show_tasks_all"),
    path("edit_task/<int:id>", views.edit_task, name="edit_task"),
    # path("update_task/<int:id>", views.update_task, name="update_task"),
    path("task_delete/<int:id>", views.task_delete, name="task_delete"),
    path('maintain/Odometer',views.maintainOdoMeter,name="maintainOdoMeter"),
    path("profile", views.profile, name="profile"),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('get/Task-By-Date-Range/<str:start_date>/to/<str:end_date>',getTaskByDateRange,name="getTaskByDateRange"),
    path('report/Index',reportIndex,name="reportIndex"),
    path('html_to_pdf',html_to_pdf,name="html_to_pdf"),
    path('export_to_excel', views.export_to_excel, name="export_to_excel"),

] 

if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
