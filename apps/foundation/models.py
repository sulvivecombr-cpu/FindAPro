"""
Foundation data model — Phase 0.

Row-level security is enforced at the application layer:
- UserProfile / ConsentRecord / AccountDeletionRequest: users may only read
  and write their own rows (see ``for_user`` and the views that use them).
- AuditLog: written only by the audit service; never exposed to end users.
- LegalDocument: public read of published documents; written only by staff
  through the Django admin.
"""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Profile attached to every user: role, account type, status, locale."""

    ROLE_CHOICES = [
        ('client', 'Cliente'),
        ('professional', 'Profissional'),
        ('admin', 'Administrador'),
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('individual', 'Pessoa física (CPF)'),
        ('company', 'Pessoa jurídica (CNPJ)'),
        ('autonomous', 'Autônomo (CPF)'),
        ('mei', 'MEI (CNPJ)'),
    ]

    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('deleted', 'Excluída'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='foundation_profile',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='individual'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    locale = models.CharField(max_length=10, default='pt-br')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuário'
        verbose_name_plural = 'Perfis de usuário'

    def __str__(self):
        return f'{self.user} ({self.get_role_display()})'

    @classmethod
    def for_user(cls, user):
        """Row-level security: a user can only access their own profile."""
        if not user.is_authenticated:
            return cls.objects.none()
        return cls.objects.filter(user=user)


class ProfessionalProfile(models.Model):
    """Stub for the professional onboarding path (later phases expand it)."""

    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('active', 'Ativo'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='professional_profile',
    )
    headline = models.CharField('Título profissional', max_length=120, blank=True)
    about = models.TextField('Sobre', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil profissional'
        verbose_name_plural = 'Perfis profissionais'

    def __str__(self):
        return f'Perfil profissional de {self.user}'


class ConsentRecord(models.Model):
    """LGPD consent capture (Lei 13.709/2018)."""

    CONSENT_TYPES = [
        ('terms', 'Termos de Uso'),
        ('privacy', 'Política de Privacidade'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consents',
    )
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPES)
    version = models.CharField(max_length=20)
    granted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Registro de consentimento'
        verbose_name_plural = 'Registros de consentimento'

    def __str__(self):
        who = self.user or 'usuário removido'
        return f'{self.get_consent_type_display()} v{self.version} — {who}'

    @classmethod
    def for_user(cls, user):
        """Row-level security: only the data subject reads their consents."""
        if not user.is_authenticated:
            return cls.objects.none()
        return cls.objects.filter(user=user)


class AccountDeletionRequest(models.Model):
    """LGPD right to erasure — self-service account deletion."""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processed', 'Processada'),
        ('cancelled', 'Cancelada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deletion_requests',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processed')
    reason = models.TextField('Motivo (opcional)', blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitação de exclusão de conta'
        verbose_name_plural = 'Solicitações de exclusão de conta'

    def __str__(self):
        return f'Exclusão — {self.user} ({self.status})'

    @classmethod
    def for_user(cls, user):
        """Row-level security: only the account owner sees their requests."""
        if not user.is_authenticated:
            return cls.objects.none()
        return cls.objects.filter(user=user)


class AuditLog(models.Model):
    """Immutable audit trail. Written only by foundation.services.audit()."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_entries',
    )
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.TextField('User agent', blank=True)

    class Meta:
        verbose_name = 'Registro de auditoria'
        verbose_name_plural = 'Registros de auditoria'
        ordering = ['-created_at']

    def __str__(self):
        who = self.actor or 'sistema'
        return f'{self.created_at:%Y-%m-%d %H:%M} — {who} — {self.action}'

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # Append-only: audit entries can never be modified.
            raise ValueError('Registros de auditoria são imutáveis.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('Registros de auditoria não podem ser removidos.')

    @classmethod
    def for_user(cls, user):
        """Row-level security: only staff may read the audit trail."""
        if not user.is_authenticated or not user.is_staff:
            return cls.objects.none()
        return cls.objects.all()


class LegalDocument(models.Model):
    """Versioned legal documents (Terms, Privacy, etc.), edited by staff."""

    DOC_TYPES = [
        ('termos', 'Termos de Uso'),
        ('privacidade', 'Política de Privacidade'),
        ('provedores-dados', 'Provedores de Dados'),
        ('licenca-software', 'Licença de Software'),
        ('localizacao', 'Localização'),
    ]

    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    version = models.CharField(max_length=20, default='1.0')
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Documento legal'
        verbose_name_plural = 'Documentos legais'
        unique_together = [('doc_type', 'version')]
        ordering = ['doc_type', '-published_at']

    def __str__(self):
        return f'{self.title} (v{self.version})'

    @classmethod
    def for_user(cls, user):
        """Row-level security: published docs are public; staff sees all."""
        return cls.objects.all()
