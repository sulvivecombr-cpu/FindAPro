from django.contrib import admin

from .models import (
    AccountDeletionRequest,
    AuditLog,
    ConsentRecord,
    LegalDocument,
    ProfessionalProfile,
    UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'account_type', 'status', 'locale', 'created_at')
    list_filter = ('role', 'account_type', 'status')
    search_fields = ('user__email', 'user__username')


@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'status', 'onboarding_completed', 'created_at')
    search_fields = ('user__email',)


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'version', 'granted_at', 'ip_address')
    list_filter = ('consent_type', 'version')
    readonly_fields = ('user', 'consent_type', 'version', 'granted_at',
                       'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False  # consents are only captured by the signup flow


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'requested_at', 'processed_at')
    readonly_fields = ('user', 'status', 'reason', 'requested_at', 'processed_at')

    def has_add_permission(self, request):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """AuditLog is append-only and writable only via foundation.services.audit()."""

    list_display = ('created_at', 'actor', 'action', 'entity_type', 'entity_id', 'ip_address')
    list_filter = ('action',)
    search_fields = ('action', 'actor__email')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Admin-only write surface for legal documents."""
    list_display = ('doc_type', 'version', 'title', 'is_current', 'published_at')
    list_filter = ('doc_type', 'is_current')
    search_fields = ('title',)
