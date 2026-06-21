from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import random
import bcrypt
import stripe
import anthropic
from groq import Groq

from django.urls import reverse
from django.utils import timezone
from .models import (
    User, Doctor, Appointment, Bill, Message, MedicalRecord,
    PasswordResetCode, Agent, PatientProfile, LabResult,
    PatientFile, HealthSummary
)

# ─── Anthropic Client ───
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
groq_client = Groq(api_key=settings.GROQ_API_KEY)
stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── AI ───


@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            if not message:
                return JsonResponse({'error': 'No message'}, status=400)

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are MediBook AI Assistant - a helpful medical clinic assistant."},
                    {"role": "user", "content": message}
                ]
            )
            return JsonResponse({'reply': response.choices[0].message.content})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST only'}, status=405)


def summarize_patient_record(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Summarize the following patient record:\n\n{patient}"}]
    )
    return JsonResponse({'summary': response.choices[0].message.content})


# ─── Public Pages ───
def landing(request):
    doctors = Doctor.objects.all()[:3]
    return render(request, 'landing.html', {'doctors': doctors})


def about(request):
    doctors = Doctor.objects.all()
    return render(request, 'about.html', {'doctors': doctors})


def services_page(request):
    return render(request, 'services.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def terms_of_service(request):
    return render(request, 'terms_of_service.html')


def contact(request):
    return render(request, 'contact.html')


# ─── Patient Auth ───
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')
        errors = {}

        if not first_name:
            errors['first_name'] = 'First name is required'
        if not last_name:
            errors['last_name'] = 'Last name is required'
        if not email:
            errors['email'] = 'Email is required'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        if password != confirm:
            errors['confirm_password'] = 'Passwords do not match'

        if errors:
            return render(request, 'register.html', {'errors': errors, 'data': request.POST})

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            first_name=first_name, last_name=last_name,
            email=email, phone=phone, password=hashed, role='patient'
        )
        send_mail(
            'Welcome to MediBook!',
            f'Hi {first_name},\n\nYour account has been created successfully.\n\nMediBook Team',
            settings.EMAIL_HOST_USER, [email], fail_silently=True,
        )
        request.session['user_id']   = user.id
        request.session['user_name'] = user.first_name
        request.session['user_role'] = user.role
        return redirect('/dashboard/')

    return render(request, 'register.html')


def login_view(request):
    reset_success = request.GET.get('reset') == 'success'
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        errors   = {}

        if not email:
            errors['email'] = 'Email is required'
        if not password:
            errors['password'] = 'Password is required'

        if not errors:
            try:
                user = User.objects.get(email=email)
                if bcrypt.checkpw(password.encode(), user.password.encode()):
                    request.session['user_id']   = user.id
                    request.session['user_name'] = user.first_name
                    request.session['user_role'] = user.role
                    return redirect('/admin-dashboard/' if user.role == 'admin' else '/dashboard/')
                else:
                    errors['login'] = 'Invalid email or password'
            except User.DoesNotExist:
                errors['login'] = 'Invalid email or password'

        return render(request, 'login.html', {'errors': errors})

    return render(request, 'login.html', {'reset_success': reset_success})


def logout_view(request):
    request.session.flush()
    return redirect('/login/')


# ─── Patient Dashboard ───

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user = User.objects.get(id=request.session['user_id'])
    appointments = Appointment.objects.filter(patient=user).order_by('date')[:5]
    bills = Bill.objects.filter(patient=user, status='unpaid')
    return render(request, 'dashboard.html', {
        'user': user,
        'appointments': appointments,
        'bills': bills,
    })

