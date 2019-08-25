# Generated by Django 2.2.2 on 2019-06-29 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appointment_time',
            field=models.DateField(verbose_name='预约时间'),
        ),
        migrations.AlterField(
            model_name='guardianship',
            name='guard_time',
            field=models.DateField(null=True, verbose_name='监护时间'),
        ),
        migrations.AlterField(
            model_name='treatship',
            name='sub_visit_time',
            field=models.DateField(blank=True, null=True, verbose_name='复诊时间'),
        ),
        migrations.AlterField(
            model_name='treatship',
            name='treat_time',
            field=models.DateField(verbose_name='治疗时间'),
        ),
        migrations.AlterField(
            model_name='verifycode',
            name='add_time',
            field=models.DateField(verbose_name='添加时间'),
        ),
    ]