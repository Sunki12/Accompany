from rest_framework import serializers
from users.models import Patient, Doctor, Guardian, TreatShip, GuardianShip, Appointment


# 监护人
class GuardianSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Guardian
        fields = ('url', 'cares',
                  'name', 'password', 'phone_number', 'guardian_id')


# 医生
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    # patients = serializers.ReadOnlyField(source="patients.name")

    class Meta:
        model = Doctor
        fields = ('url', 'patients',
                  'name', 'doctor_id', 'phone_number', 'working_unit',
                  'working_num', 'working_title', 'resume', 'password')


# 病人
class PatientSerializer(serializers.ModelSerializer):
    # doctors_name = serializers.RelatedField(source="doctors.resume", read_only=True)
    # carers = serializers.SerializerMethodField()
    # treatment = serializers.SerializerMethodField()
    #
    # def get_carers(self, obj):
    #     queryset = obj.carers.all()
    #     return [{'guardian_id': obj.guardian_id, 'guardian_phone': obj.phone_number} for obj in queryset]
    #
    # def get_treatment(self, obj):
    #     queryset = obj.treatment.all()
    #     return [{'illness_now': obj.illness_now} for obj in queryset]

    class Meta:
        model = Patient
        # fields = ('url', 'doctors', 'carers',
        #           'name', 'password', 'phone_number', 'patient_id', 'age', 'longitude', 'latitude', 'heart_rate',
        #           'blood_pressure', 'step_number', 'gender', 'marriage', 'age', 'job', 'nation',
        #           'native_place', 'address')
        fields = '__all__'
        read_only_fields=('password', )


# 治疗关系
class TreatShipSerializer(serializers.ModelSerializer):
    # patient_name = serializers.ReadOnlyField(source="patient.name")
    # doctor_name = serializers.ReadOnlyField(source="doctor.name")

    # def get_patient_names(self, obj):
    #     queryset = obj.patient
    #
    #     return [{'name': obj.name} for obj in queryset]
    doctor = DoctorSerializer()
    patient = PatientSerializer()
    guardian = GuardianSerializer()

    class Meta:
        model = TreatShip
        # fields = ('url',
        #           'illness_now', 'patient', 'doctor',
        #           'illness_past', 'sub_visit_time', 'treatment', 'medicine', 'treat_time',
        #           )
        fields = '__all__'


# 治疗关系
class TreatShipAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatShip
        fields = '__all__'
        read_only_fields = ('doctor', 'guardian', 'patient',)


# # 监护关系
# class GuardianShipSerializer(serializers.ModelSerializer):
#     # patient_id = serializers.ReadOnlyField(source="patient.patient_id")
#     # guardian_id = serializers.ReadOnlyField(source="guardian.guardian_id")
#     patient = PatientSerializer()
#     guardian = GuardianSerializer()
#
#     class Meta:
#         model = GuardianShip
#         fields = ('url',
#                   'patient', 'guardian')
#
#
# class GuardianShip2Serializer(serializers.ModelSerializer):
#     phone_number = serializers.ReadOnlyField(source="guardian.phone_number")
#
#     class Meta:
#         model = GuardianShip
#         fields = ('phone_number',)


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    guardian = GuardianSerializer()
    doctor = DoctorSerializer()

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('doctor', 'guardian', 'patient',)

# class PatientListSerializer(serializers.Serializer):
#     patient_id = serializers.CharField()
#     name = serializers.CharField()
#     main_illness = serializers.CharField()
#
#     class Meta:
#         fields = ('patient_id', 'name', 'main_illness')
