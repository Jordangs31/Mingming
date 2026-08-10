from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import CustomUser, Property, PropertyImage, Review, Partner, Inquiry, Appointment, Notification
from django.contrib.auth.decorators import login_required
from django.views import View 
from .forms import PropertyForm, ReviewForm, InquiryForm, AppointmentForm
from django.db import IntegrityError
from django.db.models import Count, Q
from django.utils import timezone
from django.core.exceptions import PermissionDenied

# LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass')

        # authenticate uses username by default, so if email is your login field:
        try:
            from .models import CustomUser
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name} ({user.user_type})!")

            # Redirect based on user_type
            if user.user_type == 'broker':
                return redirect('broker_dashboard')
            elif user.user_type == 'agent':
                return redirect('agent_dashboard')
            else:  # buyer
                return redirect('buyer_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

# REGISTER VIEW
def register_view(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        confirm_password = request.POST.get('c_pass')
        user_type = request.POST.get('user_type')  # Get role from dropdown

        # 1️⃣ Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        # 2️⃣ Check if email already exists
        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'register.html')

        # 3️⃣ Create user
        user = CustomUser.objects.create_user(
            username=email,      # Using email as username
            email=email,
            password=password,
            first_name=name,
            user_type=user_type,  # Save role
            is_verified=False     # Optional: admin verification
        )

        user.save()

        messages.success(request, "Account created successfully! Please wait for verification if you are an Agent or Broker.")
        return redirect('login')

    return render(request, 'register.html')

# -------------------------
# broker Dashboard Views
# -------------------------
class BrokerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'broker_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.user_type not in ('broker',) and not self.request.user.is_staff:
            raise PermissionDenied

        # Get ACTIVE agents only
        agents = CustomUser.objects.filter(
            user_type='agent',
            is_active=True
        )

        properties = Property.objects.all()
        context.update({
            'agents': agents, 'total_agents': CustomUser.objects.filter(user_type='agent').count(),
            'total_properties': properties.count(), 'active_listings': properties.filter(approval_status='approved', listing_status='sale').count(),
            'pending_approvals': properties.filter(approval_status='pending').count(), 'sold_properties': properties.filter(listing_status='sold').count(),
            'total_inquiries': Inquiry.objects.count(), 'upcoming_appointments': Appointment.objects.filter(date__gte=timezone.localdate()).count(),
            'recent_submissions': properties.filter(approval_status='pending').select_related('agent')[:6],
        })
        return context

class ManageAgentsView(LoginRequiredMixin, View):
    """
    View for broker to manage all agents.
    Requires user to be logged in.
    """
    def get(self, request, *args, **kwargs):
        agents = CustomUser.objects.filter(user_type='agent').order_by('-date_joined')
        context = {
            'title': 'Manage Agents',
            'user_type': request.user.user_type,
            'agents': agents,
            'active_agents': agents.filter(is_active=True).count(),
            'verified_agents': agents.filter(is_verified=True).count(),
        }
        return render(request, 'broker/manage_agents.html', context)


class ManagepropertiesView(LoginRequiredMixin, View):
    """
    View for broker to manage all property listings.
    Requires user to be logged in.
    """
    def get(self, request, *args, **kwargs):
        properties = Property.objects.select_related('agent').order_by('-created_at')
        context = {
            'title': 'Manage Properties',
            'user_type': request.user.user_type,
            'properties': properties,
            'pending_properties': properties.filter(approval_status='pending'),
            'approved_properties': properties.filter(approval_status='approved'),
            'rejected_properties': properties.filter(approval_status='rejected'),
        }
        return render(request, 'broker/manage_properties.html', context)


@login_required
def agent_dashboard_view(request):
    if request.user.user_type != 'agent' and not request.user.is_staff:
        messages.error(request, 'This dashboard is only available to agents.')
        return redirect('home')
    buyers = CustomUser.objects.filter(user_type="buyer")
    properties = Property.objects.filter(agent=request.user)
    context = {
        "buyers": buyers,
        "properties": properties,
        'total_listings': properties.count(), 'active_listings': properties.filter(approval_status='approved', listing_status='sale').count(),
        'sold_properties': properties.filter(listing_status='sold').count(), 'pending_properties': properties.filter(approval_status='pending').count(),
        'inquiries': Inquiry.objects.filter(agent=request.user)[:6], 'total_inquiries': Inquiry.objects.filter(agent=request.user).count(),
        'upcoming_appointments': Appointment.objects.filter(agent=request.user, date__gte=timezone.localdate()).count(),
        'appointments': Appointment.objects.filter(agent=request.user, date__gte=timezone.localdate())[:5],
        'notifications': Notification.objects.filter(recipient=request.user)[:5],
    }
    return render(request, "agent_dashboard.html", context)

@login_required
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.agent = request.user
            property_instance.save()

            # ✅ SAVE MULTIPLE IMAGES
            images = request.FILES.getlist('images')
            for img in images:
                PropertyImage.objects.create(
                    property=property_instance,
                    image=img
                )

            return redirect("agent_dashboard")
        else:
            print(form.errors)
    else:
        form = PropertyForm()

    return render(request, "agent/add_property.html", {"form": form})

@login_required
def edit_property(request, id):
    """
    Allows an agent to edit their own property listing.
    """
    # Make sure property belongs to the logged-in agent
    property_instance = get_object_or_404(Property, id=id, agent=request.user)

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            form.save()

             # ✅ ADD NEW IMAGES (DOES NOT DELETE OLD ONES)
            images = request.FILES.getlist('images')
            for img in images:
                PropertyImage.objects.create(
                    property=property_instance,
                    image=img
                )
            messages.success(request, "Property updated successfully!")
            return redirect("agent_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm(instance=property_instance)

    return render(request, "agent/edit_property.html", {"form": form, "property": property_instance})

@login_required
def delete_property(request, id):
    """
    Allows an agent to delete a property they own.
    """
    # Make sure the property belongs to the logged-in agent
    property_instance = get_object_or_404(Property, id=id, agent=request.user)
    
    if request.method == "POST":
        property_instance.delete()
        return redirect("agent_dashboard")
    
    # Optional: confirm deletion page
    return render(request, "agent/delete_property.html", {"property": property_instance})
# -------------------------
# Agent Dashboard Views
# -------------------------
def agents(request):
    agents = CustomUser.objects.filter(user_type='agent').select_related('agent_profile').annotate(
        listing_count=Count('property'), sold_count=Count('property', filter=Q(property__listing_status='sold'))
    )
    q = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    specialization = request.GET.get('specialization', '').strip()
    experience = request.GET.get('experience', '').strip()
    rating = request.GET.get('rating', '').strip()
    sort = request.GET.get('sort', 'name')
    if q: agents = agents.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    if location: agents = agents.filter(agent_profile__location__icontains=location)
    if specialization: agents = agents.filter(agent_profile__specializations__icontains=specialization)
    if experience.isdigit(): agents = agents.filter(agent_profile__years_experience__gte=int(experience))
    if rating: agents = agents.filter(agent_profile__rating__gte=rating)
    agents = agents.order_by({'rating': '-agent_profile__rating', 'experience': '-agent_profile__years_experience'}.get(sort, 'first_name'))

    return render(request, 'agent/agents.html', {
        'agents': agents, 'filters': request.GET
    })


def agent_profile_view(request, id):
    agent = get_object_or_404(CustomUser.objects.select_related('agent_profile'), id=id, user_type='agent')
    properties = Property.objects.filter(agent=agent, approval_status='approved', is_available=True).order_by('-created_at')
    return render(request, 'agent/profile.html', {'agent': agent, 'properties': properties, 'sold_count': Property.objects.filter(agent=agent, listing_status='sold').count(), 'inquiry_form': InquiryForm(), 'appointment_form': AppointmentForm()})


def contact_agent(request, id):
    agent = get_object_or_404(CustomUser, id=id, user_type='agent')
    if request.method != 'POST': return redirect('agent_profile', id=id)
    form = InquiryForm(request.POST)
    form.fields['property'].queryset = Property.objects.filter(agent=agent)
    if form.is_valid():
        inquiry = form.save(commit=False); inquiry.agent = agent
        if request.user.is_authenticated: inquiry.buyer = request.user
        inquiry.save()
        Notification.objects.create(recipient=agent, message=f'New inquiry from {inquiry.buyer_name}: {inquiry.subject}', link='/agent/inbox/')
        messages.success(request, 'Your inquiry has been sent successfully.')
    else: messages.error(request, 'Please correct the inquiry form and try again.')
    return redirect('agent_profile', id=id)


def schedule_appointment(request, id):
    agent = get_object_or_404(CustomUser, id=id, user_type='agent')
    if request.method != 'POST': return redirect('agent_profile', id=id)
    form = AppointmentForm(request.POST); form.fields['property'].queryset = Property.objects.filter(agent=agent)
    if form.is_valid():
        appointment = form.save(commit=False); appointment.agent = agent
        if request.user.is_authenticated: appointment.buyer = request.user
        try:
            appointment.save()
            Notification.objects.create(recipient=agent, message=f'New {appointment.get_appointment_type_display()} request from {appointment.buyer_name}', link='/agent/inbox/')
            if appointment.buyer: Notification.objects.create(recipient=appointment.buyer, message='Your appointment request has been received.')
            messages.success(request, 'Your appointment has been requested successfully.')
        except IntegrityError: messages.error(request, 'That agent is already booked at this date and time. Please choose another slot.')
    else: messages.error(request, 'Please enter a valid appointment date and time.')
    return redirect('agent_profile', id=id)


@login_required
def agent_inbox(request):
    if request.user.user_type != 'agent' and not request.user.is_staff: return redirect('home')
    inquiries = Inquiry.objects.filter(agent=request.user).select_related('property')
    if request.method == 'POST':
        inquiry = get_object_or_404(inquiries, id=request.POST.get('inquiry_id'))
        action = request.POST.get('action')
        if action == 'reply' and request.POST.get('response', '').strip():
            inquiry.response = request.POST['response'].strip(); inquiry.status = 'replied'; inquiry.save()
            if inquiry.buyer: Notification.objects.create(recipient=inquiry.buyer, message=f'Your agent replied to “{inquiry.subject}”.')
        elif action == 'close': inquiry.status = 'closed'; inquiry.save(update_fields=['status'])
        else: inquiry.status = 'read'; inquiry.save(update_fields=['status'])
        return redirect('agent_inbox')
    return render(request, 'agent/inbox.html', {'inquiries': inquiries, 'appointments': Appointment.objects.filter(agent=request.user)})


@login_required
def broker_property_decision(request, id, decision):
    if request.user.user_type != 'broker' and not request.user.is_staff: return redirect('home')
    if request.method != 'POST': return redirect('manage_properties')
    property_obj = get_object_or_404(Property, id=id)
    if decision == 'approve':
        property_obj.approval_status = 'approved'; property_obj.is_available = True; property_obj.rejection_reason = ''
        notice = f'Your property “{property_obj.title}” was approved.'
    else:
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'A rejection reason is required.'); return redirect('manage_properties')
        property_obj.approval_status = 'rejected'; property_obj.is_available = False; property_obj.rejection_reason = reason
        notice = f'Your property “{property_obj.title}” needs revision: {reason}'
    property_obj.save(); Notification.objects.create(recipient=property_obj.agent, message=notice, link='/agent/dashboard/')
    messages.success(request, f'Property {decision}d successfully.')
    return redirect('manage_properties')


@login_required
def broker_toggle_agent(request, id):
    if request.user.user_type != 'broker' and not request.user.is_staff: return redirect('home')
    if request.method == 'POST':
        agent = get_object_or_404(CustomUser, id=id, user_type='agent'); agent.is_active = not agent.is_active; agent.save(update_fields=['is_active'])
        messages.success(request, f'{agent.get_full_name() or agent.username} is now {"active" if agent.is_active else "inactive"}.')
    return redirect('manage_agents')

class AgentDashboardView(LoginRequiredMixin, View):
    """
    Dashboard main page for agents.
    """
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Agent Dashboard',
            'user_type': request.user.user_type,
        }
        return render(request, 'agent/agent_dashboard.html', context)


