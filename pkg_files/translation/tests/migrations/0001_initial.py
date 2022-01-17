# Generated by Django 3.2 on 2022-01-11 13:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyNewTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TranslatableTestModel',
            fields=[
                ('created_at', models.DateTimeField(auto_created=True, blank=True, default=django.utils.timezone.now)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.JSONField(blank=True, null=True)),
                ('description', models.JSONField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MyTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('new_test', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.mynewtest')),
            ],
        ),
    ]