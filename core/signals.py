# core/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Pin, Pinboard, Image, Followstream, Comment

logger = logging.getLogger(__name__)
def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    if sender.__name__ in ['Pin', 'Pinboard', 'Image', 'Followstream', 'Comment']:
        action = 'CREATED' if created else 'UPDATED'
        logger.info(f"[{now()}] {sender.__name__} {action}: {instance.pk}")

@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    if sender.__name__ in ['Pin', 'Pinboard', 'Image', 'Followstream', 'Comment']:
        logger.info(f"[{now()}] {sender.__name__} DELETED: {instance.pk}")


from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"[{now()}] LOGIN: User {user.email} (ID: {user.pk}) from IP {get_ip(request)}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"[{now()}] LOGOUT: User {user.email} (ID: {user.pk}) from IP {get_ip(request)}")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    email = credentials.get('email', 'UNKNOWN')
    logger.warning(f"[{now()}] LOGIN FAILED: Email {email} from IP {get_ip(request)}")
