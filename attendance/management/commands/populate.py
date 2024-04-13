import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from attendance.models import User, Attendance_info, AbsenceAccrual

class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        # Creating some users with unique recipient numbers
        user1 = User.objects.create(
            name="John Doe",
            birthdate=datetime.strptime("1990-04-01", "%Y-%m-%d").date(),
            gender=User.GenderChoices.MALE,
            recipient_number=str(random.randint(1000000000, 9999999999)),
            education_level=User.EducationLevelChoices.ELEMENTARY_1,
            welfare_exemption=500
        )
        user2 = User.objects.create(
            name="Jane Smith",
            birthdate=datetime.strptime("1992-08-12", "%Y-%m-%d").date(),
            gender=User.GenderChoices.FEMALE,
            recipient_number=str(random.randint(1000000000, 9999999999)),
            education_level=User.EducationLevelChoices.ELEMENTARY_3,
            welfare_exemption=300
        )

        # Creating attendance records
        attendance1 = Attendance_info.objects.create(
            user=user1,
            date=timezone.now().date(),
            start_time=timezone.now().replace(hour=9, minute=0),
            end_time=timezone.now().replace(hour=17, minute=0),
            status=Attendance_info.AttendanceStatus.PRESENT,
            transportation_to=Attendance_info.TransportationService.USED,
            transportation_from=Attendance_info.TransportationService.NOT_USED
        )

        # Creating Absence Accrual records
        AbsenceAccrual.objects.create(
            attendance=attendance1,
            accrual_eligible=True
        )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))
