from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProfessionalProfile, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Every user gets a UserProfile; staff accounts are admins by default."""
    if not created:
        return
    role = 'admin' if instance.is_staff else 'client'
    UserProfile.objects.get_or_create(user=instance, defaults={'role': role})


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_professional_stub(sender, instance, created, **kwargs):
    """Professionals get an (empty) ProfessionalProfile stub at signup."""
    if not created or instance.user_type != 'provider':
        return
    ProfessionalProfile.objects.get_or_create(user=instance)
