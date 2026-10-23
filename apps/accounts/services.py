from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import User

ACCOUNT_ROLE_LABELS = {
    User.Role.TECHNICIAN: "technicien",
    User.Role.MANAGER: "gestionnaire",
}


def send_account_invitation(user, request):
    """Send a password setup invitation to an eligible account."""
    if user.role not in ACCOUNT_ROLE_LABELS:
        raise ValueError("Ce type de compte ne peut pas être invité.")

    if not user.is_active:
        raise ValueError("Impossible d'inviter un compte désactivé.")

    if user.has_usable_password():
        raise ValueError("Ce compte possède déjà un mot de passe.")

    if not user.email:
        raise ValueError("Une adresse e-mail est nécessaire.")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    invitation_path = reverse(
        "accounts:invitation_confirm",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )

    invitation_url = request.build_absolute_uri(invitation_path)
    role_label = ACCOUNT_ROLE_LABELS[user.role]

    subject = "Invitation — Gestionnaire d'interventions"

    message = (
        f"Bonjour {user.first_name},\n\n"
        f"Un compte {role_label} a été créé pour vous.\n\n"
        "Pour définir votre mot de passe, utilisez le lien suivant :\n"
        f"{invitation_url}\n\n"
        "Ce lien est valable pendant 1 heure.\n\n"
        "Si vous n'attendiez pas cette invitation, contactez votre "
        "administrateur.\n"
    )

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_technician_invitation(technician, request):
    """Backward-compatible technician invitation service."""
    return send_account_invitation(technician, request)
