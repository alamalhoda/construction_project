# Generated manually for multi-project support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("construction", "0022_unitspecificexpense"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="color",
            field=models.CharField(
                default="#667eea",
                help_text="رنگ نمایش پروژه (فرمت HEX)",
                max_length=7,
                verbose_name="رنگ پروژه",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="icon",
            field=models.CharField(
                default="fa-building",
                help_text="نام کلاس آیکون Font Awesome (مثال: fa-building)",
                max_length=50,
                verbose_name="آیکون پروژه",
            ),
        ),
    ]

