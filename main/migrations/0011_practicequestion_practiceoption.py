# Generated by Django 5.2.1 on 2025-06-16 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_lessoncontent_glossary'),
    ]

    operations = [
        migrations.CreateModel(
            name='PracticeQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('explanation', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='questions/')),
                ('multiple_answers', models.BooleanField(default=False)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='main.chapter')),
            ],
        ),
        migrations.CreateModel(
            name='PracticeOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='main.practicequestion')),
            ],
        ),
    ]
