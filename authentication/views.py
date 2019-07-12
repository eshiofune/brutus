import time

from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from authentication.models import Person

CLIENT_TRIALS = {}
CLIENTS_BLOCKED = {}

def update_trials(client_ip, email):
    key = str(client_ip) + "_" + email
    trials = CLIENT_TRIALS.get(key, None)

    if trials is not None:
        CLIENT_TRIALS[key] += 1
    else:
        CLIENT_TRIALS[key] = 1

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def authenticate_user(request, email, password):
    try:
        user_from_email = Person.objects.get(email=email)
    except:
        return render(request, "auth/error.html", {
            "msg": "Incorrect email or password"
        }, status=400)

    user = authenticate(username=user_from_email.username, password=password)
    
    if user is not None:
        django_login(request, user)
        return redirect("home")
    else:
        return render(request, "auth/error.html", {
            "msg": "Incorrect email or password"
        }, status=400)

def login(request):
    return render(request, "auth/login.html")

def auth(request):
    if request.method == "POST":
        client_ip = get_client_ip(request)
        email = request.POST.get("email")
        password = request.POST.get("password")
        key = str(client_ip) + "_" + email

        update_trials(client_ip, email)

        if CLIENT_TRIALS[key] > 3:
            time_blocked = CLIENTS_BLOCKED.get(key)

            if time_blocked is not None:
                
                # User has been blocked. Check if it has been up to 5 mins:
                if round(time.time() - CLIENTS_BLOCKED.get(key)) > 300:
                    CLIENTS_BLOCKED.pop(key)
                    CLIENT_TRIALS[key] = 1
                    return authenticate_user(request, email, password)

            # Block client and save time
            else:
                CLIENTS_BLOCKED[key] = time.time()
            
            return render(request, "auth/error.html", {
                "msg": "Maximum trials exceeded"
            }, status=400)

        return authenticate_user(request, email, password)
        
    else:
        return render(request, "auth/error.html", {
            "msg": "Forbidden"
        }, status=403)

@login_required(login_url="/login/")
def home(request):
    return render(request, "auth/home.html")
