from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Event(models.Model):
    name = models.CharField('nome', max_length=200)
    description = models.TextField('descrição')
    location = models.CharField('local', max_length=200)
    start_date = models.DateTimeField('data de início')
    end_date = models.DateTimeField('data de término')
    is_active = models.BooleanField('ativo', default=False)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='organizador',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'

    def __str__(self):
        return self.name

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'pk': self.pk})
