# Generated by Django 5.2.1 on 2025-06-22 09:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_mocktest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MockTestSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('total_questions', models.IntegerField(default=24)),
                ('duration_minutes', models.IntegerField(default=45)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MockTestAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.question')),
                ('selected_choices', models.ManyToManyField(to='main.questionoption')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='main.mocktestsession')),
            ],
        ),
        migrations.DeleteModel(
            name='MockTest',
        ),
    ]
