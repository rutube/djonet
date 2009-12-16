from django.db import models

class Simple(models.Model):
	name = models.CharField(max_length=25, unique=True)
	def __unicode__(self):
		return self.name

class JustAsSimple(models.Model):
	name = models.CharField(max_length=25, unique=True)
	def __unicode__(self):
		return self.name

class CommonFieldTypes(models.Model):
	'''All fields and options listed in Django 1.1-beta docs are below.
	This class tests some of the more common setups, where common is 
	based on a sample size of one.  ;)

		Field options
			null
			blank
			choices
			db_column
			db_index
			db_tablespace
			default
			editable
			help_text
			primary_key
			unique
			unique_for_date
			unique_for_month
			unique_for_year
			verbose_name
		Field types
			AutoField
			BooleanField
			CharField
			CommaSeparatedIntegerField
			DateField
			DateTimeField
			DecimalField
			EmailField
			FileField
			FilePathField
			FloatField
			ImageField
			IntegerField
			IPAddressField
			NullBooleanField
			PositiveIntegerField
			PositiveSmallIntegerField
			SlugField
			SmallIntegerField
			TextField
			TimeField
			URLField
			XMLField
		Relationship fields
			ForeignKey
			ManyToManyField
			OneToOneField
	'''

	GENDER_TYPE = (
		( 'M', 'Male'),
		( 'F', 'Female'),
		( 'N', 'Neutral'),
	)

	choice = models.CharField(choices=GENDER_TYPE, max_length = 1)

	null_and_blank_string = models.CharField('Blank String',
	    max_length = 50, blank = True, null = True)

	blank_text = models.TextField(blank=True)

	simple = models.ForeignKey(Simple)

	created = models.DateTimeField('created', auto_now_add=True)

	url = models.URLField(verify_exists=False, max_length=500, blank=True)

	weight = models.PositiveIntegerField()

	sdt = models.DateField('Start Date', blank=True, default="")

	seasonal = models.BooleanField(default=False, db_index=True)

	amt = models.FloatField()

	empty_amt = models.FloatField(blank=True, null=True)

	many_to_many = models.ManyToManyField(JustAsSimple)

	class Meta:
		ordering = ('choice',)
		unique_together = ('url', 'sdt', 'amt')

	def __unicode__(self):
		return '%s' % (self.id,)
