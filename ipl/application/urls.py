from django.urls import include, path, re_path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    re_path('driver/?$', DriverView.as_view(), name='driver'),
    re_path('truck/?$', TruckView.as_view(), name='truck'),
    re_path('consignee/?$', ConsigneeView.as_view(), name='consignee'),
    re_path('consignor/?$', ConsignorView.as_view(), name='consignor'),
    re_path('landingpage/?$', LandingPageView.as_view(), name='landingpage'),
    re_path('challan/?$', LoadingChallanView.as_view(), name='loadingchallan'),
    re_path('bill-generation/?$', BillGenerationView.as_view(), name='billgeneration'),
    re_path('to-pay/?$', ToPayView.as_view(), name='to-pay'),
]