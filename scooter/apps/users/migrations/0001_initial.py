# Generated by Django 2.2.7 on 2020-05-26 19:40

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import scooter.apps.users.managers.users


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('username', models.CharField(error_messages={'unique': 'Ya existe un usuario'}, max_length=150, unique=True)),
                ('is_client', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('auth_facebook', models.BooleanField(default=False)),
                ('facebook_id', models.CharField(blank=True, max_length=200, null=True, unique=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('verification_deadline', models.DateTimeField()),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Status')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['-created', '-modified'],
                'get_latest_by': 'created',
                'abstract': False,
            },
            managers=[
                ('objects', scooter.apps.users.managers.users.CustomUserManager()),
            ],
        ),
    ]
