from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, JobSeeker, Company

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        if instance.user_type == 'job_seeker':
            JobSeeker.objects.create(user=instance)
        elif instance.user_type == 'company_rep':
            Company.objects.create(
                user=instance,
                name=f"{instance.username}'s Company",  # Placeholder
                description="",
                location="",
                industry="",
                culture=""
            )