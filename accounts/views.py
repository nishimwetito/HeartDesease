from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserRoleManager
# Forms from Account app
from .forms import UserRoleManagerForm, PatientsForm, HeartMedicalHistoryForm
# Tables from Heart App
from heart_app.models import Patients, Heart_Medical_History, Assigned_Test_from_Doctor_dep, RecordsFromConsult
from django.contrib import messages
from datetime import date
# Import predict model
import pickle
import numpy as np
# Create your views here.


def LoginView(request):
    roleform = UserRoleManagerForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        roleform = UserRoleManagerForm(request.POST)

        user = authenticate(username=username, password=password)

        if user is not None and roleform.is_valid():
            role = roleform.cleaned_data['role']
            if UserRoleManager.objects.filter(user=user, role=role.id):
                login(request, user)
                messages.success(request, 'Login Successfully...')
                return redirect('dashboard')
            else:
                messages.info(request, 'Invalid Credentials')
            return redirect('login')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')

    context = {'roleform': roleform}
    return render(request, 'accounts/login.html', context)

# Logout


def LogoutView(request):
    logout(request)
    messages.success(request, 'Logout Successfully...')
    return redirect('login')


@login_required(login_url='login')
def DashboardView(request):
    # Consult page
    user = UserRoleManager.objects.get(user=request.user.id)
    if UserRoleManager.objects.filter(user=request.user.id, role__role='Consult'):
        page1 = 'dash1'
        context = {'user': user,
                   'page1': page1}
        return render(request, 'accounts/consult_dashboard.html', context)

    # Heart Disease Department page
    elif UserRoleManager.objects.filter(user=request.user.id, role__role='Heart'):
        page1 = 'heartdash1'
        context = {'user': user,
                   'page1': page1}
        return render(request, 'accounts/heart_dashboard.html', context)

    # Laboratory Department page
    elif UserRoleManager.objects.filter(user=request.user.id, role__role='Laboratory'):
        page1 = 'labdash1'
        context = {'user': user,
                   'page1': page1}
        return render(request, 'accounts/laboratory_dashboard.html', context)
    else:
        return redirect('home')

# ======================= CONSULTANT PART==========
# Add Patients


@login_required(login_url='login')
def AddPatientView(request):
    page2 = 'dash2'
    patient = PatientsForm()
    if request.method == 'POST':
        patient = PatientsForm(request.POST)
        if patient.is_valid():
            patient.save(commit=True)
            if True:
                messages.success(request, 'Patient Added Successfully...')
                return redirect('viewpatients')
        else:
            messages.error(request, 'Error occured please try again...')
            return redirect('addpatient')
    context = {'page2': page2, 'patient': patient}
    return render(request, 'accounts/consult_dashboard.html', context)

# Edit Patient


@login_required(login_url='login')
def EditPatientView(request, id):
    page2 = 'dash2'
    pat = Patients.objects.get(pk=id)
    patient = PatientsForm(instance=pat)
    if request.method == 'POST':
        patient = PatientsForm(request.POST, instance=pat)

        if patient.is_valid():
            patient.save()
            if True:
                messages.success(
                    request, 'Patient Records Successfully Updated...')
                return redirect('viewpatients')
    context = {'page2': page2, 'patient': patient}
    return render(request, 'accounts/consult_dashboard.html', context)


# View patients
@login_required(login_url='login')
def PatientsView(request):
    page3 = 'dash3'
    patients = Patients.objects.all().order_by("-id")
    context = {'page3': page3,
               'patients': patients}
    return render(request, 'accounts/consult_dashboard.html', context)


# We are going to send Patient record to the doctor
def ConsultToDoctorView(request, id):
    patient = Patients.objects.get(pk=id)
    today = date.today()
    if RecordsFromConsult.objects.filter(patient=patient, patient__disease__name='Heart').exists():
        messages.error(request, 'Data Already Sent...')
    if RecordsFromConsult.objects.filter(patient=patient, patient__disease__name='Diabete').exists():
        messages.error(request, 'Data Already Sent...')
    elif Patients.objects.filter(id=patient.id, disease=None):
        messages.error(request, 'Please Select Patient Disease...')
        return redirect('viewpatients')
    else:
        record = RecordsFromConsult.objects.create(
            patient=patient,
        )
        record.save()
        messages.success(request, 'Records sent Successfully...')
    return redirect('viewconsdoctor')


