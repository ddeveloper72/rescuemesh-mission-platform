"""
Management command to reset stale mission simulations.

This command finds simulations that have been "running" for longer than
a reasonable duration and resets them to not_started status.

Useful for:
- Container restarts (simulations persist in PostgreSQL but should reset)
- Recovering from crashed/abandoned simulations
- Daily cleanup tasks

Usage:
    python manage.py reset_stale_simulations
    python manage.py reset_stale_simulations --max-age-minutes=60
    python manage.py reset_stale_simulations --reset-all
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.missions.models import MissionSimulation


class Command(BaseCommand):
    help = 'Reset stale mission simulations that have been running too long'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-minutes',
            type=int,
            default=120,
            help='Reset simulations older than this many minutes (default: 120)'
        )
        parser.add_argument(
            '--reset-all',
            action='store_true',
            help='Reset ALL simulations regardless of age'
        )

    def handle(self, *args, **options):
        max_age_minutes = options['max_age_minutes']
        reset_all = options['reset_all']

        if reset_all:
            # Reset all simulations
            simulations = MissionSimulation.objects.filter(status='running')
            count = simulations.count()
            
            simulations.update(
                status='not_started',
                started_at=None,
                accumulated_elapsed_seconds=0
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Reset ALL {count} running simulations'
                )
            )
            return

        # Find stale simulations
        cutoff_time = timezone.now() - timedelta(minutes=max_age_minutes)
        stale_simulations = MissionSimulation.objects.filter(
            status='running',
            started_at__lt=cutoff_time
        )

        count = stale_simulations.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'No stale simulations found (max age: {max_age_minutes} minutes)'
                )
            )
            return

        # Reset stale simulations
        for sim in stale_simulations:
            age_minutes = (timezone.now() - sim.started_at).total_seconds() / 60
            self.stdout.write(
                f'  Resetting simulation for "{sim.mission.name}" '
                f'(running for {age_minutes:.1f} minutes)'
            )

        stale_simulations.update(
            status='not_started',
            started_at=None,
            accumulated_elapsed_seconds=0
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Reset {count} stale simulation(s) older than {max_age_minutes} minutes'
            )
        )
