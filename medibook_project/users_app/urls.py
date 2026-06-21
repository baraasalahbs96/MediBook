from django.urls import path
from . import views

urlpatterns = [
    # ─── Public ───
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('services/', views.services_page, name='services'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),

    # ─── Patient Auth ───
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ─── Patient Portal ───
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/cancel/<int:appt_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('messages/', views.messages_view, name='messages'),
    path('health/', views.health, name='health'),
    path('billing/', views.patient_billing, name='patient_billing'),

    # ─── Password Reset ───
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-code/', views.reset_code, name='reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-code/', views.resend_code, name='resend_code'),

    # ─── Stripe Payments ───
    path('checkout/<int:bill_id>/', views.create_checkout_session, name='checkout_session'),
    path('payment-success/<int:bill_id>/', views.payment_success, name='payment_success'),
    path('payment-cancel/<int:bill_id>/', views.payment_cancel, name='payment_cancel'),

    # ─── Agent Auth ───
    path('agent-login/', views.agent_login, name='agent_login'),
    path('agent-register/', views.agent_register, name='agent_register'),
    path('agent-logout/', views.agent_logout, name='agent_logout'),

    # ─── Agent Dashboard ───
    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent-dashboard/doctors/', views.doctors_list, name='doctors_list'),
    path('agent-dashboard/doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('agent-dashboard/doctor/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    path('agent-dashboard/add-patient/', views.agent_add_patient, name='agent_add_patient'),
    path('agent-dashboard/patient/<int:patient_id>/added/', views.patient_added_confirmation, name='patient_added_confirmation'),
    path('agent-dashboard/patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('agent-dashboard/patients/', views.patients_list, name='patients_list'),
    path('agent-dashboard/add-doctor/', views.agent_add_doctor, name='agent_add_doctor'),
    path('agent-dashboard/doctor/<int:doctor_id>/added/', views.doctor_added_confirmation, name='doctor_added_confirmation'),
    path('agent-dashboard/add-appointment/', views.add_appointment, name='add_appointment'),
    path('agent-dashboard/appointment/<int:appt_id>/confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
    path('agent-dashboard/add-bill/', views.add_bill, name='add_bill'),
    path('agent-dashboard/patient/<int:patient_id>/bills/', views.patient_bills_summary, name='patient_bills_summary'),
    path('agent-dashboard/message/<int:msg_id>/', views.agent_view_message, name='agent_view_message'),
    path('agent-dashboard/available-slots/', views.available_slots, name='available_slots'),
    path('agent-dashboard/appointment/<int:appt_id>/update/', views.agent_update_appointment, name='agent_update_appointment'),

    # ─── Agent Patient Profile ───
    path('agent-dashboard/patient/<int:patient_id>/', views.agent_patient_profile, name='agent_patient_profile'),

    # ─── API ───
    path('api/message-count/', views.message_count_api, name='message_count'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('summarize-patient/<int:patient_id>/', views.summarize_patient_record, name='summarize_patient'),
]