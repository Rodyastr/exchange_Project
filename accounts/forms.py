from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

class CustomUserCreationForm(UserCreationForm):
    """
    Форма создания пользователя, расширяя UserCreationForm
    """
    email = forms.EmailField(required=True, help_text='Обязательно для восстановления пароля.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Зарегистрироваться', css_class='btn btn-primary mt-3')
        )

class CustomUserChangeForm(UserChangeForm):
    """
    Форма обновления пользователя, расширяя UserChangeForm
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'email',
            'first_name',
            'last_name',
            Submit('submit', 'Сохранить изменения', css_class='btn btn-primary mt-3')
        )