"""Foundation forms: signup with intent + LGPD consent, account deletion."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

INTENT_CHOICES = [
    ('customer', 'Quero contratar'),
    ('provider', 'Quero oferecer serviços'),
]


class SignUpForm(UserCreationForm):
    """Signup with explicit intent and mandatory LGPD consents."""

    intent = forms.ChoiceField(
        label='Como você quer usar o FindAPro?',
        choices=INTENT_CHOICES,
        widget=forms.RadioSelect,
        initial='client',
    )
    accept_terms = forms.BooleanField(label='Li e aceito os Termos de Uso')
    accept_privacy = forms.BooleanField(label='Li e aceito a Política de Privacidade')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'fp-input', 'autocomplete': 'given-name', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'fp-input', 'autocomplete': 'family-name', 'placeholder': 'Sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'fp-input', 'autocomplete': 'email', 'placeholder': 'seu@email.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update(
            {'class': 'fp-input', 'autocomplete': 'new-password', 'placeholder': 'Crie uma senha'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'fp-input', 'autocomplete': 'new-password', 'placeholder': 'Confirme a senha'}
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.user_type = self.cleaned_data['intent']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class DeleteAccountForm(forms.Form):
    """LGPD erasure: password confirmation + optional reason."""

    password = forms.CharField(
        label='Confirme sua senha',
        widget=forms.PasswordInput(attrs={'class': 'fp-input', 'autocomplete': 'current-password'}),
    )
    reason = forms.CharField(
        label='Motivo (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError('Senha incorreta.')
        return password
