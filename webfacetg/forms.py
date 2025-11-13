from django import forms

from webfacetg.models import TelegramUser
from .validators import MinMaxLengthValidator, OnlyLatinSymbolValidator, NotEmptyValidator


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
        required=False,
    )
    description = forms.CharField(
        required=False,
        label="Описание лотереи",
    )
    is_active = forms.BooleanField(required=False)

    def clean_name(self):
        name = self.cleaned_data["name"]
        NotEmptyValidator().validate(name)
        MinMaxLengthValidator(min_length=3, max_length=255).validate(name)
        OnlyLatinSymbolValidator().validate(name)
        return name

    def clean_description(self):
        description = self.cleaned_data["description"]
        if len(description) > 0:
            MinMaxLengthValidator(min_length=3, max_length=255).validate(description)
        return description

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
