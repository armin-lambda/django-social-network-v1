from django.db.models.signals import post_save
from django.core.management import call_command
from django.dispatch import receiver

from accounts.models import Story


@receiver(post_save, sender=Story)
def delete_expired_stories(sender, instance, created, **kwargs):
    if created:
        call_command('delete_expired_stories')
