from datetime import datetime
import pytz

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe

import simple_history.models
from django_model_changes import ChangesMixin

from accountifie.toolkit.fields.htmlfield import HtmlField
from accountifie.middleware.docengine import getCurrentUser


TZ = pytz.timezone(settings.TIME_ZONE)


TASK_STATUS_CHOICES = [
    ['draft', "Draft"],
    ['submitted', "Submitted for Approval"],
    ['approved', "Approved"],
    ['completed', "Completed"],
]

FREQ = [
    ['daily', 'Daily'],
    ['weekly', 'Weekly'],
    ['monthly', 'Monthly'],
    ['annual', 'annual'],
]

class TaskDef(models.Model):
    desc = models.CharField(max_length=100)
    freq = models.CharField(choices=FREQ, max_length=10)
    approvers = models.ManyToManyField(User, blank=True, related_name="a")
    preparers = models.ManyToManyField(User, blank=True, related_name="p")
    tmpl = models.CharField(max_length=100)

    def __str__(self):
        return self.desc


class Task(models.Model):
  _STATUS_COLOR_CLASS = dict(zip(zip(*TASK_STATUS_CHOICES)[0], ('info', 'warning', 'success', 'success',)))

  status = models.CharField(choices=TASK_STATUS_CHOICES, max_length=20)
  task_def = models.ForeignKey(TaskDef)
  as_of = models.DateField()
  
  history = simple_history.models.HistoricalRecords()

  def __str__(self):
    return '%s: %s' % (self.task_def.desc, datetime.strftime(self.as_of, '%d-%b-%y'))

  class Meta:
      ordering = ["-as_of"]


  def can_prep(self, user):
    return (user in self.task_def.preparers.all())

  def can_approve(self, user):
    return (user in self.task_def.approvers.all())

  def save(self, *args, **kwargs):
    action = kwargs.get('action', None)
    user = kwargs.get('user', None)
    if not user:
      user = self.user
    comment = kwargs.get('comment', None)
    if action in ['create', 'submit', 'comment']:
      if not self.can_prep(user):
        raise ValueError('User %s is not permissioned to do this' % user)
    elif action in ['signoff']:
      if not self.can_approve(user):
        raise ValueError('User %s is not permissioned to do this' % user)  
    else:
      try:
        action = self.action
        user = self.user
      except:
        raise ValueError('Unknown action -- %s. Nothing saved.' % args)
      
    if action == 'create':
      self.status = 'draft'
      comment = 'created'
      super(Task, self).save()
    elif action == 'submit':
      self.status = 'submitted'
      super(Task, self).save()
    elif action == 'signoff':
      self.status = 'approved'
      super(Task, self).save()

    AuditRecord(user=user, timestamp=datetime.now(TZ), desc=self.status, task_id=self.id, comment=comment if comment else '').save()
    return


  def signoff(self, comment=None):
    self.status = 'approved'
    self.save(comment=comment)

  def submit(self, comment=None):
    self.status = 'submitted'
    self.save(comment=comment)

  def comment(self, comment=None):
    AuditRecord(user=getCurrentUser(), timestamp=datetime.now(TZ), desc=self.status, task_id=self.id, comment=comment if comment else '').save()


  @classmethod
  def colorise(cls, sta):
    return cls._STATUS_COLOR_CLASS[sta]

  @property
  def status_tag(self):
        return mark_safe('<span class="label label-%s">%s</span>' % (
                    self.colorise(self.status), self.status)
        )
      
  @property
  def id_link(self):
      return mark_safe('<a href="/audit/task/%s/%s">%s' %( self.task_def.tmpl, self.id, self.id))


class AuditRecord(ChangesMixin, models.Model):
  user = models.ForeignKey(User)
  timestamp = models.DateTimeField()
  desc = models.CharField(max_length=50)
  task = models.ForeignKey(Task)
  comment = HtmlField(target="block", blank=True, help_text="Please add comment")

  @property
  def comment_fmt(self):
      if self.comment:
        return mark_safe(self.comment)
      else:
        return '-'

  @property
  def user_name(self):
    return self.user.username

  @property
  def task_link(self):
      return mark_safe('<a href="/audit/task/%s/%s">%s' %( self.task.task_def.tmpl, self.task.id, self.task))
