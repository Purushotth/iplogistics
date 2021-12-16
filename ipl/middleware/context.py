from django.urls import reverse
from config.ipl_config import SECONDARY_USERS

def extra_context(request):
    secondary_user = False
    if getattr(request.user, "email", None):
        if request.user.email.lower() in (SECONDARY_USERS):
            secondary_user = True

    context = {
        "driver_url":reverse('application:driver'),
        "truck_url": reverse('application:truck'),
        "consignee_url": reverse('application:consignee'),
        "consignor_url": reverse('application:consignor'),
        "landingpage_url": reverse('application:landingpage'),
        "loading_challan_url": reverse('application:loadingchallan'),
        "generate_bill_url": reverse('application:billgeneration'),
        "logout_url": reverse('account:logout'),
        "secondary_user": secondary_user
    }

    return context