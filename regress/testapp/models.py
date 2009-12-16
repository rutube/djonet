from django.db import models

class Simple(models.Model):
	name = models.CharField(max_length=25, unique=True)
	def __unicode__(self):
		return self.name
