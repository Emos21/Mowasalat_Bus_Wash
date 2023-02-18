from atexit import register
from django import template
from cryptography.fernet import Fernet
from django.conf import settings
from ..models import Configurations,User


register = template.Library()

@register.filter
def replaceBlank(value,stringVal = ""):
    value = str(value).replace(stringVal, '')
    return value

@register.filter
def encryptdata(value):
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value = fernet.encrypt(str(value).encode())
    return value

@register.filter
def checkIfNull(data):
    if data:
        return data
    return '-'
@register.filter
def getBase64(value, pos):
    if pos in value.keys():
        res=value[pos]
    return res

@register.filter
def getShelterType(value):
    if value and value != 'all':
        return Configurations.objects.filter(id=value).first().name
    else:
        return 'All'       
    
@register.filter
def getUserName(value):
    if value and value != 'all':
        return User.objects.filter(id = value).first().username
    else:
        return 'All'
