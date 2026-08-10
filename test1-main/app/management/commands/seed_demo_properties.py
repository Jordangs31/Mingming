from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from app.models import Property


class Command(BaseCommand):
    help = 'Seed the database with realistic demo property data for the MIS workflow.'

    def handle(self, *args, **options):
        User = get_user_model()

        broker, _ = User.objects.get_or_create(
            username='broker_demo',
            defaults={
                'email': 'broker_demo@example.com',
                'first_name': 'Broker',
                'last_name': 'Demo',
                'user_type': 'broker',
                'is_staff': True,
                'is_verified': True,
            },
        )
        broker.set_password('demo1234')
        broker.save()

        agents = []
        for index, data in enumerate([
            ('agent_one', 'Agent', 'One'),
            ('agent_two', 'Agent', 'Two'),
            ('agent_three', 'Agent', 'Three'),
        ], start=1):
            agent, _ = User.objects.get_or_create(
                username=data[0],
                defaults={
                    'email': f'{data[0]}@example.com',
                    'first_name': data[1],
                    'last_name': data[2],
                    'user_type': 'agent',
                    'is_verified': True,
                },
            )
            agent.set_password('demo1234')
            agent.save()
            agents.append(agent)

        demo_properties = [
            {
                'title': 'Whitewood Villas',
                'description': 'A premium family villa with landscaped garden and smart-home features.',
                'price': Decimal('9850000.00'),
                'location': 'Molino IV',
                'city': 'Bacoor',
                'province': 'Cavite',
                'bedrooms': 4,
                'bathrooms': 3,
                'floor_area': Decimal('240.00'),
                'lot_area': Decimal('320.00'),
                'parking_spaces': 2,
                'agent': agents[0],
                'approval_status': 'approved',
                'listing_status': 'sale',
                'is_available': True,
            },
            {
                'title': 'Crestview Townhouse',
                'description': 'A stylish urban townhouse designed for growing families and investors.',
                'price': Decimal('7600000.00'),
                'location': 'Poblacion',
                'city': 'Dasmariñas',
                'province': 'Cavite',
                'bedrooms': 3,
                'bathrooms': 2,
                'floor_area': Decimal('180.00'),
                'lot_area': Decimal('150.00'),
                'parking_spaces': 1,
                'agent': agents[1],
                'approval_status': 'approved',
                'listing_status': 'sale',
                'is_available': True,
            },
            {
                'title': 'Sunrise Residences',
                'description': 'A modern condominium unit with panoramic city views and resort-style amenities.',
                'price': Decimal('5400000.00'),
                'location': 'Salitran',
                'city': 'Bacoor',
                'province': 'Cavite',
                'bedrooms': 2,
                'bathrooms': 2,
                'floor_area': Decimal('96.00'),
                'lot_area': Decimal('0.00'),
                'parking_spaces': 1,
                'agent': agents[2],
                'approval_status': 'pending',
                'listing_status': 'sale',
                'is_available': False,
            },
            {
                'title': 'Riverfront Villa',
                'description': 'An elegant villa with generous outdoor space and a serene riverside setting.',
                'price': Decimal('11800000.00'),
                'location': 'Imus River Estate',
                'city': 'Imus',
                'province': 'Cavite',
                'bedrooms': 5,
                'bathrooms': 4,
                'floor_area': Decimal('320.00'),
                'lot_area': Decimal('420.00'),
                'parking_spaces': 3,
                'agent': agents[0],
                'approval_status': 'pending',
                'listing_status': 'sale',
                'is_available': False,
            },
            {
                'title': 'Bayfront Residence',
                'description': 'A contemporary coastal-inspired property ideal for premium buyers and investors.',
                'price': Decimal('8700000.00'),
                'location': 'Tanza Coast',
                'city': 'Tanza',
                'province': 'Cavite',
                'bedrooms': 4,
                'bathrooms': 3,
                'floor_area': Decimal('220.00'),
                'lot_area': Decimal('260.00'),
                'parking_spaces': 2,
                'agent': agents[1],
                'approval_status': 'approved',
                'listing_status': 'sale',
                'is_available': True,
            },
            {
                'title': 'Cedar Heights',
                'description': 'A quiet suburban home with a home office nook and family-ready layout.',
                'price': Decimal('6900000.00'),
                'location': 'General Trias',
                'city': 'General Trias',
                'province': 'Cavite',
                'bedrooms': 3,
                'bathrooms': 2,
                'floor_area': Decimal('144.00'),
                'lot_area': Decimal('180.00'),
                'parking_spaces': 1,
                'agent': agents[2],
                'approval_status': 'rejected',
                'listing_status': 'sale',
                'is_available': False,
            },
        ]

        for data in demo_properties:
            Property.objects.update_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'price': data['price'],
                    'location': data['location'],
                    'city': data['city'],
                    'province': data['province'],
                    'bedrooms': data['bedrooms'],
                    'bathrooms': data['bathrooms'],
                    'floor_area': data['floor_area'],
                    'lot_area': data['lot_area'],
                    'parking_spaces': data['parking_spaces'],
                    'agent': data['agent'],
                    'approval_status': data['approval_status'],
                    'listing_status': data['listing_status'],
                    'is_available': data['is_available'],
                },
            )

        self.stdout.write(self.style.SUCCESS('Seeded demo users and realistic property listings successfully.'))
