from django.shortcuts import render

from django.views.generic import View
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import *
from .models import *

import logging
import os
import base64

logger = logging.getLogger(__name__)


class LandingPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.get_params = request.GET.copy()
        order_saved = self.get_params.get("order_saved", 0)
        form = ShippingOrdersForm()
        consignee_list = ConsigneeModel.objects.all().values('id', 'name', 'gstin')
        consignor_list = ConsignorModel.objects.all().values('id', 'name', 'gstin')
        order_list = ShippingOrdersModel.objects.all()
        self.context = {
            'form': form,
            'consignees': consignee_list,
            'consignors': consignor_list,
            'orders': order_list,
            'order_saved': order_saved or kwargs.get("order_saved")
        }
        logger.info("[LANDINGPAGE] - GET REQUEST | USER - {}".format(request.user.email))
        response = render(request, "landingpage.html", self.context)
        logger.info("[LANDINGPAGE] - SETTING COOKIE as 1 | USER - {}".format(request.user.email))
        response.set_cookie("landing", 1, 5 * 60 * 60)
        return response

    def post(self, request, *args, **kwargs):
        is_cookie_present = request.COOKIES.get("landing", 0)
        if not is_cookie_present:
            logger.info("[LANDINGPAGE] - DUPLICATE CALL | ORDER ALREADY SAVED | USER - {}".format(request.user.email))
            logger.info("[LANDINGPAGE] - REDIRECTING TO GET PAGE | USER - {}".format(request.user.email))
            kwargs["order_saved"] = 1
            return self.get(request, *args, **kwargs)
        self.post_params = request.POST.copy()
        logger.info(
            "[LANDINGPAGE] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        form = ShippingOrdersForm(self.post_params)
        if form.is_valid():
            logger.info("[LANDINGPAGE] - FORM VALIDATED | USER - {}".format(request.user.email))
            form.save()
            logger.info("[LANDINGPAGE] - ORDER SAVED | USER - {}".format(request.user.email))
            self.context = {
                "order": ShippingOrdersModel.objects.get(id=form.instance.id)
            }
            response = render(request, "order_copy.html", self.context)
            logger.info("[LANDINGPAGE] - DELETING COOKIE | USER - {}".format(request.user.email))
            response.delete_cookie("landing")
            return response

        # consignee_list = ConsigneeModel.objects.all().values('id', 'name', 'gstin')
        # consignor_list = ConsignorModel.objects.all().values('id', 'name', 'gstin')
        # order_list = ShippingOrdersModel.objects.all()
        # self.context = {
        #     'form': ShippingOrdersForm(),
        #     'consignees': consignee_list,
        #     'consignors': consignor_list,
        #     'order_saved': order_saved,
        #     'order_posted': 1,
        #     'orders': order_list
        # }
        # return render(request, "landingpage.html", self.context)


class LoadingChallanView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = LoadingChallForm()
        result_set = ShippingOrdersModel.objects.filter(loading_challan=None)
        if len(result_set) == 0:
            return render(request, "app_static_content.html")
        driver_list = DriverModel.objects.all().values('id', 'name', 'contact_number')
        truck_list = TruckModel.objects.all().values('id', 'truck_number')
        consignee_list = ConsigneeModel.objects.all().values('id', 'name')
        consignor_list = ConsignorModel.objects.all().values('id', 'name')
        self.context = {
            'form': form,
            'driver_list': driver_list,
            'truck_list': truck_list,
            'consignees': consignee_list,
            'consignors': consignor_list,
            "no_orders_present": True if request.GET.copy().get("no_orders_present", None) else False
        }
        logger.info("[LOADING CHALLAN] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "loading_challan.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info(
            "[LOADING CHALLAN] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        generate_challan = int(self.post_params.get("challan", 0))
        form = LoadingChallForm(self.post_params)
        if form.is_valid():
            logger.info("[LOADING CHALLAN] - FORM VALIDATED | USER - {}".format(request.user.email))
            result_set = ShippingOrdersModel.objects.filter(
                created_dtm__lt=form.cleaned_data.get("billing_date"),
                consignor_place=form.cleaned_data.get("place_of_receipt"),
                consignee_place=form.cleaned_data.get("place_of_delivery"),
                loading_challan=None
            ).exclude(payment_status="to_pay")

            if generate_challan and result_set:
                logger.info("[LOADING CHALLAN] - GENERATING CHALLAN | USER - {}".format(request.user.email))
                form.save()
                for result in result_set:
                    result.loading_challan = form.instance
                    result.save()
                self.context = {
                    "result_set": result_set,
                    "lc": form.instance
                }
                return render(request, "lc_copy.html", self.context)

            driver_list = DriverModel.objects.all().values('id', 'name', 'contact_number')
            truck_list = TruckModel.objects.all().values('id', 'truck_number')
            consignee_list = ConsigneeModel.objects.all().values('id', 'name')
            consignor_list = ConsignorModel.objects.all().values('id', 'name')
            selected_driver_id = form.cleaned_data.get("driver").id
            selected_driver_contact = form.cleaned_data.get("driver").contact_number
            selected_place_of_delivery = form.cleaned_data.get("place_of_delivery")
            selected_vehicle_no_id = form.cleaned_data.get("vehicle_no").id
            self.context = {
                'r_method': "POST",
                "selected_driver_id": selected_driver_id,
                "selected_driver_contact": selected_driver_contact,
                "selected_vehicle_no_id": selected_vehicle_no_id,
                "selected_place_of_delivery": selected_place_of_delivery,
                'form': form,
                'driver_list': driver_list,
                'truck_list': truck_list,
                'consignees': consignee_list,
                'consignors': consignor_list,
                'result_set': result_set
            }
            return render(request, "loading_challan.html", self.context)


class BillGenerationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BillForm()
        # for result in ShippingOrdersModel.objects.all():
        #     result.bill = None
        #     result.loading_challan = None
        #     result.save()
        result_set = ShippingOrdersModel.objects.filter(bill=None)
        if len(result_set) == 0:
            return render(request, "app_static_content.html")

        consignor_list = ConsignorModel.objects.all().values('id', 'name')
        self.context = {
            'form': form,
            'consignors': consignor_list,
            "no_orders_present": True if request.GET.copy().get("no_orders_present", None) else False
        }
        logger.info("[BILL GENERATION] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "bill_generation.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info(
            "[BILL GENERATION] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))

        generate_bill = int(self.post_params.get("bill", 0))
        form = BillForm(self.post_params)
        if form.is_valid():
            logger.info("[BILL GENERATION] - FORM VALIDATED | USER - {}".format(request.user.email))
            result_set = ShippingOrdersModel.objects.filter(
                bill=None,
                consignor=form.cleaned_data.get("consignor"),
                payment_status="tbb"
            )
            if len(result_set) == 0:
                return HttpResponseRedirect(reverse("application:billgeneration") + '?no_orders_present=true')

            if generate_bill and result_set:
                logger.info("[BILL GENERATION] - GENERATING BILL | USER - {}".format(request.user.email))
                form.save()
                total_amount = 0
                for result in result_set:
                    result.bill = form.instance
                    result.save()
                    total_amount += result.total_charges

                self.context = {
                    "result_set": result_set,
                    "bill": form.instance,
                    "total_amount": total_amount
                }
                return render(request, "bill_copy.html", self.context)

            consignor_list = ConsignorModel.objects.all().values('id', 'name')
            self.context = {
                'form': form,
                'consignors': consignor_list,
                'result_set': result_set,
                "no_orders_present": True if request.GET.copy().get("no_orders_present", None) else False,
                "selected_consignee": form.cleaned_data.get("consignor").id
            }
            return render(request, "bill_generation.html", self.context)


class ReportsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.post_params = request.GET.copy()
        payment_status = self.post_params.get("payment_status", None)
        result_set = ShippingOrdersModel.objects.filter(payment_status=payment_status)
        total_amount = 0
        for obj in result_set:
            total_amount += obj.total_charges
        self.context = {
            "payment_status": payment_status,
            "result_set": result_set,
            "total_amount": total_amount
        }
        return render(request, "reports.html", self.context)


class DownloadsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.context = {
            "order": ShippingOrdersModel.objects.get(id=self.request.GET.get('order'))
        }
        return render(request, "bill_copy.html", self.context)

    def post(self, request, *args, **kwargs):
        self.get_params = request.GET.copy()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_type = self.get_params.get('download_type')
        if download_type == "lc":
            filename = "{}_lc.pdf".format(request.POST.get("id"))
            folder_name = "lc"
        elif download_type == "order":
            order_copy_type = self.get_params.get('order_copy_type')
            filename = "{}_{}.pdf".format(request.POST.get("id"), order_copy_type)
            folder_name = "orders"
        elif download_type == "bill":
            filename = "{}_bill.pdf".format(request.POST.get("id"))
            folder_name = "bill"
        file = os.path.join(BASE_DIR, 'media', 'documents', folder_name, filename)
        with open(file, 'wb') as destination:
            destination.write(base64.b64decode(request.POST.get("pdf_data")))
        return HttpResponse("")


class ToPayView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        result_set = ShippingOrdersModel.objects.filter(payment_status="to_pay")

        self.context = {
            "result_set": result_set
        }
        return render(request, "to_pay.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        order_list = tuple(map(int, ''.join(request.POST.getlist("order_list")).split(',')))
        filtered_list = ShippingOrdersModel.objects.filter(id__in=order_list)
        if filtered_list:
            filtered_list.update(payment_status="paid")
        result_set = ShippingOrdersModel.objects.filter(payment_status="to_pay")

        self.context = {
            "result_set": result_set,
            "update_status": 1
        }
        return render(request, "to_pay.html", self.context)


class DriverView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = DriverForm()
        self.context = {
            'form': form,
            'drivers': DriverModel.objects.all()
        }
        for obj in self.context.get("drivers"):
            obj.license_document.name = obj.license_document.name[10:]
        logger.info("[DRIVER] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "driver.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info("[DRIVER] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        form = DriverForm(self.post_params, request.FILES)
        if form.is_valid():
            logger.info("[DRIVER] - FORM VALIDATED | USER - {}".format(request.user.email))
            if DriverModel.objects.filter(name=form.cleaned_data.get("name"),
                                          contact_number=form.cleaned_data.get("contact_number")).exists():
                logger.info("[DRIVER] - DRIVER ALREADY EXISTS | USER - {}".format(request.user.email))
                self.context = {
                    'form': form,
                    'drivers': DriverModel.objects.all(),
                    'driver_exists': 1
                }
                for obj in self.context.get("drivers"):
                    obj.license_document.name = obj.license_document.name[10:]
                return render(request, "driver.html", self.context)

            form.save()
            logger.info("[DRIVER] - DRIVER SAVED | USER - {}".format(request.user.email))
            self.context = {
                'form': DriverForm(),
                'drivers': DriverModel.objects.all(),
                "upload_status": 1
            }
            for obj in self.context.get("drivers"):
                obj.license_document.name = obj.license_document.name[10:]
            return render(request, "driver.html", self.context)


class TruckView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = TruckForm()
        self.context = {
            'form': form,
            'trucks': TruckModel.objects.all()
        }
        logger.info("[TRUCK] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "truck.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info("[TRUCK] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        form = TruckForm(self.post_params)
        if form.is_valid():
            logger.info("[TRUCK] - FORM VALIDATED | USER - {}".format(request.user.email))
            truck_no = form.cleaned_data.get("truck_number")
            if TruckModel.objects.filter(truck_number=truck_no).exists():
                logger.info("[TRUCK] - TRUCK ALREADY EXISTS | USER - {}".format(request.user.email))
                truck_exists = 1
                self.context = {
                    'form': form,
                    'trucks': TruckModel.objects.all(),
                    "truck_exists": truck_exists
                }
                return render(request, "truck.html", self.context)
            form.save()
            logger.info("[TRUCK] - TRUCK SAVED | USER - {}".format(request.user.email))
            self.context = {
                'form': TruckForm(),
                'trucks': TruckModel.objects.all(),
                "upload_status": 1
            }
            return render(request, "truck.html", self.context)


class ConsigneeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ConsigneeForm()
        self.context = {
            'form': form,
            'consignees': ConsigneeModel.objects.all()
        }
        logger.info("[CONSIGNEE] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "consignee.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info("[CONSIGNEE] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        form = ConsigneeForm(self.post_params, request.FILES)
        if form.is_valid():
            logger.info("[CONSIGNEE] - FORM VALIDATED | USER - {}".format(request.user.email))
            if ConsigneeModel.objects.filter(name=form.cleaned_data.get("name"),
                                             gstin=form.cleaned_data.get("gstin")).exists():
                logger.info("[CONSIGNEE] - CONSIGNEE ALREADY EXISTS | USER - {}".format(request.user.email))
                self.context = {
                    'form': form,
                    'consignees': ConsigneeModel.objects.all(),
                    'consignee_exists': 1
                }
                return render(request, "consignee.html", self.context)

            form.save()
            logger.info("[CONSIGNEE] - CONSIGNEE SAVED | USER - {}".format(request.user.email))
        self.context = {
            'form': ConsigneeForm(),
            'consignees': ConsigneeModel.objects.all(),
            "upload_status": 1
        }
        return render(request, "consignee.html", self.context)


class ConsignorView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ConsignorForm()
        self.context = {
            'form': form,
            'consignors': ConsignorModel.objects.all()
        }
        logger.info("[CONSIGNOR] - GET REQUEST | USER - {}".format(request.user.email))
        return render(request, "consignor.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        logger.info("[CONSIGNOR] - POST REQUEST | PARAMS - {} |USER - {}".format(self.post_params, request.user.email))
        form = ConsignorForm(self.post_params, request.FILES)
        if form.is_valid():
            logger.info("[CONSIGNOR] - FORM VALIDATED | USER - {}".format(request.user.email))
            if ConsignorModel.objects.filter(name=form.cleaned_data.get("name"),
                                             gstin=form.cleaned_data.get("gstin")).exists():
                logger.info("[CONSIGNEE] - CONSIGNEE ALREADY EXISTS | USER - {}".format(request.user.email))
                self.context = {
                    'form': form,
                    'consignors': ConsignorModel.objects.all(),
                    'consignor_exists': 1
                }
                return render(request, "consignor.html", self.context)
            form.save()
            logger.info("[CONSIGNOR] - CONSIGNOR SAVED | USER - {}".format(request.user.email))
        self.context = {
            'form': ConsignorForm(),
            'consignors': ConsignorModel.objects.all(),
            "upload_status": 1
        }
        return render(request, "consignor.html", self.context)


class CashReceiptView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "cash_receipt.html", {})
