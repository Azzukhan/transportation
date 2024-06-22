from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=25)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unpaid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    po_box = models.CharField(max_length=20)  

    def __str__(self):
        return self.name

class Trip(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField()
    freight = models.CharField(max_length=25)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    toll_gate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    driver = models.CharField(max_length=30)
    paid = models.BooleanField(default=False)
    

class Invoice(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.company.name} from {self.start_date} to {self.end_date}"

