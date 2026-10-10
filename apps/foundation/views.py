"""Foundation views — Phase 0 (roles, auth, settings shell, legal pages)."""
import json

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from apps.providers.models import ServiceCategory

from .forms import DeleteAccountForm, SignUpForm
from .models import (
    AccountDeletionRequest,
    AuditLog,
    ConsentRecord,
    LegalDocument,
    ProfessionalProfile,
    UserProfile,
)
from .services import anonymize_user, audit, capture_consent

User = get_user_model()


# ---------------------------------------------------------------- signup/auth

class SignUpView(TemplateView):
    """Signup with explicit intent (hire vs offer) + LGPD consent capture."""

    template_name = 'foundation/signup.html'

    def get_context_data(self, **kwargs):
        return {
            'form': kwargs.get('form') or SignUpForm(),
            'google_configured': _google_configured(),
        }

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('foundation:app_home')
        return self.render_to_response(self.get_context_data())

    def post(self, request):
        form = SignUpForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        user = form.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'professional' if user.user_type == 'provider' else 'client'
        profile.save(update_fields=['role', 'updated_at'])
        if user.user_type == 'provider':
            ProfessionalProfile.objects.get_or_create(user=user)

        capture_consent(request, user, 'terms')
        capture_consent(request, user, 'privacy')
        audit(request, 'signup', entity=user)

        login(request, user)
        messages.success(request, 'Conta criada com sucesso. Bem-vindo(a) ao FindAPro!')
        if user.user_type == 'provider':
            return redirect('foundation:onboarding_professional')
        return redirect('foundation:app_home')


def _google_configured():
    from . import google_oauth
    return google_oauth.google_configured()


def google_login(request):
    from . import google_oauth

    if not google_oauth.google_configured():
        messages.error(request, 'O login com Google ainda não está configurado.')
        return redirect('accounts:login')
    return redirect(google_oauth.build_authorization_url(request))


def google_callback(request):
    """Exchange the OAuth code; new users go through the consent screen."""
    from . import google_oauth

    if not google_oauth.google_configured():
        return redirect('accounts:login')
    if request.GET.get('state') != request.session.pop('google_oauth_state', None):
        messages.error(request, 'Sessão de login inválida. Tente novamente.')
        return redirect('accounts:login')
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Login com Google cancelado.')
        return redirect('accounts:login')
    try:
        info = google_oauth.exchange_code(request, code)
    except Exception:
        messages.error(request, 'Não foi possível entrar com o Google. Tente novamente.')
        return redirect('accounts:login')

    request.session['google_profile'] = info
    if User.objects.filter(email__iexact=info['email']).exists():
        return _finish_google_signup(request, info, existing=True)
    return redirect('foundation:google_consent')


def google_consent(request):
    """LGPD consent screen for first-time Google signups."""
    info = request.session.get('google_profile')
    if not info:
        return redirect('accounts:login')
    if request.method == 'POST':
        if not (request.POST.get('accept_terms') and request.POST.get('accept_privacy')):
            messages.error(request, 'É necessário aceitar os Termos e a Política de Privacidade.')
            return render(request, 'foundation/google_consent.html',
                          {'google_email': info['email'],
                           'terms_url': reverse('foundation:legal_detail', args=['termos']),
                           'privacy_url': reverse('foundation:legal_detail', args=['privacidade'])})
        return _finish_google_signup(request, info, existing=False)
    return render(request, 'foundation/google_consent.html',
                  {'google_email': info['email'],
                   'terms_url': reverse('foundation:legal_detail', args=['termos']),
                   'privacy_url': reverse('foundation:legal_detail', args=['privacidade'])})


def _finish_google_signup(request, info, existing):
    from . import google_oauth

    user = User.objects.get(email__iexact=info['email'])
    if not existing:
        user.first_name = info.get('given_name', '')[:30]
        user.last_name = info.get('family_name', '')[:30]
        user.user_type = 'customer'
        user.set_unusable_password()
        user.save()
        UserProfile.objects.get_or_create(user=user)
        capture_consent(request, user, 'terms')
        capture_consent(request, user, 'privacy')
        audit(request, 'signup_google', entity=user)
    request.session.pop('google_profile', None)
    login(request, user)
    messages.success(request, 'Bem-vindo(a) ao FindAPro!')
    return redirect('foundation:app_home')