class ViewBuyersView(LoginRequiredMixin, View):
    """
    Page for agents to view buyer information.
    """
    def get(self, request, *args, **kwargs):
        # Replace this with your actual Buyer model query
        buyers = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '09123456789'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '09987654321'}
        ]
        context = {
            'title': 'View Buyers',
            'buyers': buyers,
            'user_type': request.user.user_type,
        }
        return render(request, 'agent/view_buyers.html', context)
    
class ListingsPageView(TemplateView):
    template_name = "agent/listings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["properties"] = Property.objects.filter(
            is_available=True
        ).order_by("-created_at")

        return context
    
class BasePageView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["properties"] = Property.objects.filter(
            is_available=True
        ).order_by("-created_at")

        return context

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        message = request.POST.get("message")

        messages.success(request, f"Thank you {name}. Your message has been sent successfully.")
        return redirect('contact')

    return render(request, 'contact.html', {
        'office_hours': [
            {'day': 'Monday - Friday', 'time': '8:00 AM - 6:00 PM'},
            {'day': 'Saturday', 'time': '9:00 AM - 4:00 PM'},
            {'day': 'Sunday', 'time': 'By appointment only'}
        ]
    })

def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('about')
    else:
        form = ReviewForm()

    return render(request, 'review.html', {'form': form})

