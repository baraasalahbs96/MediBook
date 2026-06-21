from django.db import models
from django.utils import timezone


# ─── Patient (User) ───
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=255)
    phone      = models.CharField(max_length=20, blank=True)
    role       = models.CharField(max_length=20, default='patient')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PatientProfile(models.Model):
    patient                 = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address                 = models.CharField(max_length=255, blank=True)
    date_of_birth           = models.DateField(null=True, blank=True)
    gender                  = models.CharField(max_length=10, blank=True)
    profile_picture         = models.ImageField(upload_to='profiles/', blank=True, null=True)
    blood_type              = models.CharField(max_length=5, blank=True)
    allergies               = models.TextField(blank=True)
    insurance_provider      = models.CharField(max_length=100, blank=True)
    insurance_number        = models.CharField(max_length=100, blank=True)
    insurance_expiry        = models.DateField(null=True, blank=True)
    emergency_contact_name  = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.patient.first_name}"


class MedicalRecord(models.Model):
    patient     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_record')
    medications = models.TextField(blank=True)
    conditions  = models.TextField(blank=True)
    procedures  = models.TextField(blank=True)
    notes       = models.TextField(blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record - {self.patient.first_name}"


class HealthSummary(models.Model):
    patient         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_summary')
    chief_complaint = models.TextField(blank=True)
    diagnosis       = models.TextField(blank=True)
    treatment_plan  = models.TextField(blank=True)
    vitals_bp       = models.CharField(max_length=20, blank=True)
    vitals_pulse    = models.CharField(max_length=20, blank=True)
    vitals_temp     = models.CharField(max_length=20, blank=True)
    vitals_weight   = models.CharField(max_length=20, blank=True)
    vitals_height   = models.CharField(max_length=20, blank=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health - {self.patient.first_name}"


# ─── Doctor ───
class Doctor(models.Model):
    name           = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=20, blank=True)
    bio            = models.TextField(blank=True)
    image          = models.CharField(max_length=255, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─── Agent ───
class Agent(models.Model):
    agent_id   = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=255)
    phone      = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent_id} - {self.first_name} {self.last_name}"


# ─── Appointment ───
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    patient       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor        = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date          = models.DateField()
    time          = models.TimeField()
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes         = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.date}"


# ─── Billing ───
class Bill(models.Model):
    STATUS_CHOICES = [
        ('unpaid',  'Unpaid'),
        ('paid',    'Paid'),
        ('overdue', 'Overdue'),
    ]
    patient     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    due_date    = models.DateField()
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - ${self.amount}"


# ─── Messaging ───
class Message(models.Model):
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    subject    = models.CharField(max_length=255)
    body       = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    reply      = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    is_replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.subject}"


# ─── Lab & Files ───
class LabResult(models.Model):
    STATUS_CHOICES = [
        ('normal',   'Normal'),
        ('abnormal', 'Abnormal'),
        ('pending',  'Pending'),
    ]
    patient      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_results')
    test_name    = models.CharField(max_length=200)
    result       = models.TextField()
    normal_range = models.CharField(max_length=100, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    test_date    = models.DateField()
    notes        = models.TextField(blank=True)
    file         = models.FileField(upload_to='lab_results/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.test_name}"


class PatientFile(models.Model):
    patient     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    name        = models.CharField(max_length=200)
    file        = models.FileField(upload_to='patient_files/')
    file_type   = models.CharField(max_length=50, blank=True)
    uploaded_by = models.CharField(max_length=50, default='agent')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.name}"


class PatientDocument(models.Model):
    patient     = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='documents')
    file        = models.FileField(upload_to='patient_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc - {self.patient}"


# ─── Password Reset ───
class PasswordResetCode(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 600

    def __str__(self):
        return f"{self.user.email} - {self.code}"