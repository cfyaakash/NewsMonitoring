from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Company(models.Model):
    name = models.CharField(max_length=250, blank=True, unique=True)

    def __str__(self):
        return self.name


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    client = models.ForeignKey(Company, related_name='company_client', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return "%s 's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Subscriber.objects.get_or_create(user=instance)
    post_save.connect(create_user_profile, sender=User)


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    # companies = models.ManyToManyField(Company, related_name='tagged_comp')
    client = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, verbose_name='Client')
    created_by = models.ForeignKey(Subscriber, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('url', 'client')

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    body_text = models.TextField(max_length=1000)
    url = models.URLField(max_length=500)
    companies = models.ManyToManyField(Company)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Company,related_name='story_client', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('url', 'client')

    def __str__(self):
        return self.title