def search_properties(request):
    properties = Property.objects.all().order_by('-created_at')

    city = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    bedrooms = request.GET.get('bedrooms')
    property_type = request.GET.get('property_type')
    sort_by = request.GET.get('sort_by')

    if city and city.strip():
        properties = properties.filter(city__icontains=city.strip())

    if property_type and property_type != "":
        properties = properties.filter(property_type=property_type)

    if min_price and min_price != "":
        properties = properties.filter(price__gte=min_price)

    if max_price and max_price != "":
        properties = properties.filter(price__lte=max_price)

    if bedrooms and bedrooms != "":
        if bedrooms == "3":
            properties = properties.filter(bedrooms__gte=3)
        else:
            properties = properties.filter(bedrooms=bedrooms)

    if sort_by == 'price_low':
        properties = properties.order_by('price')
    elif sort_by == 'price_high':
        properties = properties.order_by('-price')
    elif sort_by == 'latest':
        properties = properties.order_by('-created_at')

    paginator = Paginator(properties, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {
        'properties': page_obj,
        'page_obj': page_obj,
        'featured_properties': properties[:6],
        'property_types': [
            ('house_lot', 'House & Lot'),
            ('condo', 'Condominium'),
            ('townhouse', 'Townhouse')
        ],
        'sort_by': sort_by or 'latest'
    })

