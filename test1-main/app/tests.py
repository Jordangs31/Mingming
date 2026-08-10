from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import CustomUser, Property


class ApprovalWorkflowTests(TestCase):
    def setUp(self):
        self.agent = CustomUser.objects.create_user(
            username='agent@example.com',
            email='agent@example.com',
            password='pass1234',
            first_name='Agent',
            user_type='agent',
            is_verified=True,
        )
        self.staff_user = CustomUser.objects.create_user(
            username='broker@example.com',
            email='broker@example.com',
            password='pass1234',
            first_name='Broker',
            user_type='broker',
            is_verified=True,
            is_staff=True,
        )
        self.property = Property.objects.create(
            title='Sample Property',
            description='A test property for approval flow.',
            price=Decimal('7500000.00'),
            location='Molino IV',
            city='Bacoor',
            province='Cavite',
            bedrooms=3,
            bathrooms=2,
            floor_area=Decimal('120.00'),
            lot_area=Decimal('120.00'),
            parking_spaces=1,
            agent=self.agent,
        )

    def test_seller_dashboard_uses_live_pending_approval_data(self):
        response = self.client.get(reverse('seller_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Approval')
        self.assertContains(response, '1')

    def test_approve_property_endpoint_updates_property_status(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(reverse('approve_property', args=[self.property.id]))

        self.property.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.property.approval_status, 'approved')

    def test_broker_management_screen_has_live_agent_overview(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('manage_agents'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Agents')
        self.assertContains(response, 'Active Agents')

    def test_agent_dashboard_shows_property_management_actions(self):
        self.client.force_login(self.agent)
        response = self.client.get(reverse('agent_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Property Listings')
        self.assertContains(response, 'Add Property')
