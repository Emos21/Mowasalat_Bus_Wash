from rest_framework import serializers, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Task, Site, Location, Configurations, WorkDoneDamages, Notification


# Serializers
class LocationSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'task_count']


class SiteSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = Site
        fields = ['id', 'site_code', 'location', 'location_name', 'date_added']


class TaskSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source='site_id.site_code', read_only=True)
    location_name = serializers.CharField(source='site_id.location.name', read_only=True)
    assigned_to = serializers.CharField(source='user.username', read_only=True)
    shelter_type_name = serializers.CharField(source='shelter_type.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_name', 'task_description', 'status',
            'site_code', 'location_name', 'assigned_to',
            'shelter_type_name', 'is_scanned', 'has_damage',
            'createdat', 'map_url'
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source='site_id.site_code', read_only=True)
    location_name = serializers.CharField(source='site_id.location.name', read_only=True)
    assigned_to = serializers.CharField(source='user.username', read_only=True)
    shelter_type_name = serializers.CharField(source='shelter_type.name', read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class DamageReportSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task_id.task_name', read_only=True)
    reported_by = serializers.CharField(source='user.username', read_only=True)
    damage_type = serializers.CharField(source='damage.name', read_only=True)

    class Meta:
        model = WorkDoneDamages
        fields = ['id', 'name', 'comment', 'task_name', 'reported_by', 'damage_type', 'created_at']


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configurations
        fields = ['id', 'name', 'code', 'config_type']


# ViewSets
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.annotate(task_count=Count('site__task')).order_by('name')
    serializer_class = LocationSerializer


class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Site.objects.select_related('location').order_by('site_code')
    serializer_class = SiteSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('site_id', 'site_id__location', 'user', 'shelter_type').order_by('-createdat')
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer


class DamageReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkDoneDamages.objects.select_related('task_id', 'user', 'damage').order_by('-created_at')
    serializer_class = DamageReportSerializer


# API Views
@api_view(['GET'])
def api_dashboard_stats(request):
    """Get dashboard statistics for mobile app"""
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    in_progress_tasks = Task.objects.filter(status='in progress').count()
    total_sites = Site.objects.count()
    total_locations = Location.objects.count()
    damage_reports = WorkDoneDamages.objects.count()

    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

    # Top locations by task count
    top_locations = Location.objects.annotate(
        task_count=Count('site__task')
    ).order_by('-task_count')[:5].values('name', 'task_count')

    return Response({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_rate': completion_rate,
        'total_sites': total_sites,
        'total_locations': total_locations,
        'damage_reports': damage_reports,
        'top_locations': list(top_locations)
    })


@api_view(['GET'])
def api_tasks_by_location(request, location_id):
    """Get all tasks for a specific location"""
    tasks = Task.objects.filter(
        site_id__location_id=location_id
    ).select_related('site_id', 'user', 'shelter_type')
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def api_tasks_by_status(request, status):
    """Get tasks filtered by status"""
    tasks = Task.objects.filter(status=status).select_related('site_id', 'user', 'shelter_type')
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def api_update_task_status(request, task_id):
    """Update task status from mobile app"""
    try:
        task = Task.objects.get(id=task_id)
        new_status = request.data.get('status')
        if new_status in ['in progress', 'completed']:
            task.status = new_status
            task.save()
            return Response({'success': True, 'message': f'Task status updated to {new_status}'})
        return Response({'success': False, 'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        return Response({'success': False, 'message': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.task_name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'task_name', 'is_read', 'created_at']


@api_view(['GET'])
def api_notifications(request):
    """Get recent notifications"""
    notifications = Notification.objects.all()[:20]
    serializer = NotificationSerializer(notifications, many=True)
    unread_count = Notification.objects.filter(is_read=False).count()
    return Response({
        'notifications': serializer.data,
        'unread_count': unread_count
    })


@api_view(['POST'])
def api_mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def api_mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(is_read=False).update(is_read=True)
    return Response({'success': True})


# Performance Metrics API
@api_view(['GET'])
def api_performance_metrics(request):
    """Get worker performance metrics"""
    from django.contrib.auth.models import User
    from django.db import models as db_models

    # Get all users with task assignments
    users_with_tasks = User.objects.filter(tasks_assigned__isnull=False).distinct()

    worker_stats = []
    for user in users_with_tasks:
        user_tasks = Task.objects.filter(user=user)
        completed = user_tasks.filter(status='completed').count()
        total = user_tasks.count()
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0

        worker_stats.append({
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'total_tasks': total,
            'completed_tasks': completed,
            'in_progress': user_tasks.filter(status='in progress').count(),
            'completion_rate': completion_rate
        })

    # Sort by completion rate
    worker_stats.sort(key=lambda x: x['completion_rate'], reverse=True)

    # Location performance
    location_stats = Location.objects.annotate(
        total_tasks=Count('site__task'),
        completed_tasks=Count('site__task', filter=db_models.Q(site__task__status='completed'))
    ).values('name', 'total_tasks', 'completed_tasks')

    return Response({
        'worker_performance': worker_stats,
        'location_performance': list(location_stats),
        'summary': {
            'total_workers': len(worker_stats),
            'avg_completion_rate': round(sum(w['completion_rate'] for w in worker_stats) / len(worker_stats), 1) if worker_stats else 0
        }
    })
