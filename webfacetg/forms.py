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
        fields = ('full_name', )


class CreateLotteryForm(forms.Form):
    name = forms.CharField(
        label="Имя лотереи",
        min_length=2,
        max_length=255,
    )
    description = forms.CharField(
        required=False,
        label="Описание лотереи",
        min_length=2,
        max_length=255,
    )
    is_active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
