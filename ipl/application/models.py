from django.db import models
from django.db.models.deletion import CASCADE


def user_directory_path(instance, filename):
    return 'ipl/media/documents/driver/{0}_{1}'.format(instance.name, filename)


class DriverModel(models.Model):
    name = models.CharField(max_length=45)
    contact_number = models.BigIntegerField(default=None)
    alternate_contact = models.BigIntegerField(default=None)
    family_contact = models.BigIntegerField(default=None)
    date_of_joining = models.DateField(default=None)
    license_number = models.CharField(max_length=45)
    license_document = models.FileField(upload_to=user_directory_path)
    address_permanent = models.CharField(max_length=300, default=None)
    address_temporary = models.CharField(max_length=300, default=None)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Driver'
        get_latest_by = 'created_dtm'
        ordering = ['name']


class TruckModel(models.Model):
    truck_number = models.CharField(max_length=45)
    no_of_wheels = models.IntegerField(default=None)
    model = models.IntegerField(default=None)
    feet = models.IntegerField(default=None)
    mileage = models.IntegerField(default=None)
    manufacture_name = models.CharField(max_length=45)
    manufacture_date = models.DateField(default=None)
    truck_type = models.CharField(max_length=45)
    tonnage = models.CharField(max_length=300)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Truck'
        get_latest_by = 'created_dtm'
        ordering = ['truck_number']


class ConsigneeModel(models.Model):
    name = models.CharField(max_length=45)
    contact = models.BigIntegerField()
    gstin = models.CharField(max_length=15)
    address = models.CharField(max_length=300)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Consignee'
        get_latest_by = 'created_dtm'


class ConsignorModel(models.Model):
    name = models.CharField(max_length=45)
    contact = models.BigIntegerField()
    gstin = models.CharField(max_length=15)
    address = models.CharField(max_length=300)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Consignor'
        get_latest_by = 'created_dtm'


class BillModel(models.Model):
    consignor = models.ForeignKey(ConsignorModel, on_delete=CASCADE)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bill'
        get_latest_by = 'created_dtm'


class LoadingChallanModel(models.Model):
    class ConsigneePlaces(models.TextChoices):
        indore = 'indore', ('Indore')
        nagpur = 'nagpur', ('Nagpur')
        pune = 'pune', ('Pune')
        secunderabad = 'secunderabad', ('Secunderabad')

    lc_no = models.AutoField(primary_key=True)
    billing_date = models.DateField(default=None)
    place_of_receipt = models.CharField(max_length=45, default="Coimbatore")
    place_of_delivery = models.CharField(max_length=45, choices=ConsigneePlaces.choices, default=None)
    driver = models.ForeignKey(DriverModel, on_delete=CASCADE)
    vehicle_no = models.ForeignKey(TruckModel, on_delete=CASCADE)
    supplier = models.CharField(max_length=45)
    weight = models.CharField(max_length=45)
    vehicle_hire = models.IntegerField()
    advance_amount = models.FloatField()
    balance_amount = models.FloatField()
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LoadingChallan'
        get_latest_by = 'created_dtm'


class ShippingOrdersModel(models.Model):
    class TaxPayable(models.TextChoices):
        Male = 'Consignee', ('Consignee')
        Female = 'Consignor', ('Consignor')
        Transgender = 'IPL', ('IPL')

    class PaymentStatus(models.TextChoices):
        to_pay = 'to_pay', ('To Pay')
        tbb = 'tbb', ('To be Billed')
        paid = 'paid', ('PAID')

    class ConsigneePlaces(models.TextChoices):
        indore = 'indore', ('Indore')
        nagpur = 'nagpur', ('Nagpur')
        pune = 'pune', ('Pune')
        secunderabad = 'secunderabad', ('Secunderabad')

    consignor = models.ForeignKey(ConsignorModel, on_delete=CASCADE)
    consignor_gst = models.CharField(max_length=15)
    consignor_place = models.CharField(max_length=15, default="Coimbatore")
    consignee = models.ForeignKey(ConsigneeModel, on_delete=CASCADE)
    consignee_gst = models.CharField(max_length=15)
    consignee_place = models.CharField(max_length=15, choices=ConsigneePlaces.choices, default=None)
    no_of_packages = models.CharField(max_length=15)
    package_value = models.IntegerField()
    package_description = models.CharField(max_length=115)
    actual_weight = models.FloatField()
    charged_weight = models.FloatField()
    freight_charges = models.FloatField()
    lr_charges = models.FloatField()
    hamali_charges = models.FloatField()
    door_collection = models.FloatField()
    door_delivery = models.FloatField()
    other_charges = models.FloatField()
    total_charges = models.FloatField()
    paid_amount = models.FloatField()
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=None)
    invoice_no = models.IntegerField()
    invoice_date = models.DateField(default=None)
    billing_date = models.DateField(default=None)
    gs_tax_payable = models.CharField(max_length=20, choices=TaxPayable.choices, default=None)
    created_dtm = models.DateTimeField(auto_now_add=True)
    updated_dtm = models.DateTimeField(auto_now=True)
    loading_challan = models.ForeignKey(LoadingChallanModel, on_delete=CASCADE, default=None, null=True)
    bill = models.ForeignKey(BillModel, on_delete=CASCADE, default=None, null=True)

    class Meta:
        db_table = 'Orders'
        get_latest_by = 'created_dtm'
