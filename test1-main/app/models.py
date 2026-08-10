from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):

    phone = models.CharField(max_length=15, blank=True, null=True)

    USER_TYPE = (
        ('buyer', 'Buyer'),
        ('agent', 'Agent'),
        ('broker', 'Broker'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE, default='buyer')

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
class Property(models.Model):

    PROPERTY_TYPE = [
        ('house_lot', 'House and Lot'),
    ]

    LISTING_STATUS = [
        ('sale', 'For Sale'),
        ('sold', 'Sold'),
    ]

    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE,
        default='house_lot'
    )

    listing_status = models.CharField(
        max_length=10,
        choices=LISTING_STATUS,
        default='sale'
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)

    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)

    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()

    floor_area = models.DecimalField(max_digits=10, decimal_places=2)
    lot_area = models.DecimalField(max_digits=10, decimal_places=2)

    parking_spaces = models.IntegerField(default=0)

    image = models.ImageField(upload_to='property_images/', blank=True, null=True)

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_available = models.BooleanField(default=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"
    
class Review(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Partner(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/')
    website = models.URLField()

    def __str__(self):
        return self.name


class AgentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_profile')
    photo = models.ImageField(upload_to='agent_profiles/', blank=True, null=True)
    title = models.CharField(max_length=120, default='Licensed Real Estate Agent')
    license_number = models.CharField(max_length=80, blank=True)
    biography = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    specializations = models.CharField(max_length=255, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    office_location = models.CharField(max_length=255, blank=True)
    working_hours = models.CharField(max_length=150, default='Mon–Fri, 9:00 AM–5:00 PM')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f'Profile: {self.user}'


class Inquiry(models.Model):
    STATUS = [('new', 'New'), ('read', 'Read'), ('replied', 'Replied'), ('closed', 'Closed')]
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_inquiries')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_inquiries')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    buyer_name = models.CharField(max_length=150)
    email = models.EmailField()
    contact_number = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    response = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Appointment(models.Model):
    TYPE = [('viewing', 'Property Viewing'), ('office', 'Office Meeting'), ('online', 'Online Meeting'), ('consultation', 'Consultation')]
    STATUS = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyer_appointments')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_appointments')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=TYPE, default='viewing')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['agent', 'date', 'time'], name='unique_agent_appointment_slot')]
        ordering = ['date', 'time']


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
