from django import forms
from betterforms.changelist import SearchForm


class FileForm(forms.Form):
    file = forms.FileField(required=True)


class SplashForm(SearchForm):
    SEARCH_FIELDS = []
    def set_searchfields(self, fld_list):
        self.SEARCH_FIELDS = fld_list

    def __init__(self, *args, **kwargs):
        super(SplashForm, self).__init__(*args, **kwargs)
