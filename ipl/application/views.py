from django.shortcuts import render

from django.views.generic import View
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .forms import *
from .models import *

# from fpdf import FPDF, HTMLMixin
# from fpdf.html import HTML2FPDF
import html

# def generate_pdf(result_set):
#     data = []
#     pdf = PDF()
#     pdf.add_page()
#     data.append(("CONSIGNOR", "CONSIGNEE", "G.C. NO", "DATE", "TO", "PKGS", "WEIGHT", "TOPAY",
#                  "TBB", "PAID"))
#     for result in result_set:
#         data.append((result.consignor.name, result.consignee.name, str(result.id), str(result.billing_date),
#                      result.consignee_place, str(result.no_of_packages), str(result.charged_weight)))
#         #
#         # data = (
#         #     ("First name", "Last name", "Age", "City"),
#         #     ("Jules", "Smith", "34", "San Juan"),
#         #     ("Mary", "Ramos", "45", "Orlando"),
#         #     ("Carlson", "Banks", "19", "Los Angeles"),
#         #     ("Lucas", "Cimon", "31", "Saint-Mahturin-sur-Loire"),
#         # )
#     pdf.write_html(
#         f"""<table border="1"><thead><tr>
#                 <th width="4%">{data[0][0]}</th>
#                 <th width="18%">{data[0][1]}</th>
#                 <th width="18%">{data[0][2]}</th>
#                 <th width="10%">{data[0][3]}</th>
#                 <th width="10%">{data[0][4]}</th>
#                 <th width="10%">{data[0][5]}</th>
#                 <th width="10%">{data[0][6]}</th>
#                 <th width="10%">{data[0][7]}</th>
#                 <th width="10%">{data[0][8]}</th>
#                 <th width="10%">{data[0][9]}</th>
#             </tr></thead><tbody><tr>
#                 <td>{'</td><td>'.join(data[1])}</td>
#             </tr>
#             </tbody></table>"""
#     )
#     pdf.output('tuto1.pdf', 'F')
#     return FileResponse(open('tuto1.pdf', 'rb'))

from fpdf import FPDF
import xhtml2pdf
import wkhtmltopdf

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pdf_status = pisa.CreatePDF(html, dest=response)

    if pdf_status.err:
        return HttpResponse('Some errors were encountered <pre>' + html + '</pre>')

    return response

class PDF(FPDF):
    def lines(self):
        self.set_line_width(0.0)
        self.line(5.0,5.0,205.0,5.0) # top one
        self.line(5.0,292.0,205.0,292.0) # bottom one
        self.line(5.0,5.0,5.0,292.0) # left one
        self.line(205.0,5.0,205.0,292.0) # right one


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        # pdf = PDF(orientation='L')
        # pdf.add_page()
        # pdf.lines()
        # pdf.output('test.pdf', 'F')
        # return FileResponse(open('test.pdf', 'rb'))

        template_name = "sample1.html"

        # var = WKhtmlToPdf(
        #     url='https://www.cricbuzz.com/',
        #     output_file='~/Downloads/example.pdf',
        # )
        # print(1111)
        # print(var.render())
        return render_to_pdf(
            template_name,{}
        )



class LandingPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ShippingOrdersForm()
        consignee_list = ConsigneeModel.objects.all().values('id', 'name', 'gstin')
        consignor_list = ConsignorModel.objects.all().values('id', 'name', 'gstin')
        order_list = ShippingOrdersModel.objects.all()
        self.context = {
            'form': form,
            'consignees': consignee_list,
            'consignors': consignor_list,
            'orders': order_list,
            'order_saved': 0
        }
        return render(request, "landingpage.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        form = ShippingOrdersForm(self.post_params)
        order_saved = 0
        if form.is_valid():
            form.save()
            order_saved = 1
        consignee_list = ConsigneeModel.objects.all().values('id', 'name', 'gstin')
        consignor_list = ConsignorModel.objects.all().values('id', 'name', 'gstin')
        order_list = ShippingOrdersModel.objects.all()
        self.context = {
            'form': ShippingOrdersForm(),
            'consignees': consignee_list,
            'consignors': consignor_list,
            'order_saved': order_saved,
            'order_posted': 1,
            'orders': order_list
        }
        return render(request, "landingpage.html", self.context)


#         pdf = PDF()
#         pdf.add_page()
#
#         # creating a new image file with light blue color with A4 size dimensions using PIL
#         img = Image.new('RGB', (210, 297), "lightyellow")
#         img.save('blue_colored.png')
#
#         # adding image to pdf page that e created using fpdf
#         pdf.image('blue_colored.png', x=0, y=0, w=210, h=297, type='', link='')
#         # pdf.rect(20,20,20,20)
#         # pdf.set_font('Arial', 'B', 16)
#         # pdf.cell(40, 10, 'Hello World!')
#         data = (
#             ("First name", "Last name", "Age", "City"),
#             ("Jules", "Smith", "34", "San Juan"),
#             ("Mary", "Ramos", "45", "Orlando"),
#             ("Carlson", "Banks", "19", "Los Angeles"),
#             ("Lucas", "Cimon", "31", "Saint-Mahturin-sur-Loire"),
#         )
#         # pdf.write_html(
#         #     f"""<table border="1"><thead><tr>
#         #     <th width="25%">{data[0][0]}</th>
#         #     <th width="25%">{data[0][1]}</th>
#         #     <th width="15%">{data[0][2]}</th>
#         #     <th width="35%">{data[0][3]}</th>
#         # </tr></thead><tbody><tr>
#         #     <td>{'</td><td>'.join(data[1])}</td>
#         # </tr><tr>
#         #     <td>{'</td><td>'.join(data[2])}</td>
#         # </tr><tr>
#         #     <td>{'</td><td>'.join(data[3])}</td>
#         # </tr><tr>
#         #     <td>{'</td><td>'.join(data[4])}</td>
#         # </tr></tbody></table>"""
#         # )
#
#         str1 = """
# <H1 align="center">html2fpdf</H1>
# <h2>Basic usage</h2>
# <p>You can now easily print text mixing different
# styles : <B>bold</B>, <I>italic</I>, <U>underlined</U>, or
# <B><I><U>all at once</U></I></B>!<BR>You can also insert links
# on text, such as <A HREF="http://www.fpdf.org">www.fpdf.org</A>,
# or on an image: click on the logo.<br>
# <center>
# </center>
# <h3>Sample List</h3>
# <ul><li>option 1</li>
# <ol><li>option 2</li></ol>
# <li>option 3</li></ul>
#
# <table border="0" align="center" width="50%">
# <thead>
#     <tr>
#         <th width="40%">Header 1</th>
#         <th width="40%">header 2</th>
#     </tr>
# </thead>
# <tbody>
#     <tr>
#         <td>cell 1</td>
#         <td>cell 2</td>
#     </tr>
#     <tr>
#         <td>cell 2</td>
#         <td>cell 3</td>
#     </tr>
# </tbody>
# </table>
#         """
#         pdf.write_html(
#             str1
#         )
#         pdf.output('tuto1.pdf', 'F')
#         return FileResponse(open('tuto1.pdf', 'rb'))
# return HttpResponseRedirect(reverse("application:loadingchallan", kwargs={"id":form.instance.id}))


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
        return render(request, "loading_challan.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        generate_challan = int(self.post_params.get("challan", 0))
        form = LoadingChallForm(self.post_params)
        if form.is_valid():
            result_set = ShippingOrdersModel.objects.filter(
                created_dtm__lt=form.cleaned_data.get("billing_date"),
                consignor_place=form.cleaned_data.get("place_of_receipt"),
                consignee_place=form.cleaned_data.get("place_of_delivery"),
                loading_challan=None
            )

            # if generate_challan:
            #     form.save()
            #     for result in result_set:
            #         result.loading_challan = form.instance
            #         result.save()
            #
            #     return generate_pdf(result_set)

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
        result_set = ShippingOrdersModel.objects.exclude(loading_challan=None).filter(bill=None)
        if len(result_set) == 0:
            return render(request, "app_static_content.html")

        consignor_list = ConsignorModel.objects.all().values('id', 'name')
        self.context = {
            'form': form,
            'consignors': consignor_list,
            "no_orders_present": True if request.GET.copy().get("no_orders_present", None) else False
        }
        return render(request, "bill_generation.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        generate_bill = int(self.post_params.get("bill", 0))
        form = BillForm(self.post_params)
        if form.is_valid():
            result_set = ShippingOrdersModel.objects.exclude(loading_challan=None).filter(
                bill=None,
                consignor=form.cleaned_data.get("consignor")
            )
            if len(result_set) == 0:
                return HttpResponseRedirect(reverse("application:billgeneration") + '?no_orders_present=true')

            # if generate_bill:
            #     form.save()
            #     for result in result_set:
            #         result.bill = form.instance
            #         result.save()
            #
            #     return generate_pdf(result_set)

            consignor_list = ConsignorModel.objects.all().values('id', 'name')
            self.context = {
                'form': form,
                'consignors': consignor_list,
                'result_set': result_set,
                "no_orders_present": True if request.GET.copy().get("no_orders_present", None) else False
            }
            return render(request, "bill_generation.html", self.context)


# class PDF(FPDF, HTMLMixin):
#     def write_html(self, text, image_map=None):
#         h2p = HTML2FPDF(self, image_map)
#         text = html.unescape(text)  # To deal with HTML entities
#         h2p.feed(text)


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
        return render(request, "driver.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        form = DriverForm(self.post_params, request.FILES)
        if form.is_valid():
            form.save()
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
        return render(request, "truck.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        form = TruckForm(self.post_params)
        if form.is_valid():
            truck_no = form.cleaned_data.get("truck_number")
            if TruckModel.objects.filter(truck_number=truck_no).exists():
                truck_exists = 1
                self.context = {
                    'form': form,
                    'trucks': TruckModel.objects.all(),
                    "truck_exists": truck_exists
                }
                return render(request, "truck.html", self.context)
            try:
                form.save()
                self.context = {
                    'form': TruckForm(),
                    'trucks': TruckModel.objects.all(),
                    "upload_status": 1
                }
                return render(request, "truck.html", self.context)
            except Exception as e:
                print(e)


class ConsigneeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ConsigneeForm()
        self.context = {
            'form': form,
            'consignees': ConsigneeModel.objects.all()
        }
        return render(request, "consignee.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        form = ConsigneeForm(self.post_params, request.FILES)
        if form.is_valid():
            form.save()
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
        return render(request, "consignor.html", self.context)

    def post(self, request, *args, **kwargs):
        self.post_params = request.POST.copy()
        form = ConsignorForm(self.post_params, request.FILES)
        if form.is_valid():
            form.save()
        self.context = {
            'form': ConsignorForm(),
            'consignors': ConsignorModel.objects.all(),
            "upload_status": 1
        }
        return render(request, "consignor.html", self.context)


class CashReceiptView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ConsignorForm()
        self.context = {
            'form': form,
            'consignors': ConsignorModel.objects.all()
        }
        return render(request, "consignor.html", self.context)