def property_detail(request, id):
    property = get_object_or_404(Property, id=id)
    similar_properties = Property.objects.exclude(id=property.id).filter(city=property.city)[:3]
    property_images = list(property.images.all())

    if not property_images and property.image:
        property_images = [property]

    context = {
        "property": property,
        "property_images": property_images,
        "similar_properties": similar_properties,
        "amenities": [
            'Swimming Pool', 'Garden', '24/7 Security', 'Smart Home', 'Covered Parking', 'Function Hall'
        ],
        "features": [
            'Move-in ready', 'Near schools', 'Near major road', 'Premium developer', 'Family-friendly'
        ],
    }

    return render(request, "view_property.html", context)

def partnerships(request):
    partners = Partner.objects.all()
    return render(request, 'partnership.html', {'partners': partners})

def home(request):
    properties = Property.objects.all().order_by('-created_at')
    partners = Partner.objects.all().order_by('name')

    return render(request, 'home.html', {
        'properties': properties[:8],
        'featured_properties': properties[:4],
        'latest_properties': properties[:4],
        'partners': partners,
        'testimonials': [
            {
                'name': 'Maria Santos',
                'role': 'Home Buyer',
                'feedback': 'The experience was smooth, transparent, and genuinely premium. We found the perfect family home in just one weekend.',
            },
            {
                'name': 'Carlos Dela Cruz',
                'role': 'Investor',
                'feedback': 'The property insights, walkthroughs, and overall presentation made the decision process very easy and confident.',
            },
            {
                'name': 'Ariana Reyes',
                'role': 'Relocating Professional',
                'feedback': 'Everything felt polished and professional. The team was responsive, helpful, and highly knowledgeable.',
            }
        ],
        'stats': [
            {'label': 'Properties Sold', 'value': '280+'},
            {'label': 'Happy Clients', 'value': '1,200+'},
            {'label': 'Cities Covered', 'value': '18'},
            {'label': 'Average Rating', 'value': '4.9/5'}
        ],
        'faqs': [
            {'question': 'How do I schedule a viewing?', 'answer': 'Use the schedule viewing button on any property detail page or contact our licensed agents directly through the website.'},
            {'question': 'Can I compare properties before deciding?', 'answer': 'Yes. Use the saved and compare sections to review multiple residences side by side.'},
            {'question': 'Are properties verified before listing?', 'answer': 'All approved listings are reviewed by the admin team before they become visible in the buyer marketplace.'}
        ]
    })

