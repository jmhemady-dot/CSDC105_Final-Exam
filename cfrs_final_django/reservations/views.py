from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
from .models import Facility
from .forms import FacilityForm
from .models import Reservation, Facility
from django.db.models import Q
from datetime import datetime


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'auth/login.html')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def facility_list(request):

    facilities = Facility.objects.all()

    return render(request,
                  'facilities/facility_list.html',
                  {'facilities': facilities})


def add_facility(request):

    if request.method == 'POST':

        facility_name = request.POST.get('facility_name')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')

        Facility.objects.create(
            facility_name=facility_name,
            location=location,
            capacity=capacity
        )

        return JsonResponse({
            'status': 'success'
        })

    return render(
        request,
        'facilities/add_facility.html'
    )

def edit_facility(request, facility_id):
    facility = get_object_or_404(Facility, facility_id = facility_id)

    if request.method == 'POST':
        try:
            facility.name = request.POST.get('facility_name')
            facility.location = request.POST.get('location')
            facility.capacity = request.POST.get('capacity')

            facility.save()

            return JsonResponse({
                'success': True,
                'message': 'Facility updated successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return render(request, 'facilities/edit_facility.html', {'facility': facility})

def delete_facility(request):

    if request.method == 'POST':

        facility_id = request.POST.get('facility_id')

        facility = Facility.objects.get(pk=facility_id)

        facility.delete()

        return JsonResponse({
            'status': 'success',
            'message': "Facility deleted successfully"
        })


def account_list(request):

    users = User.objects.all().select_related('profile')

    return render(request, 'accounts/account_list.html', {
        'users': users
    })

def add_account(request):

    if request.method == "POST":

        try:
            # 1. Create user
            user = User.objects.create(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                username=request.POST['username'],
                password=make_password(request.POST['password'])
            )

            # 2. Create profile
            Profile.objects.create(
                user=user,
                role_id=request.POST['role_id']
            )

            return JsonResponse({
                "status": "success",
                "message": "Account created successfully"
            })

        except Exception as e:

            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return render(request, 'accounts/add_account.html')

def edit_account(request, user_id):

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')

            user.save()

            profile = user.profile
            profile.role_id = request.POST.get('role_id')
            profile.save()

            return JsonResponse({
                "status": "success",
                "message": "Account updated successfully"
            })

        except Exception as e:

            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return render(request, 'accounts/edit_account.html', {
        'user': user
    })

def delete_account(request):

    if request.method == 'POST':

        user_id = request.POST.get('user_id')

        user = User.objects.get(id=user_id)

        user.delete()

        return JsonResponse({
            'status': 'success',
            'message': "User deleted successfully"
        })

def create_reservation_page(request):

    facilities = Facility.objects.all()

    return render(request, 'reservations/create_reservation.html', {
        'facilities': facilities
    })

@login_required
def add_reservation(request):

    if request.method == "POST":

        try:
            facility = get_object_or_404(
                Facility,
                facility_id=request.POST.get('facility_id')
            )

            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            if not all([date, start_time, end_time]):
                return JsonResponse({
                    "status": "error",
                    "message": "Missing required fields"
                }, status=400)

            # Convert to proper time objects (important for reliable comparison)
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()

            if start_time_obj >= end_time_obj:
                return JsonResponse({
                    "status": "error",
                    "message": "Start time must be earlier than end time"
                }, status=400)

            # CONFLICT CHECK
            conflict_exists = Reservation.objects.filter(
                facility=facility,
                date=date,
            ).filter(
                Q(start_time__lt=end_time_obj) &
                Q(end_time__gt=start_time_obj)
            ).exists()

            if conflict_exists:
                return JsonResponse({
                    "status": "error",
                    "message": "This time slot is already booked for this facility"
                }, status=409)

            Reservation.objects.create(
                facility=facility,
                requestor=request.user,
                date=date,
                start_time=start_time_obj,
                end_time=end_time_obj,
                attendees=request.POST.get('attendees'),
                purpose=request.POST.get('purpose'),
                status='pending'
            )

            return JsonResponse({
                "status": "success",
                "message": "Reservation created successfully"
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)

def my_reservations(request):
    reservations = Reservation.objects.filter(requestor=request.user)

    context = {
        "reservations": reservations
    }
    return render(request, "reservations/my_reservations.html", context)

def reservation_list(request):
    reservations = Reservation.objects.all()

    return render(request, "reservations/reservation_list.html", {
        "reservations": reservations
    })

def reservation_events(request):
    reservations = Reservation.objects.select_related('facility', 'requestor').all()

    events = []

    for r in reservations:
        events.append({
            "id": r.reservation_id,
            "title": f"{r.facility.facility_name} - {r.requestor.first_name} {r.requestor.last_name}",
            "start": f"{r.date}T{r.start_time}",
            "end": f"{r.date}T{r.end_time}",

            "backgroundColor": (
                "#198754" if r.status == "approved"
                else "#ffc107" if r.status == "pending"
                else "#dc3545"
            ),

            "borderColor": (
                "#198754" if r.status == "approved"
                else "#ffc107" if r.status == "pending"
                else "#dc3545"
            ),

            "extendedProps": {
                "purpose": r.purpose,
                "attendees": r.attendees,
                "status": r.status,
            }
        })

    return JsonResponse(events, safe=False)

def approve_request(request):
    reservation_id = request.POST.get('reservation_id')

    if request.method == "POST":
        try:
            reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

            reservation.status = "approved"
            reservation.save()

            return JsonResponse({
                "status": "success",
                "message": "Reservation approved successfully"
            })

        except Reservation.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Reservation not found"
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })

def reject_request(request):
    reservation_id = request.POST.get('reservation_id')

    if request.method == "POST":
        try:
            reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

            reservation.status = "rejected"
            reservation.save()

            return JsonResponse({
                "status": "success",
                "message": "Reservation rejected successfully"
            })

        except Reservation.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Reservation not found"
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })


