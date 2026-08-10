from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    HomePageView,
    AboutPageView,
    ListingsPageView,
    View_propertyPageView,
    ContactPageView,
    BasePageView,
    register_view,
    login_view,
    BrokerDashboardView,
    AgentDashboardView,
    BuyerDashboardView,
    ManageAgentsView,
    ManagepropertiesView,
    ViewBuyersView,
    agent_dashboard_view,
    add_property,
    edit_property,
    delete_property,
    add_review,
    agents,
    search_properties,
    property_detail,
    partnerships,
    home,
    contact_view,
    favorites_view,
    buyer_profile_view,
    appointment_history_view,
    inquiry_history_view,
    seller_dashboard_view,
    virtual_tour_view,
    approve_property,
    reject_property
    , agent_profile_view, contact_agent, schedule_appointment, agent_inbox, broker_property_decision, broker_toggle_agent
)

urlpatterns = [
    # -------------------------
    # Public / General Pages
    # -------------------------
    path('', home, name='home'),
    path('home/', HomePageView.as_view(), name='base'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('agent/listings/', ListingsPageView.as_view(), name='listings'),
    path('contact/', contact_view, name='contact'),
    path('property/', View_propertyPageView.as_view(), name='property'),
    path('search/', search_properties, name='search_properties'),
    path('property/<int:id>/', property_detail, name='property_detail'),
    path('favorites/', favorites_view, name='favorites'),
    path('buyer-profile/', buyer_profile_view, name='buyer_profile'),
    path('appointments/', appointment_history_view, name='appointment_history'),
    path('inquiries/', inquiry_history_view, name='inquiry_history'),
    path('seller-dashboard/', seller_dashboard_view, name='seller_dashboard'),
    path('seller-dashboard/approve/<int:id>/', approve_property, name='approve_property'),
    path('seller-dashboard/reject/<int:id>/', reject_property, name='reject_property'),
    path('virtual-tour/<int:id>/', virtual_tour_view, name='virtual_tour'),

    # -------------------------
    # Broker Dashboard Section
    # -------------------------
    path('broker_dashboard/', BrokerDashboardView.as_view(), name='broker_dashboard'),

    # Broker Management Pages
    path('broker/agents/', ManageAgentsView.as_view(), name='manage_agents'),
    path('broker/properties/', ManagepropertiesView.as_view(), name='manage_properties'),

    # -------------------------
    # Agent Dashboard Section
    # -------------------------
    path('agent/agents/', agents, name='agents'),
    path('agent/<int:id>/', agent_profile_view, name='agent_profile'),
    path('agent/<int:id>/contact/', contact_agent, name='contact_agent'),
    path('agent/<int:id>/appointment/', schedule_appointment, name='schedule_appointment'),
    path('agent/inbox/', agent_inbox, name='agent_inbox'),
    path('agent/dashboard/', agent_dashboard_view, name='agent_dashboard'),
    path('agent/add-property/', add_property, name='add_property'),
    path('agent/edit-property/<int:id>/', edit_property, name='edit_property'),
    path('agent/delete-property/<int:id>/', delete_property, name='delete_property'),
    path('agent/buyers/', ViewBuyersView.as_view(), name='view_buyers'),
    path('broker/properties/<int:id>/<str:decision>/', broker_property_decision, name='broker_property_decision'),
    path('broker/agents/<int:id>/toggle/', broker_toggle_agent, name='broker_toggle_agent'),

    # Buyer Dashboard Section
    path('buyer_dashboard/', BuyerDashboardView.as_view(), name='buyer_dashboard'),

    # Reviews
    path('add-review/', add_review, name='add_review'),

    path('partnerships/', partnerships, name='partnerships'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