def appointments(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user    = User.objects.get(id=request.session['user_id'])
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date      = request.POST.get('date')
        time      = request.POST.get('time')
        notes     = request.POST.get('notes', '')
        errors    = {}

        if not doctor_id: errors['doctor'] = 'Please select a doctor'
        if not date:      errors['date']   = 'Date is required'
        if not time:      errors['time']   = 'Time is required'

        if errors:
            appts = Appointment.objects.filter(patient=user).order_by('-created_at')
            return render(request, 'appointments.html', {
                'user': user, 'doctors': doctors,
                'appointments': appts, 'errors': errors, 'data': request.POST
            })

        doctor = Doctor.objects.get(id=doctor_id)
        Appointment.objects.create(
            patient=user, doctor=doctor, date=date, time=time, notes=notes
        )
        send_mail(
            'Appointment Confirmed - MediBook',
            f'Hi {user.first_name},\n\nYour appointment with Dr. {doctor.name} is confirmed.\nDate: {date}\nTime: {time}\n\nMediBook Team',
            settings.EMAIL_HOST_USER, [user.email], fail_silently=True,
        )
        return redirect('/appointments/')

    appts    = Appointment.objects.filter(patient=user).order_by('-created_at')
    upcoming = appts.filter(status__in=['pending', 'confirmed'])
    past     = appts.filter(status__in=['completed', 'cancelled'])
    return render(request, 'appointments.html', {
        'user': user, 'doctors': doctors, 'upcoming': upcoming, 'past': past,
    })

def add_appointment(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    if request.method == 'POST':
        appt = Appointment.objects.create(
            patient_id=request.POST['patient_id'],
            doctor_id=request.POST['doctor_id'],
            date=request.POST['date'],
            time=request.POST['time'],
            notes=request.POST.get('notes', ''),
            status='confirmed'
        )
        send_mail(
            'Appointment Confirmed - MediBook',
            (
                f'Hi {appt.patient.first_name},\n\n'
                f'Your appointment has been booked and confirmed.\n\n'
                f'Doctor: Dr. {appt.doctor.name} ({appt.doctor.specialization})\n'
                f'Date: {appt.date}\n'
                f'Time: {appt.time}\n'
                f'{("Notes: " + appt.notes) if appt.notes else ""}\n\n'
                f'If you have any questions, please contact us.\n\n'
                f'MediBook Team'
            ),
            settings.EMAIL_HOST_USER, [appt.patient.email], fail_silently=True,
        )
        return redirect('appointment_confirmation', appt_id=appt.id)
    return redirect('/agent-dashboard/')


def appointment_confirmation(request, appt_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    appt = get_object_or_404(Appointment, id=appt_id)
    return render(request, 'appointment_confirmation.html', {'appt': appt})


def patient_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments.html', {'appointments': appointments})

def cancel_appointment(request, appt_id):
    if 'user_id' not in request.session:
        return redirect('/login/')
    try:
        appt = Appointment.objects.get(id=appt_id, patient_id=request.session['user_id'])
        appt.status = 'cancelled'
        appt.save()
    except Appointment.DoesNotExist:
        pass
    return redirect('/appointments/')

def patient_billing(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user  = User.objects.get(id=request.session['user_id'])
    bills = Bill.objects.filter(patient=user).order_by('-created_at')
    return render(request, 'patient_billing.html', {'user': user, 'bills': bills})



def add_bill(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    if request.method == 'POST':
        bill = Bill.objects.create(
            patient_id=request.POST['patient_id'],
            amount=request.POST['amount'],
            due_date=request.POST['due_date'],
            description=request.POST.get('description', ''),
            status='unpaid'
        )
        return redirect('patient_bills_summary', patient_id=bill.patient_id)
    return redirect('/agent-dashboard/')


def patient_bills_summary(request, patient_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    patient = get_object_or_404(User, id=patient_id)
    bills        = Bill.objects.filter(patient=patient).order_by('-created_at')
    paid_bills   = bills.filter(status='paid')
    unpaid_bills = bills.filter(status__in=['unpaid', 'overdue'])
    paid_total   = sum((b.amount for b in paid_bills), 0)
    unpaid_total = sum((b.amount for b in unpaid_bills), 0)
    return render(request, 'patient_bills_summary.html', {
        'patient': patient,
        'bills': bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'paid_total': paid_total,
        'unpaid_total': unpaid_total,
    })


def messages_view(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user = User.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body    = request.POST.get('body', '').strip()
        errors  = {}
        if not subject: errors['subject'] = 'Subject is required'
        if not body:    errors['body']    = 'Message is required'
        if errors:
            msgs = Message.objects.filter(sender=user).order_by('-created_at')
            return render(request, 'patient_messages.html', {
                'user': user, 'messages': msgs, 'errors': errors, 'data': request.POST
            })
        Message.objects.create(sender=user, subject=subject, body=body)
        return redirect('/messages/')

    msgs = Message.objects.filter(sender=user).order_by('-created_at')
    return render(request, 'patient_messages.html', {'user': user, 'messages': msgs})


def agent_view_message(request, msg_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    msg = Message.objects.get(id=msg_id)
    msg.is_read = True
    msg.save()

    if request.method == 'POST':
        reply_text = request.POST.get('reply', '').strip()
        if reply_text:
            msg.reply = reply_text
            msg.is_replied = True
            msg.replied_at = timezone.now()
            msg.save()
            send_mail(
                f'Re: {msg.subject} - MediBook',
                f'Hi {msg.sender.first_name},\n\n{reply_text}\n\nMediBook Team',
                settings.EMAIL_HOST_USER, [msg.sender.email], fail_silently=True,
            )
        return redirect('agent_view_message', msg_id=msg.id)

    return render(request, 'agent_message_detail.html', {'msg': msg})



def message_count_api(request):
    if 'user_id' not in request.session:
        return JsonResponse({'count': 0})
    count = Message.objects.filter(
        sender_id=request.session['user_id'], is_read=False
    ).count()
    return JsonResponse({'count': count})


def health(request):
    if 'user_id' not in request.session:
        return redirect('/login/')
    user   = User.objects.get(id=request.session['user_id'])
    record, _ = MedicalRecord.objects.get_or_create(patient=user)
    return render(request, 'health.html', {'user': user, 'record': record})


# ─── Password Reset ───
def forgot_password(request):
    if request.method == 'POST':
        email  = request.POST.get('email', '').strip()
        errors = {}
        if not email:
            errors['email'] = 'Email is required'
        else:
            try:
                user = User.objects.get(email=email)
                code = str(random.randint(100000, 999999))
                PasswordResetCode.objects.create(user=user, code=code)
                try:
                    send_mail(
                        'MediBook - Password Reset Code',
                        f'Hi {user.first_name},\n\nYour password reset code is:\n\n{code}\n\nExpires in 10 minutes.\n\nMediBook Team',
                        settings.EMAIL_HOST_USER, [email], fail_silently=False,
                    )
                except Exception:
                    errors['email'] = 'Failed to send email. Please try again.'
                    return render(request, 'forgot_password.html', {'errors': errors})
            except User.DoesNotExist:
                pass
            request.session['reset_email'] = email
            return redirect('/reset-code/')
        return render(request, 'forgot_password.html', {'errors': errors})
    return render(request, 'forgot_password.html')


def reset_code(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('/forgot-password/')

    if request.method == 'POST':
        code   = request.POST.get('code', '').strip()
        errors = {}
        if not code or len(code) != 6:
            errors['code'] = 'Please enter the 6-digit code'
            return render(request, 'reset_code.html', {'errors': errors})
        try:
            user  = User.objects.get(email=email)
            reset = PasswordResetCode.objects.filter(user=user, code=code, is_used=False).last()
            if not reset:
                errors['code'] = 'Invalid code. Please try again.'
            elif reset.is_expired():
                errors['code'] = 'Code has expired. Please request a new one.'
            else:
                reset.is_used = True
                reset.save()
                request.session['reset_verified'] = True
                return redirect('/reset-password/')
        except User.DoesNotExist:
            errors['code'] = 'Invalid code.'
        return render(request, 'reset_code.html', {'errors': errors})
    return render(request, 'reset_code.html')


def reset_password(request):
    email    = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    if not email or not verified:
        return redirect('/forgot-password/')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm  = request.POST.get('confirm_password', '')
        errors   = {}
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        if password != confirm:
            errors['confirm_password'] = 'Passwords do not match'
        if errors:
            return render(request, 'reset_password.html', {'errors': errors})
        try:
            user = User.objects.get(email=email)
            user.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user.save()
            del request.session['reset_email']
            del request.session['reset_verified']
            return redirect('/login/?reset=success')
        except User.DoesNotExist:
            return redirect('/forgot-password/')
    return render(request, 'reset_password.html')


def resend_code(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('/forgot-password/')
    try:
        user = User.objects.get(email=email)
        code = str(random.randint(100000, 999999))
        PasswordResetCode.objects.create(user=user, code=code)
        send_mail(
            'MediBook - New Password Reset Code',
            f'Hi {user.first_name},\n\nYour new reset code is:\n\n{code}\n\nExpires in 10 minutes.\n\nMediBook Team',
            settings.EMAIL_HOST_USER, [email], fail_silently=True,
        )
    except User.DoesNotExist:
        pass
    return redirect('/reset-code/')


# ─── Agent Auth ───
def agent_login(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id', '').strip()
        password = request.POST.get('password', '')
        errors   = {}
        if not agent_id: errors['agent_id']  = 'Agent ID is required'
        if not password: errors['password']  = 'Password is required'
        if not errors:
            try:
                agent = Agent.objects.get(agent_id=agent_id)
                if bcrypt.checkpw(password.encode(), agent.password.encode()):
                    request.session['agent_id']   = agent.id
                    request.session['agent_name'] = agent.first_name
                    request.session['agent_code'] = agent.agent_id
                    return redirect('/agent-dashboard/')
                else:
                    errors['login'] = 'Invalid Agent ID or password'
            except Agent.DoesNotExist:
                errors['login'] = 'Invalid Agent ID or password'
        return render(request, 'agent_login.html', {'errors': errors})
    return render(request, 'agent_login.html')


def agent_register(request):
    if request.method == 'POST':
        agent_id   = request.POST.get('agent_id', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')
        errors     = {}

        if not agent_id:
            errors['agent_id'] = 'Agent ID is required'
        elif Agent.objects.filter(agent_id=agent_id).exists():
            errors['agent_id'] = 'Agent ID already exists'
        if not first_name: errors['first_name'] = 'First name is required'
        if not last_name:  errors['last_name']  = 'Last name is required'
        if not email:
            errors['email'] = 'Email is required'
        elif Agent.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        if password != confirm:
            errors['confirm_password'] = 'Passwords do not match'

        if errors:
            return render(request, 'agent_register.html', {'errors': errors, 'data': request.POST})

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        Agent.objects.create(
            agent_id=agent_id, first_name=first_name, last_name=last_name,
            email=email, phone=phone, password=hashed
        )
        return redirect('/agent-login/')
    return render(request, 'agent_register.html')


def agent_logout(request):
    request.session.flush()
    return redirect('/agent-login/')


# ─── Agent Dashboard ───
def agent_dashboard(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    agent        = Agent.objects.get(id=request.session['agent_id'])
    patients     = User.objects.filter(role='patient')
    doctors      = Doctor.objects.all()
    appointments = Appointment.objects.all().order_by('-created_at')[:10]
    bills        = Bill.objects.all().order_by('-created_at')[:10]
    messages_all = Message.objects.all().order_by('-created_at')[:10]
    return render(request, 'agent_dashboard.html', {
        'agent': agent,
        'patients': patients,
        'doctors': doctors,
        'appointments': appointments,
        'bills': bills,
        'messages': messages_all,
        'total_patients': patients.count(),
        'total_doctors': doctors.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_bills': Bill.objects.filter(status='unpaid').count(),
        'unread_messages': Message.objects.filter(is_read=False).count(),
        'today': datetime.today().date().isoformat(),
    })

def patients_list(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    patients = User.objects.filter(role='patient')
    return render(request, 'patients_list.html', {'patients': patients})


def agent_add_patient(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', 'medibook123')
        errors     = {}
        if not first_name: errors['first_name'] = 'Required'
        if not last_name:  errors['last_name']  = 'Required'
        if not email:
            errors['email'] = 'Required'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists'
        if errors:
            return render(request, 'agent_add_patient.html', {'errors': errors, 'data': request.POST})
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        patient = User.objects.create(
            first_name=first_name, last_name=last_name,
            email=email, phone=phone, password=hashed, role='patient'
        )
        return redirect('patient_added_confirmation', patient_id=patient.id)
    return render(request, 'agent_add_patient.html')


def patient_added_confirmation(request, patient_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    patient = get_object_or_404(User, id=patient_id)
    return render(request, 'patient_added_confirmation.html', {'patient': patient})

def doctors_list(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    doctors = Doctor.objects.all()
    return render(request, 'doctors_list.html', {'doctors': doctors})


def agent_add_doctor(request):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    if request.method == 'POST':
        name           = request.POST.get('name', '').strip()
        specialization = request.POST.get('specialization', '').strip()
        email          = request.POST.get('email', '').strip()
        phone          = request.POST.get('phone', '').strip()
        bio            = request.POST.get('bio', '').strip()
        if name and specialization and email:
            doctor = Doctor.objects.create(
                name=name, specialization=specialization,
                email=email, phone=phone, bio=bio
            )
            return redirect('doctor_added_confirmation', doctor_id=doctor.id)
    return redirect('/agent-dashboard/')


def doctor_added_confirmation(request, doctor_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'doctor_added_confirmation.html', {'doctor': doctor})

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.name = request.POST.get('name', doctor.name)
        doctor.specialization = request.POST.get('specialization', doctor.specialization)
        doctor.email = request.POST.get('email', doctor.email)
        doctor.phone = request.POST.get('phone', doctor.phone)
        doctor.bio = request.POST.get('bio', doctor.bio)
        doctor.save()
        return redirect(f'/agent-dashboard/doctors/?success=1')  
    return render(request, 'doctor_detail.html', {'doctor': doctor})


def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        doctor.delete()
        return redirect('doctors_list')
    return redirect('doctor_detail', doctor_id=doctor_id)


# ─── Agent Patient Profile ───
def agent_patient_profile(request, patient_id):
    if 'agent_id' not in request.session:
        return redirect('/agent-login/')
    
    patient      = get_object_or_404(User, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date')
    bills        = Bill.objects.filter(patient=patient).order_by('-created_at')
    messages     = Message.objects.filter(sender=patient).order_by('-created_at')
    record, _    = MedicalRecord.objects.get_or_create(patient=patient)
    health, _    = HealthSummary.objects.get_or_create(patient=patient)
    profile, _   = PatientProfile.objects.get_or_create(patient=patient)
    doctors      = Doctor.objects.all()
    blood_types  = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    lab_results  = LabResult.objects.filter(patient=patient).order_by('-test_date')
    patient_files = PatientFile.objects.filter(patient=patient).order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            patient.first_name = request.POST.get('first_name', patient.first_name)
            patient.last_name  = request.POST.get('last_name', patient.last_name)
            patient.phone      = request.POST.get('phone', patient.phone)
            patient.save()
            profile.address                 = request.POST.get('address', '')
            profile.date_of_birth           = request.POST.get('date_of_birth') or None
            profile.gender                  = request.POST.get('gender', '')
            profile.blood_type              = request.POST.get('blood_type', '')
            profile.allergies               = request.POST.get('allergies', '')
            profile.insurance_provider      = request.POST.get('insurance_provider', '')
            profile.insurance_number        = request.POST.get('insurance_number', '')
            profile.insurance_expiry        = request.POST.get('insurance_expiry') or None
            profile.emergency_contact_name  = request.POST.get('emergency_contact_name', '')
            profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
            if request.FILES.get('profile_picture'):
                profile.profile_picture = request.FILES['profile_picture']
            profile.save()

        elif action == 'update_health':
            health.chief_complaint = request.POST.get('chief_complaint', '')
            health.diagnosis       = request.POST.get('diagnosis', '')
            health.treatment_plan  = request.POST.get('treatment_plan', '')
            health.vitals_bp       = request.POST.get('vitals_bp', '')
            health.vitals_pulse    = request.POST.get('vitals_pulse', '')
            health.vitals_temp     = request.POST.get('vitals_temp', '')
            health.vitals_weight   = request.POST.get('vitals_weight', '')
            health.vitals_height   = request.POST.get('vitals_height', '')
            health.save()

        elif action == 'update_record':
            record.medications = request.POST.get('medications', '')
            record.conditions  = request.POST.get('conditions', '')
            record.procedures  = request.POST.get('procedures', '')
            record.notes       = request.POST.get('notes', '')
            record.save()

        elif action == 'add_appointment':
            doctor_id = request.POST.get('doctor_id')
            date      = request.POST.get('date')
            time      = request.POST.get('time')
            if doctor_id and date and time:
                Appointment.objects.create(
                    patient=patient, doctor_id=doctor_id,
                    date=date, time=time, notes=request.POST.get('notes', '')
                )

        elif action == 'add_bill':
            amount   = request.POST.get('amount')
            due_date = request.POST.get('due_date')
            if amount and due_date:
                Bill.objects.create(
                    patient=patient, amount=amount,
                    due_date=due_date,
                    description=request.POST.get('description', '')
                )

        elif action == 'update_appt_status':
            Appointment.objects.filter(id=request.POST.get('appt_id')).update(
                status=request.POST.get('status')
            )

        elif action == 'mark_paid':
            Bill.objects.filter(id=request.POST.get('bill_id')).update(status='paid')

        elif action == 'send_message':
            subject = request.POST.get('subject', '')
            body    = request.POST.get('body', '')
            if subject and body:
                Message.objects.create(
                    sender=patient, subject=f"[Admin] {subject}",
                    body=body, is_read=True
                )

        elif action == 'add_lab':
            LabResult.objects.create(
                patient=patient,
                test_name=request.POST.get('test_name', ''),
                result=request.POST.get('result', ''),
                normal_range=request.POST.get('normal_range', ''),
                status=request.POST.get('lab_status', 'pending'),
                test_date=request.POST.get('test_date'),
                notes=request.POST.get('lab_notes', ''),
                file=request.FILES.get('lab_file'),
            )

        elif action == 'delete_lab':
            LabResult.objects.filter(
                id=request.POST.get('lab_id'), patient=patient
            ).delete()

        elif action == 'add_file':
            f = request.FILES.get('patient_file')
            if f:
                PatientFile.objects.create(
                    patient=patient,
                    name=request.POST.get('file_name', f.name),
                    file=f, file_type=f.content_type, uploaded_by='agent'
                )

        return redirect('/agent-dashboard/?saved=1')
    return render(request, 'agent_patient_profile.html', {
        'patient': patient, 'appointments': appointments,
        'bills': bills, 'messages': messages,
        'record': record, 'health': health, 'profile': profile,
        'doctors': doctors, 'blood_types': blood_types,
        'lab_results': lab_results, 'patient_files': patient_files,
        'today': datetime.today().date().isoformat(),
    })
    
    
def delete_patient(request, patient_id):
    patient = get_object_or_404(User, id=patient_id)
    if request.method == 'POST':
        patient_name = f"{patient.first_name} {patient.last_name}"
        patient.delete()
        return redirect(f"{reverse('patients_list')}?deleted={patient_name}")
    return redirect('patients_list')


def agent_update_appointment(request, appt_id):
    if 'agent_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    if request.method == 'POST':
        Appointment.objects.filter(id=appt_id).update(status=request.POST.get('status'))
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid'}, status=400)


def available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date      = request.GET.get('date')
    all_slots = [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '14:00', '14:30', '15:00', '15:30',
        '16:00', '16:30', '17:00'
    ]
    booked = Appointment.objects.filter(
        doctor_id=doctor_id, date=date, status__in=['pending', 'confirmed']
    ).values_list('time', flat=True)
    booked_str = [t.strftime('%H:%M') for t in booked]
    available  = [s for s in all_slots if s not in booked_str]
    return JsonResponse({'slots': available})




# ─── Stripe Payments ───
def create_checkout_session(request, bill_id):
    bill    = get_object_or_404(Bill, id=bill_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'MediBook - Bill #{bill.id}'},
                'unit_amount': int(bill.amount * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/payment-success/{bill.id}/'),
        cancel_url=request.build_absolute_uri(f'/payment-cancel/{bill.id}/'),
    )
    return redirect(session.url, code=303)


def payment_success(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    bill.status = 'paid'
    bill.save()
    return render(request, 'payment_success.html', {'bill': bill})


def payment_cancel(request, bill_id):
    return render(request, 'payment_cancel.html')