from datetime import datetime, timedelta

from django.db.models import Count, QuerySet
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.utils import json

from users.models import Patient, TreatShip, Doctor, Guardian, GuardianShip, Appointment
from users.serializers import PatientSerializer, DoctorSerializer, TreatShipSerializer, GuardianSerializer, \
    AppointmentSerializer, TreatShipAddSerializer, AppointmentAddSerializer
from rest_framework.renderers import JSONRenderer


class Utf8JSONRenderer(JSONRenderer):
    charset = 'utf-8'


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    renderer_classes = (Utf8JSONRenderer,)

    @detail_route(methods=['POST'])  # 修改病人基本信息
    def change_patient(self, request, pk=None):
        patient = self.get_object()
        serializer = PatientSerializer(patient, data=request.data)
        post = request.POST
        phone = post.get('phone_number')
        # patient_id = post.get('patient_id')
        if (Patient.objects.filter(phone_number=phone).count() != 0 and
                Patient.objects.filter(phone_number=phone)[0].patient_id != pk or
                Doctor.objects.filter(phone_number=phone).count() != 0 or
                Guardian.objects.filter(phone_number=phone).count() != 0):
            return Response({'error': '手机号已存在'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    # 病人列表 接口 /patients/patient_list/
    # @list_route()
    # def patient_list(self, request):
    #     patient_list = Patient.objects.all().order_by('-age')
    #
    #     page = self.paginate_queryset(patient_list)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(patient_list, many=True)
    #     return Response(serializer.data)


class TreatShipViewSet(viewsets.ModelViewSet):
    queryset = TreatShip.objects.all()
    serializer_class = TreatShipSerializer

    renderer_classes = (Utf8JSONRenderer,)

    @list_route(methods=['POST'])
    def add_treatship(self, request):  # 添加病人信息
        post = request.POST
        doctor_id = post.get('doctor_id')
        guardian_id = post.get('guardian_id')
        doctor = Doctor.objects.get(doctor_id=doctor_id)
        # print(request.data)
        try:
            guardian = Guardian.objects.get(guardian_id=guardian_id)  # 查看是否有该联系人信息
        except Guardian.DoesNotExist:
            return Response({'status': '相关监护人不存在'}, status=status.HTTP_400_BAD_REQUEST)
        patient_serializer = PatientSerializer(data=request.data)
        if patient_serializer.is_valid():
            patient = patient_serializer.save()  # 添加病人信息
        else:
            return Response(patient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        treatShip_serializer = TreatShipAddSerializer(data=request.data)
        if treatShip_serializer.is_valid():
            treatShip_serializer.save(doctor=doctor, guardian=guardian, patient=patient)  # 添加病情信息
            return Response({'status': '添加病人信息成功'}, status=status.HTTP_200_OK)
        else:
            return Response(treatShip_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'])
    def add_treat_info(self, request):  # 添加病人新的病情信息 （多条时）
        post = request.POST
        doctor_id = post.get('doctor_id')
        guardian_id = post.get('guardian_id')
        patient_id = post.get('patient_id')
        doctor = Doctor.objects.get(doctor_id=doctor_id)
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            return Response({'status': '相关病人不存在'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            guardian = Guardian.objects.get(guardian_id=guardian_id)
        except Guardian.DoesNotExist:
            return Response({'status': '相关监护人不存在'}, status=status.HTTP_400_BAD_REQUEST)
        treat_info_serializer = TreatShipAddSerializer(data=request.data)
        if treat_info_serializer.is_valid():
            treat_info_serializer.save(doctor=doctor, guardian=guardian, patient=patient)
            return Response({'status': '添加病情信息成功'}, status=status.HTTP_200_OK)
        else:
            return Response(treat_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'])  # 查看病人病情信息（一条） 给监护人看 Sunday.
    def get_one_treatment_info(self, request):
        get = request.GET
        patient_id = get.get('patient_id')
        result = TreatShip.objects.filter(patient__patient_id=patient_id).order_by('-treat_time')[0]
        serializer = TreatShipAddSerializer(result, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'])  # 查看病人病情信息（多条） 给医生看 Sunday.
    def get_many_treatment_info(self, request):
        get = request.GET
        patient_id = get.get('patient_id')
        result = TreatShip.objects.filter(patient__patient_id=patient_id).order_by('-treat_time')
        serializer = TreatShipSerializer(result, many=True, context={'request': request})
        print(serializer.data)
        return Response(serializer.data)

    @list_route(methods=['GET', 'POST'])  # 搜索病人 和 病人列表接口
    def search_patient(self, request):
        get = request.GET
        patient_name = get.get('patient_name')
        doctor_phone = get.get('doctor_phone')
        results = TreatShip.objects.filter(patient__name__icontains=patient_name,
                                           doctor__phone_number=doctor_phone).values('patient__patient_id',
                                                                                     'patient__name',
                                                                                     'patient__main_illness').annotate(
            Count('id'))
        # 使用values进行调用返回的是valueQuerySet字段，而非QuerySet, 所以先转成list然后再使用json.dumps转成json
        if results:
            results = list(results)
            data = json.dumps(results)
            return HttpResponse(data)

    @list_route(methods=['GET'])
    def get_patient_basic_info(self, request):  # 查看病人基本信息 以及联系人信息
        get = request.GET
        patient_id = get.get('patient_id')
        doctor_id = get.get('doctor_id')
        # 按treat_time排序 取最近一次治疗的监护人信息
        result = TreatShip.objects.filter(doctor__doctor_id=doctor_id,
                                          patient__patient_id=patient_id).order_by('-treat_time')[0]
        serializer = TreatShipSerializer(result, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'])  # 监护人查看医嘱
    def get_guard_record(self, request):
        guardian_id = request.GET.get('guardian_id')
        try:
            result = TreatShip.objects.filter(guardian__guardian_id=guardian_id).order_by('-treat_time')[0]
        except:
            return Response({'status': '您暂时没有监护的病人记录'})
        serializer = TreatShipSerializer(result, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'])  # 监护人查看病人病历
    def guardian_get_treat_info(self, request):
        patient_id = request.GET.get('patient_id')
        result = TreatShip.objects.filter(patient__patient_id=patient_id).order_by('treat_time')
        serializer = TreatShipSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    renderer_classes = (Utf8JSONRenderer,)

    @list_route(methods=['POST'])  # 医生登录
    def doctor_login(self, request):
        phone = request.POST.get('phone_number')
        psw = request.POST.get('password')
        try:
            result = Doctor.objects.get(phone_number=phone,
                                        password=psw)
        except:
            return Response({'status': '用户不存在'})
        serializer = DoctorSerializer(result, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['POST'])  # 医生注册
    def doctor_register(self, request):
        id = request.POST.get('doctor_id')
        phone = request.POST.get('phone_number')
        doctor = Doctor.objects.filter(doctor_id=id)
        doctor2 = Doctor.objects.filter(phone_number=phone)
        if doctor.count() == 1:
            return Response({'status': '用户已经存在'})
        elif doctor2.count() == 1:
            return Response({'status': '此手机号已经注册'})
        doctor_serializer = DoctorSerializer(data=request.data)
        if doctor_serializer.is_valid():
            doctor_serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer

    renderer_classes = (Utf8JSONRenderer,)

    @list_route(methods=['POST'])  # 监护人登录
    def guardian_login(self, request):
        phone = request.POST.get('phone_number')
        psw = request.POST.get('password')
        try:
            result = Guardian.objects.get(phone_number=phone, password=psw)
        except:
            return Response({'status': '用户不存在'})
        # serializer = GuardianSerializer(result, context={'request': request})
        guardian_id = result.guardian_id
        treatship = TreatShip.objects.filter(guardian_id=guardian_id).order_by('-treat_time')
        if treatship.count() == 0:
            return Response({'status': '该监护人现在没有病人监护'})
        else:
            serializer2 = TreatShipSerializer(treatship[0], context={'request': request})
            return Response(serializer2.data)

    @list_route(methods=['POST'])  # 监护人注册
    def guardian_register(self, request):
        id = request.POST.get('guardian_id')
        phone = request.POST.get('phone_number')
        guardian = Guardian.objects.filter(guardian_id=id)
        guardian2 = Guardian.objects.filter(phone_number=phone)
        if guardian.count() == 1:
            return Response({'status': '用户已经存在'})
        elif guardian2.count() == 1:
            return Response({'status': '此手机号已经注册'})
        guardian_serializer = GuardianSerializer(data=request.data)
        if guardian_serializer.is_valid():
            guardian_serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(guardian_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GuardianShipViewSet(viewsets.ModelViewSet):
#     queryset = GuardianShip.objects.all()
#     serializer_class = GuardianShipSerializer

# @list_route(methods=['POST'])  # 添加联系人信息
# def add_guardian_id(self, request):
#     serializer = GuardianShipSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(status=status.HTTP_200_OK)
#     else:
#         return Response(serializer.errors,
#                         status=status.HTTP_400_BAD_REQUEST)
#
# @list_route(methods=['GET'])  # 查看病人联系人信息
# def get_guardian_detail(self, request):
#     get = request.GET
#     patient_id = get.get('patient_id')
#     result = GuardianShip.objects.filter(patient_id=patient_id)
#     serializer = GuardianShip2Serializer(result, many=True, context={'request': request})
#     return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    renderer_classes = (Utf8JSONRenderer,)

    @list_route(methods=['GET'])  # 医生查看预约信息 ———— 一周内记录
    def appointment_info_list(self, request):
        doctor_id = request.GET.get('doctor_id')
        date_now = datetime.now()
        date_past = date_now - timedelta(days=7)  # 过去一周
        print(date_now)  # 2019-06-29 14:16:11.346336
        result = Appointment.objects.filter(doctor__doctor_id=doctor_id,
                                            appointment_time__range=[date_past, date_now]).order_by('-appointment_time')
        serializer = AppointmentSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'])  # 医生查看预约信息 ———— 病人详细预约信息
    def appointment_info_detail(self, request):
        doctor_id = request.GET.get('doctor_id')
        patient_id = request.GET.get('patient_id')
        guardian_id = request.GET.get('guardian_id')
        appointment_time = request.GET.get('appointment_time')
        result = Appointment.objects.get(doctor__doctor_id=doctor_id,
                                         patient__patient_id=patient_id,
                                         guardian__guardian_id=guardian_id,
                                         appointment_time=appointment_time)
        serializer = AppointmentSerializer(result, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['GET'])  # 医生查看预约信息   ———— 只有预约状态
    def appointment_only_list(self, request):
        doctor_id = request.GET.get('doctor_id')
        result = Appointment.objects.filter(doctor__doctor_id=doctor_id,
                                            appointment_state='appoint').order_by('-appointment_time')
        serializer = AppointmentSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['POST'])  # 医生修改预约状态 变为已完成
    def change_appointment_state(self, request):
        id = request.POST.get('id')
        try:
            appointment = Appointment.objects.get(id=id)
            appointment.appointment_state = 'completed'
            appointment.save()
            return Response(status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['POST'])  # 监护人预约医生
    def guardian_appoint(self, request):
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        guardian_id = request.POST.get('guardian_id')
        patient = Patient.objects.get(patient_id=patient_id)
        doctor = Doctor.objects.get(doctor_id=doctor_id)
        guardian = Guardian.objects.get(guardian_id=guardian_id)
        appoint_serializer = AppointmentAddSerializer(data=request.data)
        # appoiontment_state = 'appoint' 前端附加一个此字段 值固定为appoint
        if appoint_serializer.is_valid():
            appoint_serializer.save(doctor=doctor, patient=patient, guardian=guardian)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(appoint_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'])  # 监护人查看预约
    def guardian_get_appoint(self, request):
        guardian_id = request.GET.get('guardian_id')
        try:
            result = Appointment.objects.filter(guardian__guardian_id=guardian_id,
                                                appointment_state='appoint').order_by('-appointment_time')[0]
        except:
            return Response({'status': '您没有未完成的预约。您可以选择去提交一个预约。'})
        appoint_serializer = AppointmentSerializer(result, context={'request': request})
        return Response(appoint_serializer.data)

    @list_route(methods=['GET'])  # 监护人取消预约
    def cancel_appoint(self, request):
        id = request.GET.get('id')
        appoint = Appointment.objects.get(id=id)
        appoint.delete()
        return Response(status=status.HTTP_200_OK)
