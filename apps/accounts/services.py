from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_technician_invitation(technician, request):
    """Send a password setup invitation to a technician."""
    if technician.has_usable_password():
        raise ValueError("Le technicien possède déjà un mot de passe.")

    uid = urlsafe_base64_encode(force_bytes(technician.pk))
    token = default_token_generator.make_token(technician)

    invitation_path = reverse(
        "accounts:invitation_confirm",
        kwargs={
            "uidb64": uid,
            "token": token,
        },
    )

    invitation_url = request.build_absolute_uri(invitation_path)
    subject = "Invitation — Gestionnaire d'interventions"
    message = (
        f"Bonjour {technician.first_name},\n\n"
        "Un compte technicien a été créé pour vous.\n\n"
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
        recipient_list=[technician.email],
        fail_silently=False,
    )