def DeleteConsultRecord(request, id):
    record = RecordsFromConsult.objects.get(pk=id)
    record.delete()
    return redirect('viewconsdoctor')


# Here we view the data we sent to doctor
def viewConsultToDoctorView(request):
    page5 = 'dash5'
    patientrecord = RecordsFromConsult.objects.all()
    context = {'page5': page5,
               'patientrecord': patientrecord}
    return render(request, 'accounts/consult_dashboard.html', context)
# ======================= CONSULTANT PART END==========


# ======================= LABORATORY PART ============

# There are medical test record done for lab test
def HeartLabMedicalHistView(request):
    page2 = 'labdash2'
    exams = Heart_Medical_History.objects.all().order_by("-id")
    context = {'page2': page2,
               'exams': exams}
    return render(request, 'accounts/laboratory_dashboard.html', context)


# Records from doctor
def RecordsFromDoctorView(request):
    page3 = 'labdash3'
    records = Assigned_Test_from_Doctor_dep.objects.filter(
        patient__disease__name='Heart')
    context = {'page3': page3,
               'records': records}
    return render(request, 'accounts/laboratory_dashboard.html', context)


# Here we are going to add and save laboratory exam results
def AddHeartLabResults(request, id):
    page4 = 'labdash4'
    patients = Assigned_Test_from_Doctor_dep.objects.get(pk=id)
    examrec = HeartMedicalHistoryForm()

    if request.method == 'POST':
        examrec = HeartMedicalHistoryForm(request.POST)
        if examrec.is_valid():
            # Clean form data
            chestpaintype = examrec.cleaned_data['chestpaintype']
            restingbp = examrec.cleaned_data['restingbp']
            cholesterol = examrec.cleaned_data['cholesterol']
            fastingbs = examrec.cleaned_data['fastingbs']
            restingecg = examrec.cleaned_data['restingecg']
            maxhr = examrec.cleaned_data['maxhr']
            exerciseangina = examrec.cleaned_data['exerciseangina']
            oldpeak = examrec.cleaned_data['oldpeak']
            st_slope = examrec.cleaned_data['st_slope']

            # Save cleaned data to database
            patientrecords = Heart_Medical_History.objects.create(
                patient_id=patients.patient.id,
                chestpaintype=chestpaintype,
                restingbp=restingbp,
                cholesterol=cholesterol,
                fastingbs=fastingbs,
                restingecg=restingecg,
                maxhr=maxhr,
                exerciseangina=exerciseangina,
                oldpeak=oldpeak,
                st_slope=st_slope,
            )
            patientrecords.save()
            if True:
                patients.delete()
                messages.success(
                    request, f'Heart Exam Results of {patients.patient.first_name} Saved Successfully...')
                return redirect('heartlabresult')
        else:
            messages.error(request, 'Error Occured! Please Try again...')
            return redirect('addheartexam', patients.id)

    context = {'page4': page4,
               'patients': patients,
               'examrec': examrec}
    return render(request, 'accounts/laboratory_dashboard.html', context)


# Here we are going to update and save laboratory exam results
def EditHeartLabResults(request, id):
    page4 = 'labdash4'
    patients = Heart_Medical_History.objects.get(pk=id)
    examrec = HeartMedicalHistoryForm(instance=patients)

    if request.method == 'POST':
        examrec = HeartMedicalHistoryForm(request.POST, instance=patients)
        if examrec.is_valid():
            examrec.save(commit=True)
            messages.success(
                request, f'Heart Exam Results of {patients.patient.first_name} Updated Successfully...')
            return redirect('heartlabresult')
        else:
            messages.error(request, 'Error Occured! Please Try again...')
            return redirect('addheartexam', patients.id)

    context = {'page4': page4,
               'patients': patients,
               'examrec': examrec}
    return render(request, 'accounts/laboratory_dashboard.html', context)

