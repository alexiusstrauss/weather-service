"""
Django management command to run behave BDD tests.
"""
import os
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command to run behave BDD tests."""

    help = "Run BDD tests using behave"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--features", default="tests/features", help="Path to features directory (default: tests/features)"
        )
        parser.add_argument("--tags", help="Run only features/scenarios with these tags")
        parser.add_argument("--format", default="pretty", help="Output format (default: pretty)")
        parser.add_argument("--verbose", action="store_true", help="Verbose output")

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            import behave
        except ImportError:
            self.stdout.write(self.style.ERROR("behave is not installed. Install it with: pip install behave"))
            return

        # Build behave command arguments
        behave_args = [options["features"]]

        if options["tags"]:
            behave_args.extend(["--tags", options["tags"]])

        if options["format"]:
            behave_args.extend(["--format", options["format"]])

        if options["verbose"]:
            behave_args.append("--verbose")

        # Set Django settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_service.settings.test")

        self.stdout.write(f"Running behave with args: {' '.join(behave_args)}")

        # Run behave
        from behave.__main__ import main as behave_main

        # Save original argv
        original_argv = sys.argv

        try:
            # Set argv for behave
            sys.argv = ["behave"] + behave_args

            # Run behave
            exit_code = behave_main()

            if exit_code == 0:
                self.stdout.write(self.style.SUCCESS("All BDD tests passed!"))
            else:
                self.stdout.write(self.style.ERROR(f"BDD tests failed with exit code: {exit_code}"))

        except SystemExit as e:
            exit_code = e.code
            if exit_code == 0:
                self.stdout.write(self.style.SUCCESS("All BDD tests passed!"))
            else:
                self.stdout.write(self.style.ERROR(f"BDD tests failed with exit code: {exit_code}"))
        finally:
            # Restore original argv
            sys.argv = original_argv
