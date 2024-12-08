from django import forms

from webfacetg.models import TelegramUser


class EditTelegramUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    class Meta:
        model = TelegramUser
        fields = ('full_name', 'full_name_from_tg')

