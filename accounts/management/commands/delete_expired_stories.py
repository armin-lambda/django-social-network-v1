from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.translation import ngettext
from django.utils import timezone

from accounts.models import Story


class Command(BaseCommand):
    help = 'Delete Expired Stories'

    def handle(self, *args, **options):
        expired_time = timezone.now() - timedelta(hours=24)
        deleted_count, _ = Story.objects.filter(
            created_at__lt = expired_time
        ).delete()

        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    ngettext(
                        f"{deleted_count} expired story deleted.",
                        f"{deleted_count} expired stories deleted.",
                        deleted_count
                    )
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('There are no expired stories.'),
            )
