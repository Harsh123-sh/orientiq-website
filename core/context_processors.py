from .models import SiteSetting


def site_settings(request):
    return {
        "site_settings": SiteSetting.objects.filter(pk=1).first(),
        "whatsapp_message": (
            "Hi ORENTIQ, I'm interested in your services and would like to "
            "discuss my project. Could you please help me?"
        ),
    }