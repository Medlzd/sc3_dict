from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        def create_custom_permissions(sender, **kwargs):
            content_type, _ = ContentType.objects.get_or_create(app_label='core', model='user')

            Permission.objects.get_or_create(
                codename="can_manage_users",
                name="Can manage users",
                content_type=content_type,
            )

        post_migrate.connect(create_custom_permissions, sender=self)
