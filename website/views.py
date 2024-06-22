# website/views.py
from .forms import QuoteRequestForm
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection, EmailMultiAlternatives

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CompanyForm, TripForm, LoginRequestForm
from .models import Company, Trip, Invoice
from django.db.models import Sum, Q
from datetime import datetime
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
import pdfkit
import os
# views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import Company, Trip
from decimal import Decimal

def generate_invoice_number():
    last_invoice = Invoice.objects.all().order_by('id').last()
    if not last_invoice:
        return 'TAX/IN/1'
    invoice_no = last_invoice.id + 1
    return f'TAX/IN/{invoice_no}'

def fetch_resources(uri, rel):
    # Handle local file paths or resources from the internet
    if uri.startswith('/'):
        # Convert local file paths to Django's MEDIA_ROOT
        path = os.path.join(settings.MEDIA_ROOT, uri.lstrip('/'))
    else:
        # Handle resources from the internet or other external sources
        path = uri

    try:
        # Open and read the content of the resource
        with open(path, 'rb') as file:
            data = file.read()
    except FileNotFoundError:
        # Return None if the file is not found
        return None

    # Return a tuple containing the content type and data
    return ('application/octet-stream', data)

@login_required
def download_invoice(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    trips = Trip.objects.filter(company=company, paid=False)  # Only consider unpaid trips

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        driver_name = request.POST.get('driver_name')

        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            trips = trips.filter(date__gte=from_date, date__lte=to_date)

        if driver_name:
            trips = trips.filter(driver__icontains=driver_name)

        total_invoice_amount = trips.aggregate(Sum('amount'))['amount__sum']
        total_amount_include_vat = Decimal('0.00')
        total_vat_amount = Decimal('0.00')
        total_toll_amount = Decimal('0.00')

        for trip in trips:
            # Calculate VAT and total amount for each trip
            trip.vat = trip.amount * Decimal('0.05')
            trip.total_amount = trip.amount + trip.vat + trip.toll_gate
            total_amount_include_vat += trip.total_amount
            total_vat_amount += trip.vat
            total_toll_amount += trip.toll_gate
            trip.paid = True

            # Update company amounts
            company.paid_amount += trip.total_amount
            company.unpaid_amount -= trip.total_amount

            # Save changes
            company.save()
            trip.save()

        # Generate Invoice PDF
        context = {
            'company': company,
            'trips': trips,
            'total_amount_include_vat': total_amount_include_vat,
            'total_vat_amount': total_vat_amount,
            'total_amount': total_invoice_amount,
            'total_toll_amount': total_toll_amount,
            'invoice_date': datetime.now(),
            'invoice_number': generate_invoice_number()  # Implement this function as needed
        }

        html = render_to_string('invoice_template.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{company.id}.pdf"'

        pisa_status = pisa.CreatePDF(
            html, dest=response, encoding='utf-8',
            link_callback=fetch_resources  # Define fetch_resources function as needed
        )

        if pisa_status.err:
            return HttpResponse('Error generating PDF: %s' % html)

        return response

    return render(request, 'download_invoice.html', {'company': company})

    

def login(request):
    if request.method == 'POST':
        form = LoginRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('dashboard')  # Redirect to admin dashboard after login
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginRequestForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    companies = Company.objects.all()
    total_companies = companies.count()
    total_paid_amount = sum(company.paid_amount for company in companies)
    total_unpaid_amount = sum(company.unpaid_amount for company in companies)
    
    context = {
        'companies': companies,
        'total_companies': total_companies,
        'total_paid_amount': total_paid_amount,
        'total_unpaid_amount': total_unpaid_amount,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            # Initialize paid_amount and unpaid_amount to zero for the new company
            new_company = Company.objects.latest('id')
            new_company.paid_amount = 0
            new_company.unpaid_amount = 0
            new_company.save()
            return redirect('dashboard')
    else:
        form = CompanyForm()
    return render(request, 'add_company.html', {'form': form})

def add_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)  # Save the form data but don't commit to database yet
            trip.vat = trip.amount * Decimal('0.05')
            trip.total_amount = trip.amount + trip.vat + trip.toll_gate
            trip.save()  # Commit the trip to database

            # Update the unpaid_amount of the associated company
            trip.company.unpaid_amount += trip.total_amount
            trip.company.save()

            messages.success(request, 'Trip added successfully.')
            return redirect('add_trip')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TripForm()
    return render(request, 'add_trip.html', {'form': form})



@login_required
def company_detail(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    trips = Trip.objects.filter(company=company, paid=False)

    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        driver_name = request.POST.get('driver_name')

        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

            trips = trips.filter(date__gte=from_date, date__lte=to_date)
        
        if driver_name:
            trips = trips.filter(driver__icontains=driver_name)

    context = {
        'company': company,
        'trips': trips,
    }
    return render(request, 'company_detail.html', context)


@login_required
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    company_id = trip.company.id
    trip.delete()
    return redirect('company_detail', company_id=company_id)

@login_required
def update_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    company = trip.company  # Get the company related to this trip

    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            old_amount = trip.amount  # Store old amount for updating total_unpaid_amount
            form.save()

            # Calculate the difference in amount
            new_amount = trip.amount
            amount_difference = new_amount - old_amount

            # Update total_unpaid_amount in Company model
            company.unpaid_amount += amount_difference
            company.save()

            # Redirect to company detail page or any appropriate URL after successful update
            return redirect('company_detail', company_id=trip.company.id)
    else:
        form = TripForm(instance=trip)

    context = {
        'form': form,
        'trip': trip,
    }
    return render(request, 'update_trip.html', context)



def index(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']
            freight = form.cleaned_data['freight']
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            note = form.cleaned_data['note']

            # Construct the email message
            subject = 'New Quote Request'
            message = "Hello"
            html_content = render_to_string('email.html', {
                'name': name,
                'email': email,
                'mobile': mobile,
                'freight': freight,
                'origin': origin,
                'destination': destination,
                'note': note,
            })
            recipient_list = ["aak5471@gmail.com"]
            from_email = "MS_fjvWs4@trial-pxkjn41pyw94z781.mlsender.net"  # Replace with your email address

            try:
                with get_connection(
                        host=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        use_tls=True,
                ) as connection:
                    email_message = EmailMultiAlternatives(
                        subject=subject,
                        body=message,
                        to=recipient_list,
                        from_email=from_email,
                        connection=connection
                    )
                    email_message.attach_alternative(html_content, "text/html")
                    email_message.send(fail_silently=False)
                return redirect('service')
            except Exception as e:
                form.add_error(None, f'Error sending email: {e}')
                print("Error:", e)
    else:
        form = QuoteRequestForm()

    return render(request, 'index.html', {'form': form, 'user': request.user})

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Construct the email message
        email_subject = 'New Contact Form Submission'
        email_message = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nPhone: {phone}\nMessage: {message}"
        html_content = render_to_string('email_template.html', {
            'name': name,
            'email': email,
            'subject': subject,
            'phone': phone,
            'message': message,
        })
        recipient_list = ["aak5471@gmail.com"]
        from_email = "MS_fjvWs4@trial-pxkjn41pyw94z781.mlsender.net"  # Ensure this is set in your settings

        try:
            with get_connection(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=True,
            ) as connection:
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=email_message,
                    to=recipient_list,
                    from_email=from_email,
                    connection=connection
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
            return render(request, 'contact.html', {'success': True})
        except Exception as e:
            return render(request, 'contact.html', {'error': str(e)})

    return render(request, 'contact.html')

def service(request):
    return render(request, 'service.html')

def feature(request):
    return render(request, 'feature.html')

def quote(request):
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']
            freight = form.cleaned_data['freight']
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            note = form.cleaned_data['note']

            # Construct the email message
            subject = 'New Quote Request'
            message = "Hello"
            html_content = render_to_string('email.html', {
                'name': name,
                'email': email,
                'mobile': mobile,
                'freight': freight,
                'origin': origin,
                'destination': destination,
                'note': note,
            })
            recipient_list = ["aak5471@gmail.com"]
            from_email = "MS_fjvWs4@trial-pxkjn41pyw94z781.mlsender.net"  # Replace with your email address

            try:
                with get_connection(
                        host=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        use_tls=True,
                ) as connection:
                    email_message = EmailMultiAlternatives(
                        subject=subject,
                        body=message,
                        to=recipient_list,
                        from_email=from_email,
                        connection=connection
                    )
                    email_message.attach_alternative(html_content, "text/html")
                    email_message.send(fail_silently=False)
                return redirect('service')
            except Exception as e:
                form.add_error(None, f'Error sending email: {e}')
                print("Error:", e)
    else:
        form = QuoteRequestForm()

    return render(request, 'quote.html', {'form':form})

def error_404(request):
    return render(request, '404.html')

def paid_companies(request):
    companies = Company.objects.annotate(total_paid_amount=Sum('trip__amount', filter=Q(trip__paid=True)))
    total_paid_amount = companies.aggregate(Sum('total_paid_amount'))['total_paid_amount__sum']
    total_unpaid_amount = companies.aggregate(Sum('unpaid_amount'))['unpaid_amount__sum']

    context = {
        'companies': companies,
        'total_paid_amount': total_paid_amount,
        'total_unpaid_amount': total_unpaid_amount,
    }
    return render(request, 'paid_companies.html', context)

def unpaid_companies(request):
    companies = Company.objects.annotate(total_unpaid_amount=Sum('trip__amount', filter=Q(trip__paid=False)))
    total_paid_amount = companies.aggregate(Sum('paid_amount'))['paid_amount__sum']
    total_unpaid_amount = companies.aggregate(Sum('unpaid_amount'))['unpaid_amount__sum']

    context = {
        'companies': companies,
        'total_paid_amount': total_paid_amount,
        'total_unpaid_amount': total_unpaid_amount,

    }
    return render(request, 'unpaid_companies.html', context)
