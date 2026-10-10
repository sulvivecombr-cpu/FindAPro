"""Foundation services: audit trail and LGPD consent capture."""
from django.utils import timezone


def client_ip(request):
    """Extract the client IP from a request."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or None


def user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')[:1000]


def audit(request, action, entity=None, actor=None):
    """Append an entry to the audit log. Admin-only write, append-only."""
    from .models import AuditLog

    if actor is None:
        user = getattr(request, 'user', None)
        actor = user if (user and user.is_authenticated) else None

    AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=type(entity).__name__ if entity else '',
        entity_id=str(entity.pk) if entity and entity.pk else '',
        ip_address=client_ip(request) if request else None,
        device=user_agent(request) if request else '',
    )


def capture_consent(request, user, consent_type):
    """Store a ConsentRecord for the document version in force right now."""
    from .models import ConsentRecord, LegalDocument

    doc = LegalDocument.objects.filter(
        doc_type=consent_type, is_current=True
    ).first()
    ConsentRecord.objects.create(
        user=user,
        consent_type=consent_type,
        version=doc.version if doc else '1.0',
        ip_address=client_ip(request),
        user_agent=user_agent(request),
    )


def anonymize_user(user):
    """LGPD right to erasure: strip personal data and deactivate the account."""
    import uuid

    user.is_active = False
    user.email = f'removido-{uuid.uuid4().hex[:12]}@nao-encontrado.findapro'
    user.first_name = 'Usuário'
    user.last_name = 'Removido'
    user.phone = ''
    user.bio = ''
    user.save(update_fields=['is_active', 'email', 'first_name', 'last_name', 'phone', 'bio'])

    profile = getattr(user, 'foundation_profile', None)
    if profile:
        profile.status = 'deleted'
        profile.save(update_fields=['status', 'updated_at'])
