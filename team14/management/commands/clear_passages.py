from django.core.management.base import BaseCommand
from team14.models import Passage


class Command(BaseCommand):
    help = "Delete all passages and related questions/options"

    def handle(self, *args, **kwargs):
        count = Passage.objects.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("⚠️ No passages found to delete"))
            return

        Passage.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(f"✅ Successfully deleted {count} passages and all related data")
        )
