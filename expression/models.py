from django.db import models

# to make new model: python manage.py makemigrations, python manage.py migrate

class Genre(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name


class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title


class Genesummary(models.Model):
    geneName = models.CharField(max_length=50)
    totalNum = models.PositiveIntegerField()
    novelNum = models.PositiveIntegerField()
    
    def __str__(self):
        return self.title


class Genecounts(models.Model):
    # sampleID created prior from 1...
    sampleID = models.PositiveIntegerField()
    geneName = models.CharField(max_length=50)
    counts = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.CharField(max_length=2)
    sex = models.CharField(max_length=2)
    
    def __str__(self):
        return self.title

class Transcriptcounts(models.Model):
    # sampleID created prior from 1...
    sampleID = models.PositiveIntegerField()
    geneName = models.CharField(max_length=50, blank=True, null=True)
    isoform = models.CharField(max_length=50)
    counts = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.CharField(max_length=2)
    sex = models.CharField(max_length=2)
    
    def __str__(self):
        return self.title