# ======================= LABORATORY PART END============


# ======================= HEART DEPARTMENT =======
def FinalTestResultsView(request):
    page2 = 'heartdash2'
    examresult = Heart_Medical_History.objects.all().order_by('-id')
    context = {'page2': page2,
               'examresult': examresult}
    return render(request, 'accounts/heart_dashboard.html', context)


# Here we view the data sent from Consult department to Heart Department
def RecordsFromConsultView(request):
    page3 = 'heartdash3'
    patientrec = RecordsFromConsult.objects.filter(
        patient__disease__name='Heart')
    context = {'page3': page3,
               'patientrec': patientrec}
    return render(request, 'accounts/heart_dashboard.html', context)


# We are deleting the data from consult department
def HeartDeleteConsultRecord(request, id):
    record = RecordsFromConsult.objects.get(pk=id)
    record.delete()
    return redirect('fromconsult')
# Command to send data to laboratory


def HeartSendToLabTest(request, id):
    fromcons = RecordsFromConsult.objects.get(pk=id)
    testrec = Assigned_Test_from_Doctor_dep.objects.create(
        patient=fromcons.patient)
    testrec.save()
    if True:
        fromcons.delete()
        messages.success(request, 'Records Sent to Laboratory Successfully...')
        return redirect('viewheartlab')


# View the record sent to laboratory
def ViewHeartSendToLabTest(request):
    page4 = 'heartdash4'
    patientrectest = Assigned_Test_from_Doctor_dep.objects.filter(
        patient__disease__name='Heart')
    context = {'page4': page4,
               'patientrectest': patientrectest}
    return render(request, 'accounts/heart_dashboard.html', context)


# Make Heart Disease Predictions
def HeartPredictView(request, id):
    page5 = 'heartdash5'
    patient_data = Heart_Medical_History.objects.get(pk=id)
    # load columns to be fitted in mode
    Age = int(patient_data.age)
    Sex = int(patient_data.sex)
    ChestPainType = int(patient_data.chestpaintype)
    RestingBP = int(patient_data.restingbp)
    Cholesterol = int(patient_data.cholesterol)
    FastingBS = int(patient_data.fastingbs)
    RestingECG = int(patient_data.restingecg)
    MaxHR = int(patient_data.maxhr)
    ExerciseAngina = int(patient_data.exerciseangina)
    Oldpeak = float(patient_data.oldpeak)
    ST_Slope = int(patient_data.st_slope)

    test_data = np.array(
        [[Age, Sex, ChestPainType, RestingBP, Cholesterol, FastingBS,
          RestingECG, MaxHR, ExerciseAngina, Oldpeak, ST_Slope]])
    # Call model to make a prediction
    model = pickle.load(open('./predictions/heart_model.pkl', 'rb'))
    # We cal fetch the output
    result = model.predict(test_data)
    predict_probability = model.predict_proba(test_data)
    prob_no_disease = predict_probability[0][0]
    prob_has_disease = predict_probability[0][1]

    # Here we automatically save the data to database
    patient_data.heartdisease = result[0]
    patient_data.save(force_update=True)

    context = {'page5': page5,
               'patient_data': patient_data,
               'result': result,
               'prob_no_disease': prob_no_disease,
               'prob_has_disease': prob_has_disease}
    return render(request, 'accounts/heart_dashboard.html', context)
# ======================= HEART DEPARTMENT END =====


# ================== Turn HTML to PDF to generate report =====

def PrintPatientResult(request):
    # Retrieve the data from the model
    data = Heart_Medical_History.objects.all()

    # Load the template
    template = get_template('accounts/heart_report.html')

    # Render the data
    context = {'data': data}
    rendered_template = template.render(context)

    # Create a PDF object
    pdf = HttpResponse(content_type='application/pdf')
    pdf['Content-Disposition'] = 'attachment; filename="Heart Treament Department Summary Report.pdf"'

    # Convert the HTML template into PDF
    pisa_status = pisa.CreatePDF(rendered_template, dest=pdf)

    # If PDF generation failed, return an error
    if pisa_status.err:
        return HttpResponse('PDF creation error')

    return pdf
