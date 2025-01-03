# Generated by Django 5.1.3 on 2024-12-28 17:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_classcontentmodel_embed_video_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classcontentmodel',
            name='content_type',
            field=models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True or False'), ('fill_gaps', 'Fill in the Gaps'), ('word_bank', 'Word Bank'), ('drop_down_text', 'Drop Down Text'), ('ordering', 'Ordering'), ('sorting', 'Sorting'), ('category', 'Category'), ('matching', 'Matching'), ('flashcards', 'Flashcards'), ('table', 'Table'), ('accordion', 'Accordion'), ('tabs', 'Tabs'), ('button_stack', 'Button Stack'), ('process', 'Process'), ('timeline', 'Timeline'), ('multiple_choice_knowledge_check', 'Multiple Choice Knowledge Check'), ('true_false_knowledge_check', 'True or False Knowledge Check'), ('fill_gaps_knowledge_check', 'Fill in the Gaps Knowledge Check'), ('word_bank_knowledge_check', 'Word Bank Knowledge Check'), ('drop_down_text_knowledge_check', 'Drop Down Text Knowledge Check'), ('ordering_knowledge_check', 'Ordering Knowledge Check'), ('sorting_knowledge_check', 'Sorting Knowledge Check'), ('categories_knowledge_check', 'Categories Knowledge Check'), ('matching_knowledge_check', 'Matching Knowledge Check'), ('word_order_knowledge_check', 'Word Order Knowledge Check'), ('picture_matching_knowledge_check', 'Picture Matching Knowledge Check'), ('picture_labeling_knowledge_check', 'Picture Labeling Knowledge Check'), ('text_block', 'Text Block'), ('text_article', 'Text Article'), ('text_quote', 'Text Quote'), ('text_highlighted', 'Text Highlighted'), ('info_box', 'Info Box'), ('icon_list', 'Icon List'), ('image', 'Imagen'), ('video', 'Video'), ('audio', 'Audio'), ('video_embed', 'Video Embebido'), ('attachment', 'Archivo Adjunto'), ('ia_chat', 'IA Chat')], max_length=100),
        ),
        migrations.CreateModel(
            name='ScenarioModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('goals', models.JSONField(blank=True, null=True)),
                ('vocabulary', models.JSONField(blank=True, null=True)),
                ('key_expressions', models.JSONField(blank=True, null=True)),
                ('additional_info_objective', models.JSONField(blank=True, null=True)),
                ('limitations_student', models.TextField()),
                ('role_student', models.CharField(max_length=200)),
                ('role_polly', models.CharField(max_length=200)),
                ('instructions_polly', models.JSONField(blank=True, null=True)),
                ('limitations_polly', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scenarios', to='dashboard.classmodel')),
            ],
        ),
        migrations.CreateModel(
            name='ConversationHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=100)),
                ('messages', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversation_histories', to='dashboard.scenariomodel')),
            ],
        ),
    ]
