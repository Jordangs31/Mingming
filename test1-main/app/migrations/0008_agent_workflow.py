# Generated manually for the agent and broker workflow.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('app', '0007_property_approval_status_and_more')]

    operations = [
        migrations.AddField(model_name='property', name='rejection_reason', field=models.TextField(blank=True)),
        migrations.CreateModel(
            name='AgentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='agent_profiles/')),
                ('title', models.CharField(default='Licensed Real Estate Agent', max_length=120)),
                ('license_number', models.CharField(blank=True, max_length=80)),
                ('biography', models.TextField(blank=True)), ('location', models.CharField(blank=True, max_length=150)),
                ('years_experience', models.PositiveIntegerField(default=0)), ('specializations', models.CharField(blank=True, max_length=255)),
                ('languages', models.CharField(blank=True, max_length=255)), ('office_location', models.CharField(blank=True, max_length=255)),
                ('working_hours', models.CharField(default='Mon–Fri, 9:00 AM–5:00 PM', max_length=150)),
                ('rating', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='agent_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(max_length=150)), ('email', models.EmailField(max_length=254)), ('contact_number', models.CharField(blank=True, max_length=30)),
                ('subject', models.CharField(max_length=200)), ('message', models.TextField()), ('response', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('new', 'New'), ('read', 'Read'), ('replied', 'Replied'), ('closed', 'Closed')], default='new', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_inquiries', to=settings.AUTH_USER_MODEL)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_inquiries', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inquiries', to='app.property')),
            ], options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(max_length=150)), ('buyer_email', models.EmailField(max_length=254)), ('date', models.DateField()), ('time', models.TimeField()),
                ('appointment_type', models.CharField(choices=[('viewing', 'Property Viewing'), ('office', 'Office Meeting'), ('online', 'Online Meeting'), ('consultation', 'Consultation')], default='viewing', max_length=20)),
                ('notes', models.TextField(blank=True)), ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_appointments', to=settings.AUTH_USER_MODEL)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='buyer_appointments', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments', to='app.property')),
            ], options={'ordering': ['date', 'time']},
        ),
        migrations.AddConstraint(model_name='appointment', constraint=models.UniqueConstraint(fields=('agent', 'date', 'time'), name='unique_agent_appointment_slot')),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('message', models.CharField(max_length=255)),
                ('link', models.CharField(blank=True, max_length=255)), ('is_read', models.BooleanField(default=False)), ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ], options={'ordering': ['-created_at']},
        ),
    ]
