from django.db import models
import os

class Tasks(models.Model):
    subjectId = models.IntegerField() #overarching subject id 
    situationId = models.IntegerField()
    situationTitle = models.CharField()
    text = models.TextField()

    def __str__(self):
        return self.situationTitle
    
class TermCandidates(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    term = models.TextField()
    startPosition = models.IntegerField()
    endPosition = models.IntegerField()

    def __str__(self):
        return self.term
    
class SNOMEDLinks(models.Model):
    term = models.ForeignKey(TermCandidates, on_delete=models.CASCADE) #one term candidate can have several SNOMED links
    conceptId = models.CharField()
    descriptionId = models.CharField()
    typeId = models.CharField()
    concept = models.TextField()
    similarity = models.FloatField()
    
class DBLinks(models.Model):
    snomed = models.ForeignKey(SNOMEDLinks, on_delete=models.CASCADE)
    icpc = models.CharField()
    icpcTerm = models.CharField()
    situationId = models.IntegerField() #the situation id that belongs to that icpc term
