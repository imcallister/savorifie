from django import forms

from betterforms.forms import Fieldset, BetterModelForm

from accountifie.toolkit.forms import Html5Mixin, BootstrapMixin, BootstrapForm

import audit.models


class TraceForm(forms.Form):
    file = forms.FileField(required=True)


class TaskBetterForm(BootstrapMixin, Html5Mixin, BetterModelForm):

    class Meta:
        model = audit.models.Task
        fieldsets = (
            Fieldset('', (
                ('task_def', 'as_of', 'status'),
                
            )),
        )

    def __init__(self, *args, **kwargs):
        super(TaskBetterForm, self).__init__(*args, **kwargs)
        instance = self.instance
        model = instance.__class__
        self.fields['status'].initial = 'draft'


class CommentForm(BootstrapForm):
    comment = forms.CharField(widget=forms.Textarea)