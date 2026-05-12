from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('URLHandler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clickevent',
            name='visitor_id',
            field=models.CharField(max_length=36, null=True),
        ),
    ]