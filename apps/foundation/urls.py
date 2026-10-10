"""Foundation URL map — Phase 0 routing."""
from django.urls import path

from . import views

app_name = 'foundation'

urlpatterns = [
    # Public browsing
    path('categories/', views.categories, name='categories'),
    path('legal/', views.legal_list, name='legal'),
    path('legal/<slug:doc_type>/', views.legal_detail, name='legal_detail'),

    # Authenticated app
    path('app/', views.app_home, name='app_home'),
    path('app/onboarding/profissional/', views.onboarding_professional,
         name='onboarding_professional'),

    # Settings shell
    path('settings/', views.settings_home, name='settings_home'),
    path('settings/conta/', views.settings_account, name='settings_account'),
    path('settings/conta/excluir/', views.delete_account, name='delete_account'),
    path('settings/aparencia/', views.settings_appearance, name='settings_appearance'),
    path('settings/carteira/', views.settings_wallet, name='settings_wallet'),
    path('settings/ajuda/', views.settings_help, name='settings_help'),
    path('settings/politicas/', views.settings_policies, name='settings_policies'),
    path('settings/legal/', views.settings_legal, name='settings_legal'),

    # Google OAuth
    path('accounts/google/login/', views.google_login, name='google_login'),
    path('accounts/google/callback/', views.google_callback, name='google_callback'),
    path('accounts/google/consent/', views.google_consent, name='google_consent'),
]
