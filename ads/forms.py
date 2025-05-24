from django import forms
from .models import Ad, ExchangeProposal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

class AdForm(forms.ModelForm):
    """Форма объявления"""
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'image_url',
            'category',
            'condition',
            Submit('submit', 'Сохранить объявление', css_class='btn btn-primary mt-3')
        )

class ExchangeProposalForm(forms.ModelForm):
    """Форма обмена предложениями"""
    ad_sender = forms.ModelChoiceField(
        queryset=Ad.objects.none(),
        label="Ваше объявление для обмена",
        help_text="Выберите одно из ваших объявлений, которое вы предлагаете для обмена."
    )

    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'ad_receiver': forms.HiddenInput(), # Скрываем, так как оно будет установлено из URL
        }

    def __init__(self, *args, **kwargs):
        user_ads_queryset = kwargs.pop('queryset', None) # Get queryset for ad_sender
        super().__init__(*args, **kwargs)
        if user_ads_queryset is not None:
            self.fields['ad_sender'].queryset = user_ads_queryset
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'ad_sender',
            'ad_receiver',
            'comment',
            Submit('submit', 'Отправить предложение', css_class='btn btn-primary mt-3')
        )