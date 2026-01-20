from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from Bus_Wash.models import Location, Site, Task, Configurations, TypeofWash
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Seed database with realistic Qatar/Mowasalat bus wash data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with Qatar/Mowasalat data...')

        # Create Groups
        level1_group, _ = Group.objects.get_or_create(name='Level1')
        level2_group, _ = Group.objects.get_or_create(name='Level2')

        # Create Users (Mowasalat staff)
        staff_members = [
            {'username': 'ahmed_driver', 'email': 'ahmed@mowasalat.qa', 'first_name': 'Ahmed', 'last_name': 'Al-Thani'},
            {'username': 'khalid_supervisor', 'email': 'khalid@mowasalat.qa', 'first_name': 'Khalid', 'last_name': 'Al-Kuwari'},
            {'username': 'mohammed_tech', 'email': 'mohammed@mowasalat.qa', 'first_name': 'Mohammed', 'last_name': 'Al-Naimi'},
            {'username': 'fatima_admin', 'email': 'fatima@mowasalat.qa', 'first_name': 'Fatima', 'last_name': 'Al-Sulaiti'},
            {'username': 'omar_washer', 'email': 'omar@mowasalat.qa', 'first_name': 'Omar', 'last_name': 'Hassan'},
            {'username': 'yusuf_inspector', 'email': 'yusuf@mowasalat.qa', 'first_name': 'Yusuf', 'last_name': 'Al-Mansouri'},
        ]

        users = []
        for staff in staff_members:
            user, created = User.objects.get_or_create(
                username=staff['username'],
                defaults={
                    'email': staff['email'],
                    'first_name': staff['first_name'],
                    'last_name': staff['last_name'],
                    'is_staff': False
                }
            )
            if created:
                user.set_password('mowasalat123')
                user.save()
            users.append(user)
            if 'supervisor' in staff['username'] or 'admin' in staff['username']:
                user.groups.add(level1_group)
            else:
                user.groups.add(level2_group)

        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} staff members'))

        # Qatar Locations (Major areas with bus shelters)
        qatar_locations = [
            'Doha Central',
            'West Bay',
            'The Pearl-Qatar',
            'Lusail City',
            'Al Wakrah',
            'Al Khor',
            'Al Rayyan',
            'Education City',
            'Hamad International Airport',
            'Souq Waqif',
            'Katara Cultural Village',
            'Msheireb Downtown',
            'Al Sadd',
            'Industrial Area',
            'Umm Salal',
            'Al Gharrafa',
            'Al Dafna',
            'Corniche Street',
            'Al Bidda',
            'Sports City',
        ]

        locations = []
        for loc_name in qatar_locations:
            loc, _ = Location.objects.get_or_create(name=loc_name)
            locations.append(loc)

        self.stdout.write(self.style.SUCCESS(f'Created {len(locations)} Qatar locations'))

        # Shelter Types (Configurations)
        shelter_types = [
            {'name': 'Standard Shelter', 'code': 'STD', 'config_type': 'shelter_type'},
            {'name': 'Air-Conditioned Shelter', 'code': 'AC', 'config_type': 'shelter_type'},
            {'name': 'Metro Link Shelter', 'code': 'MTR', 'config_type': 'shelter_type'},
            {'name': 'Express Stop', 'code': 'EXP', 'config_type': 'shelter_type'},
            {'name': 'Park & Ride', 'code': 'PNR', 'config_type': 'shelter_type'},
            {'name': 'Metrolink Station', 'code': 'MLS', 'config_type': 'shelter_type'},
        ]

        shelter_configs = []
        for st in shelter_types:
            config, _ = Configurations.objects.get_or_create(
                code=st['code'],
                defaults={'name': st['name'], 'config_type': st['config_type']}
            )
            shelter_configs.append(config)

        # Damage Types (Configurations)
        damage_types = [
            {'name': 'Graffiti', 'code': 'GRF', 'config_type': 'damages'},
            {'name': 'Broken Glass', 'code': 'BGL', 'config_type': 'damages'},
            {'name': 'Seat Damage', 'code': 'SDM', 'config_type': 'damages'},
            {'name': 'Roof Leak', 'code': 'RLK', 'config_type': 'damages'},
            {'name': 'AC Malfunction', 'code': 'ACM', 'config_type': 'damages'},
            {'name': 'Lighting Issue', 'code': 'LGT', 'config_type': 'damages'},
            {'name': 'Bench Damage', 'code': 'BND', 'config_type': 'damages'},
            {'name': 'Sign Damage', 'code': 'SGN', 'config_type': 'damages'},
        ]

        for dt in damage_types:
            Configurations.objects.get_or_create(
                code=dt['code'],
                defaults={'name': dt['name'], 'config_type': dt['config_type']}
            )

        self.stdout.write(self.style.SUCCESS('Created shelter types and damage configurations'))

        # Bus Shelter Sites (with Karwa-style codes)
        # Mowasalat uses codes like KRW-XXX for Karwa bus shelters
        sites_data = [
            {'code': 'KRW-001', 'location': 'Doha Central'},
            {'code': 'KRW-002', 'location': 'Doha Central'},
            {'code': 'KRW-003', 'location': 'West Bay'},
            {'code': 'KRW-004', 'location': 'West Bay'},
            {'code': 'KRW-005', 'location': 'The Pearl-Qatar'},
            {'code': 'KRW-006', 'location': 'The Pearl-Qatar'},
            {'code': 'KRW-007', 'location': 'Lusail City'},
            {'code': 'KRW-008', 'location': 'Lusail City'},
            {'code': 'KRW-009', 'location': 'Al Wakrah'},
            {'code': 'KRW-010', 'location': 'Al Wakrah'},
            {'code': 'KRW-011', 'location': 'Al Khor'},
            {'code': 'KRW-012', 'location': 'Al Rayyan'},
            {'code': 'KRW-013', 'location': 'Al Rayyan'},
            {'code': 'KRW-014', 'location': 'Education City'},
            {'code': 'KRW-015', 'location': 'Education City'},
            {'code': 'KRW-016', 'location': 'Hamad International Airport'},
            {'code': 'KRW-017', 'location': 'Hamad International Airport'},
            {'code': 'KRW-018', 'location': 'Souq Waqif'},
            {'code': 'KRW-019', 'location': 'Katara Cultural Village'},
            {'code': 'KRW-020', 'location': 'Msheireb Downtown'},
            {'code': 'KRW-021', 'location': 'Msheireb Downtown'},
            {'code': 'KRW-022', 'location': 'Al Sadd'},
            {'code': 'KRW-023', 'location': 'Al Sadd'},
            {'code': 'KRW-024', 'location': 'Industrial Area'},
            {'code': 'KRW-025', 'location': 'Industrial Area'},
            {'code': 'KRW-026', 'location': 'Umm Salal'},
            {'code': 'KRW-027', 'location': 'Al Gharrafa'},
            {'code': 'KRW-028', 'location': 'Al Dafna'},
            {'code': 'KRW-029', 'location': 'Corniche Street'},
            {'code': 'KRW-030', 'location': 'Corniche Street'},
            {'code': 'KRW-031', 'location': 'Al Bidda'},
            {'code': 'KRW-032', 'location': 'Sports City'},
        ]

        sites = []
        for site_data in sites_data:
            location = Location.objects.get(name=site_data['location'])
            site, _ = Site.objects.get_or_create(
                site_code=site_data['code'],
                defaults={'location': location}
            )
            sites.append(site)

        self.stdout.write(self.style.SUCCESS(f'Created {len(sites)} bus shelter sites'))

        # Types of Wash per location
        wash_types_data = [
            'Full Exterior Wash',
            'Interior Deep Clean',
            'AC Vent Cleaning',
            'Glass & Window Polish',
            'Pressure Wash',
            'Sanitization Wash',
            'Quick Rinse',
        ]

        for location in locations:
            for wash_name in wash_types_data:
                TypeofWash.objects.get_or_create(
                    location=location,
                    name=wash_name
                )

        self.stdout.write(self.style.SUCCESS('Created wash types for all locations'))

        # Create Tasks (Bus Wash assignments)
        task_templates = [
            {'name': 'Morning Shelter Wash', 'desc': 'Complete morning wash cycle for bus shelter including exterior cleaning and sanitization.'},
            {'name': 'Evening Maintenance Clean', 'desc': 'End of day cleaning and inspection of shelter facilities.'},
            {'name': 'Deep Sanitization', 'desc': 'Full sanitization protocol for high-traffic shelter.'},
            {'name': 'AC Unit Maintenance', 'desc': 'Clean and service air conditioning units in shelter.'},
            {'name': 'Glass Panel Cleaning', 'desc': 'Clean all glass panels and remove any graffiti.'},
            {'name': 'Weekly Inspection Wash', 'desc': 'Thorough weekly cleaning with full inspection report.'},
            {'name': 'Post-Event Cleanup', 'desc': 'Special cleaning after major public event.'},
            {'name': 'Quarterly Deep Clean', 'desc': 'Comprehensive quarterly maintenance and deep cleaning.'},
        ]

        # Create tasks for the past 30 days
        tasks_created = 0
        for i in range(60):
            task_template = random.choice(task_templates)
            site = random.choice(sites)
            user = random.choice(users)
            shelter_type = random.choice(shelter_configs)

            days_ago = random.randint(0, 30)
            task_date = timezone.now() - timedelta(days=days_ago)

            status = random.choice(['in progress', 'completed', 'completed', 'completed'])

            task = Task.objects.create(
                task_name=f"{task_template['name']} - {site.site_code}",
                task_description=task_template['desc'],
                user=user,
                site_id=site,
                shelter_type=shelter_type,
                status=status,
                is_scanned=random.choice([True, False]),
                map_url=f"https://maps.google.com/?q=Qatar+{site.location.name.replace(' ', '+')}",
                odometerbefore=random.randint(10000, 50000) if status == 'completed' else None,
                odometerafter=random.randint(50001, 60000) if status == 'completed' else None,
            )
            tasks_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {tasks_created} wash tasks'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write('')
        self.stdout.write('Sample login credentials:')
        self.stdout.write('  Username: khalid_supervisor')
        self.stdout.write('  Password: mowasalat123')
        self.stdout.write('')
        self.stdout.write('  Username: ahmed_driver')
        self.stdout.write('  Password: mowasalat123')