def favorites_view(request):
    return render(request, 'favorites.html', {
        'favorite_properties': Property.objects.all()[:4],
        'compare_properties': Property.objects.all()[:2]
    })

def buyer_profile_view(request):
    return render(request, 'buyer_profile.html', {
        'buyer': {
            'name': 'Jasmine Rivera',
            'email': 'jasmine.rivera@email.com',
            'phone': '0917-123-4567',
            'location': 'Bacoor, Cavite',
            'membership': 'Premium Buyer'
        }
    })

def appointment_history_view(request):
    return render(request, 'appointment_history.html', {
        'upcoming': [
            {'title': 'Sunrise Residences Tour', 'date': '2026-08-12', 'status': 'Confirmed'},
            {'title': 'Crestview Townhouse Viewing', 'date': '2026-08-17', 'status': 'Pending'}
        ],
        'previous': [
            {'title': 'Makati Garden Loft', 'date': '2026-07-10', 'status': 'Completed'},
            {'title': 'Riverfront Villa', 'date': '2026-06-28', 'status': 'Completed'}
        ]
    })

def inquiry_history_view(request):
    return render(request, 'inquiry_history.html', {
        'inquiries': [
            {
                'property': 'Sunrise Residences',
                'date': '2026-08-02',
                'status': 'Replied',
                'message': 'I would like to request a schedule for the unit visit and financing details.',
                'reply': 'An agent has already sent the viewing schedule and a brochure summary.'
            },
            {
                'property': 'Crestview Townhouse',
                'date': '2026-07-21',
                'status': 'Awaiting Response',
                'message': 'Could you share the updated price, floor plan, and payment terms?',
                'reply': 'Pending coordination with the listing agent.'
            }
        ]
    })

def seller_dashboard_view(request):
    all_properties = Property.objects.all()
    approved_properties = all_properties.filter(approval_status='approved')
    pending_properties = all_properties.filter(approval_status='pending')
    rejected_properties = all_properties.filter(approval_status='rejected')

    return render(request, 'seller_dashboard.html', {
        'total_properties': all_properties.count(),
        'active_listings': approved_properties.count(),
        'sold_properties': all_properties.filter(listing_status='sold').count(),
        'pending_approval': pending_properties.count(),
        'rejected_properties': rejected_properties.count(),
        'total_views': 4320,
        'total_inquiries': 83,
        'total_appointments': 27,
        'monthly_revenue': '₱1,240,000',
        'recent_activities': [
            f'{approved_properties.count()} approved listings are now visible to buyers',
            f'{pending_properties.count()} listings are waiting for admin review',
            f'{rejected_properties.count()} listings were rejected and need revision',
            'Commission report updated for the latest sales cycle'
        ],
        'approval_queue': pending_properties.order_by('-created_at')[:5]
    })

@login_required
def approve_property(request, id):
    property_obj = get_object_or_404(Property, id=id)
    property_obj.approval_status = 'approved'
    property_obj.is_available = True
    property_obj.listing_status = 'sale'
    property_obj.save(update_fields=['approval_status', 'is_available', 'listing_status'])
    messages.success(request, f'Property "{property_obj.title}" approved successfully.')
    return redirect('seller_dashboard')

