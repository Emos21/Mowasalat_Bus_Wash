import enum
import logging
import qrcode
import math
from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib.auth.models import User
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Create your models here.



# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile.png", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} Profile"

    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)


        img = Image.open(self.image.path)  

        
        if img.height > 100 or img.width > 100:
            output_size = (100, 100)
            img.thumbnail(output_size)  
            img.save(self.image.path)  



class Location(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Site(models.Model):
    site_code = models.CharField(max_length=100)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True
    )
    avatar = models.ImageField(default="shelter.jpg", upload_to="site-img/", null=True, blank=True)

    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_code

    def save(self, *args, **kwargs):
        super(Site, self).save(*args, **kwargs)
        print(self.avatar)
        imag = Image.open(self.avatar.path)
        if imag.width > 200 or imag.height > 200:
            output_size = (200, 200)
            imag.thumbnail(output_size)
            imag.save(self.avatar.path)


class TypeofWash(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name



class SiteMap(models.Model):
    name= models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    map_url = models.URLField(max_length=10000)

    def __str__(self):
        return self.name

####### TASK MANAGER ########

STATUSES = (
    ("in progress", "In Progress"),
    ("completed", "Complete"),
)

TIMER_STATE = (
    ("Start Timer", "start timer"),
    ("Stop Timer", "stop timer"),
)


class Timestamp(models.Model):
    task = models.ForeignKey("Task", on_delete=models.CASCADE, null=True)
    begin_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()

    def elapsed_time(self):
        return math.floor(((self.end_time - self.begin_time).total_seconds() / 60))

    class Meta:
        db_table = "timestamps"


class Configurations(models.Model):
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255, null=True)
    config_type = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        return self.name


class Task(models.Model):
    task_complete = models.BooleanField(default=False)
    task_name = models.CharField(max_length=100)
    task_description = models.TextField()
    timer_state = models.CharField(
        max_length=11, choices=TIMER_STATE, default="Start Timer"
    )
    begin_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=11, choices=STATUSES, default="in progress")
    odometerbefore = models.IntegerField(null=True, blank=True)
    odometerafter = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        related_name="tasks_assigned",
        verbose_name=_("assigned to"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_scanned = models.BooleanField(default=False)
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE, null=True)
    
    map_url = models.URLField(max_length=10000, null=True)
    createdat = models.DateField(auto_now_add=True, null=True)
    updatedat = models.DateField(auto_now_add=True, null=True)

    beforewash_task_img = models.FileField(
        upload_to="Task_Complete/before/", null=True, blank=True
    )
    afterwash_task_img = models.FileField(
        upload_to="Task_Complete/after/", null=True, blank=True
    )
    start_time = models.DateTimeField(auto_now=False, null=True,blank=True)
    stop_time = models.DateTimeField(auto_now=False, null=True,blank=True)
    has_damage = models.BooleanField(default=False)
    shelter_type = models.ForeignKey(Configurations, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "tasks"
    


    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        if self.beforewash_task_img:
            imag = Image.open(self.beforewash_task_img.path)
            if imag.width > 200 or imag.height > 200:
                output_size = (200, 200)
                imag.thumbnail(output_size)
                imag.save(self.beforewash_task_img.path)
        
        if self.afterwash_task_img:
            imag = Image.open(self.afterwash_task_img.path)
            if imag.width > 200 or imag.height > 200:
                output_size = (200, 200)
                imag.thumbnail(output_size)
                imag.save(self.afterwash_task_img.path)
 


class WorkDoneDamages(models.Model):
    name = models.CharField(max_length=100)
    comment = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to="Damages/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name="workdamages_assigned",
        verbose_name=_("assigned to"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    damage = models.ForeignKey(Configurations, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(WorkDoneDamages, self).save(*args, **kwargs)
        print(self.avatar)
        imag = Image.open(self.avatar.path)
        if imag.width > 200 or imag.height > 200:
            output_size = (200, 200)
            imag.thumbnail(output_size)
            imag.save(self.avatar.path)