# ------------------------------------------------------------ public browsing

def permission_denied(request, exception=None):
    """403 page."""
    return render(request, 'foundation/403.html', status=403)


def page_not_found(request, exception=None):
    """404 page."""
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    """500 page."""
    return render(request, 'errors/500.html', status=500)


def categories(request):
    """Public categories — real data only; empty state when none exist."""
    cats = ServiceCategory.objects.filter(is_active=True).annotate(
        num_providers=Count('providers', filter=Q(providers__is_active=True)),
    )
    return render(request, 'foundation/categories.html', {'categories': cats})


def legal_list(request):
    docs = LegalDocument.objects.filter(is_current=True).order_by('doc_type')
    return render(request, 'foundation/legal_list.html', {'documents': docs})


def legal_detail(request, doc_type):
    valid_types = dict(LegalDocument.DOC_TYPES)
    if doc_type not in valid_types:
        raise Http404('Documento não encontrado.')
    doc = LegalDocument.objects.filter(doc_type=doc_type, is_current=True).first()
    if not doc:
        raise Http404('Documento não publicado.')
    return render(request, 'foundation/legal_detail.html', {'document': doc})


# ------------------------------------------------------- authenticated shell

@login_required
def app_home(request):
    """/app/ — authenticated dashboard. Real data only: empty states."""
    profile = getattr(request.user, 'foundation_profile', None)
    return render(request, 'foundation/app_home.html', {'profile': profile})


@login_required
def onboarding_professional(request):
    """Stub onboarding path for professionals (built in a later phase)."""
    profile = getattr(request.user, 'foundation_profile', None)
    if profile and profile.role not in ('professional', 'admin'):
        return render(request, 'foundation/403.html', status=403)
    prof = ProfessionalProfile.objects.filter(user=request.user).first()
    return render(request, 'foundation/onboarding_professional.html',
                  {'professional': prof})


# ----------------------------------------------------------- settings shell

@login_required
def settings_home(request):
    return render(request, 'foundation/settings/home.html')


@login_required
def settings_account(request):
    consents = ConsentRecord.for_user(request.user).order_by('-granted_at')
    return render(request, 'foundation/settings/account.html',
                  {'profile': getattr(request.user, 'foundation_profile', None),
                   'consents': consents})


@login_required
def settings_appearance(request):
    return render(request, 'foundation/settings/appearance.html')


@login_required
def settings_wallet(request):
    """Wallet entry — present but disabled until its phase."""
    return render(request, 'foundation/settings/wallet.html', {'enabled': False})


@login_required
def settings_help(request):
    return render(request, 'foundation/settings/help.html')


@login_required
def settings_policies(request):
    return render(request, 'foundation/settings/policies.html')


@login_required
def settings_legal(request):
    docs = LegalDocument.objects.filter(is_current=True).order_by('doc_type')
    return render(request, 'foundation/settings/legal.html', {'documents': docs})


@login_required
def delete_account(request):
    """LGPD right to erasure — confirm, log, anonymize, deactivate."""
    if request.method == 'POST':
        form = DeleteAccountForm(request.user, request.POST)
        if form.is_valid():
            AccountDeletionRequest.objects.create(
                user=request.user,
                status='processed',
                reason=form.cleaned_data['reason'],
                processed_at=timezone.now(),
            )
            audit(request, 'account_deletion_requested', entity=request.user)
            anonymize_user(request.user)
            logout(request)
            messages.success(
                request,
                'Sua conta foi excluída. Seus dados pessoais foram removidos conforme a LGPD.',
            )
            return redirect('core:home')
    else:
        form = DeleteAccountForm(request.user)
    return render(request, 'foundation/settings/delete_account.html', {'form': form})