@login_required
def reject_property(request, id):
    property_obj = get_object_or_404(Property, id=id)
    property_obj.approval_status = 'rejected'
    property_obj.is_available = False
    property_obj.save(update_fields=['approval_status', 'is_available'])
    messages.success(request, f'Property "{property_obj.title}" was marked for revision.')
    return redirect('seller_dashboard')

class AgentDashboardView(TemplateView):
    template_name = 'agent_dashboard.html'


class BuyerDashboardView(TemplateView):
    template_name = 'buyer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorite_properties'] = Property.objects.all()[:3]
        context['scheduled_visits'] = [
            {'title': 'Sunrise Residences Tour', 'date': '2026-08-12', 'status': 'Confirmed'},
            {'title': 'Crestview Townhouse Viewing', 'date': '2026-08-17', 'status': 'Pending'}
        ]
        context['inquiries'] = [
            {'property': 'Sunrise Residences', 'status': 'Replied'},
            {'property': 'Mandaluyong Loft', 'status': 'Awaiting Response'}
        ]
        context['notifications'] = [
            'New price update on the Bayfront Residence',
            'Your appointment for Parade Heights has been confirmed',
            'An agent replied to your inquiry about the Cortez Residence'
        ]
        context['recent_activity'] = [
            'Saved three premium properties for later comparison',
            'Requested a viewing for the Metro Skyline unit',
            'Updated buyer profile preferences and notification settings'
        ]
        return context


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        properties = Property.objects.all().order_by('-created_at')
        partners = Partner.objects.all().order_by('name')

        context.update({
            'properties': properties[:8],
            'featured_properties': properties[:4],
            'latest_properties': properties[:4],
            'partners': partners,
            'testimonials': [
                {
                    'name': 'Maria Santos',
                    'role': 'Home Buyer',
                    'feedback': 'The experience was smooth, transparent, and genuinely premium. We found the perfect family home in just one weekend.',
                },
                {
                    'name': 'Carlos Dela Cruz',
                    'role': 'Investor',
                    'feedback': 'The property insights, walkthroughs, and overall presentation made the decision process very easy and confident.',
                },
                {
                    'name': 'Ariana Reyes',
                    'role': 'Relocating Professional',
                    'feedback': 'Everything felt polished and professional. The team was responsive, helpful, and highly knowledgeable.',
                }
            ],
            'stats': [
                {'label': 'Properties Sold', 'value': '280+'},
                {'label': 'Happy Clients', 'value': '1,200+'},
                {'label': 'Cities Covered', 'value': '18'},
                {'label': 'Average Rating', 'value': '4.9/5'}
            ],
            'faqs': [
                {'question': 'How do I schedule a viewing?', 'answer': 'Use the schedule viewing button on any property detail page or contact our licensed agents directly through the website.'},
                {'question': 'Can I compare properties before deciding?', 'answer': 'Yes. Use the saved and compare sections to review multiple residences side by side.'},
                {'question': 'Are properties verified before listing?', 'answer': 'All approved listings are reviewed by the admin team before they become visible in the buyer marketplace.'}
            ]
        })
        return context

class AboutPageView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = Review.objects.order_by("-created_at")
        return context

class ContactPageView(TemplateView):
    template_name = 'contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['office_info'] = {
            'address': 'Molino IV, City of Bacoor, Cavite 4102',
            'phone': '0932-391-4987 | 0939-859-4321',
            'email': 'lcaraberealty@gmail.com'
        }
        return context


def virtual_tour_view(request, id):
    property = get_object_or_404(Property, id=id)
    return render(request, 'virtual_tour.html', {
        'property': property,
        'property_images': list(property.images.all())[:4],
        'hotspots': [
            {'label': 'Living Area', 'x': '32%', 'y': '52%'},
            {'label': 'Dining Nook', 'x': '58%', 'y': '40%'},
            {'label': 'Bedroom Suite', 'x': '70%', 'y': '68%'}
        ]
    })


class View_propertyPageView(TemplateView):
    template_name = 'view_property.html'

class BasePageView(TemplateView):
    template_name = 'base.html'
