from datetime import datetime

from django.db import models


# Create your models here.
class Person(models.Model):
    """
    抽象基类
    """
    name = models.CharField(max_length=128, verbose_name="姓名")
    password = models.CharField(max_length=60, verbose_name="密码")
    # identify_number = models.CharField(max_length=18, verbose_name="身份证号")
    phone_number = models.CharField(max_length=11, verbose_name="手机号", unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Patient(Person):
    """
    病人
    """
    # 主键 身份证号
    patient_id = models.CharField(max_length=18, primary_key=True, verbose_name="身份证号")
    # null=True表示允许数据库值为空
    # blank=True表示允许表单验证值为空
    longitude = models.CharField(max_length=30, null=True, blank=True, verbose_name="经度")
    latitude = models.CharField(max_length=30, null=True, blank=True, verbose_name="纬度")
    heart_rate = models.CharField(max_length=10, null=True, blank=True, verbose_name="心率")
    blood_pressure = models.CharField(max_length=10, null=True, blank=True, verbose_name="血压")
    step_number = models.CharField(max_length=10, null=True, blank=True, verbose_name="步数")
    gender = models.CharField(
        max_length=6,
        choices=(("male", "男"), ("female", "女")),
        null=True, blank=True,
        verbose_name="性别"
    )
    marriage = models.CharField(
        max_length=20,
        choices=(("YES", "已婚"), ("NO", "未婚")),
        null=True, blank=True,
        verbose_name="婚姻状况"
    )
    age = models.CharField(max_length=6, blank=True, verbose_name="年龄")
    job = models.CharField(max_length=200, null=True, blank=True, verbose_name="工作")
    nation = models.CharField(max_length=20, null=True, blank=True, verbose_name="民族")
    native_place = models.CharField(max_length=200, null=True, blank=True, verbose_name="籍贯")
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name="住址")
    main_illness = models.CharField(max_length=100, null=True, blank=True, verbose_name="主要疾病")

    class Meta:
        db_table = "patient"  # 表名


class Guardian(Person):
    """
    监护人
    """
    # 主键 身份证号
    guardian_id = models.CharField(max_length=18, primary_key=True, verbose_name="身份证号")
    # 多对多关系
    cares = models.ManyToManyField(Patient, related_name="carers", through="GuardianShip")

    class Meta:
        db_table = "guardian"  # 表名


class Doctor(Person):
    """
    医生
    """
    # 主键 身份证号
    doctor_id = models.CharField(max_length=18, primary_key=True, verbose_name="身份证号")
    working_unit = models.CharField(max_length=30, verbose_name="从业单位")
    working_num = models.CharField(max_length=30, verbose_name="工号")
    working_title = models.CharField(max_length=30, verbose_name="职称")
    resume = models.TextField(max_length=1000, verbose_name="简介")
    # 多对多关系
    patients = models.ManyToManyField(Patient, related_name="doctors", through="TreatShip")

    class Meta:
        db_table = "Doctor"  # 表名
        unique_together = ('working_unit', 'working_num')


class GuardianShip(models.Model):
    """
    监护关系
    """
    # 外键 分别为 Patient 和 Guardian 的主键
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="病人身份证号")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, verbose_name="监护人身份证号")
    # 监护关系的其他属性
    guard_time = models.DateField(verbose_name="监护时间", null=True)

    class Meta:
        db_table = "guardianShip"  # 表名


class TreatShip(models.Model):
    """
    治疗关系
    """
    # 外键 分别为 Patient 和 Doctor 的主键
    patient = models.ForeignKey(Patient, related_name='treatment', on_delete=models.CASCADE, verbose_name="病人身份证号")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="医生身份证号")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE)
    # 治疗关系的其他属性
    illness_now = models.TextField(max_length=1000, null=True, blank=True, verbose_name="现今病情")
    illness_past = models.TextField(max_length=1000, null=True, blank=True, verbose_name="以往病史")
    sub_visit_time = models.DateField(null=True, blank=True, verbose_name="复诊时间")
    treatment = models.TextField(max_length=1000, null=True, blank=True, verbose_name="治疗方案")
    medicine = models.TextField(max_length=1000, null=True, blank=True, verbose_name="服药信息")
    # 接受治疗的时间
    treat_time = models.DateField(verbose_name="治疗时间")

    class Meta:
        db_table = "treatShip"  # 表名
        unique_together = ('patient', 'doctor', 'guardian', 'treat_time')


class VerifyCode(models.Model):
    """
    短信验证码
    """
    code = models.CharField(max_length=10, verbose_name="验证码")
    phone_number = models.CharField(max_length=11, verbose_name="手机号")
    add_time = models.DateField(verbose_name="添加时间")

    def __str__(self):
        return self.code


class Appointment(models.Model):
    # 外键
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE)

    appointment_time = models.DateField(verbose_name="预约时间")
    appointment_state = models.CharField(max_length=10,
                                         choices=(("appoint", "预约"), ("completed", "已完成"))
                                         )

    class Meta:
        db_table = "appointment"  # 表名
        unique_together = ('patient', 'doctor', 'guardian', 'appointment_time')
