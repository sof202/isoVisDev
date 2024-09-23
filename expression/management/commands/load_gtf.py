# load_gtf.py
from csv import DictReader
from django.core.management.base import BaseCommand
from expression.models import TranscriptFeature  # Adjust the import based on your app name

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables

Important to migrate the app first: 
manage.py makemigrations expression
manage.py migrate

# to reload the database
python manage.py load_gtf
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from gtfcheck.csv"

    def handle(self, *args, **options):
                
        # Show this before loading the data into the database
        print("Loading gtf")

        #Code to load the data into database
        for row in DictReader(open('./expression/files/gtfcheck.csv')):
            TranscriptGtfFeatures=TranscriptFeature(seqname=row['seqname'], geneName=row['geneName'], isoform=row['isoform'], start=row['start'], end=row['end'], feature = row['feature'], strand = row['strand'])  
            TranscriptGtfFeatures.save()
