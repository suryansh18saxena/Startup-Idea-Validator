from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth,messages
from django.contrib.auth.decorators import login_required
# ========================= Regester new user ===============================

def signup(request):

    if request.method  == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return redirect("signup")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect("signup")

        new_user = User.objects.create_user(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password
        )
        # new_user.set_password(password)  #setting the password for the new user in the encypreted (hashed) formate

        messages.success(request, "Account created successfully!")

        return redirect("login")



    return render(request,"accounts/user/signup.html")

# ====================================== login new user =====================================================

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = auth.authenticate(request, username = username, password = password)

        if user is not None:
            auth.login(request, user) #this is the function for the login

            return redirect("home")
        else:
            messages.error(request,"Invalid username or password.")
            
    return render(request,"accounts/user/login.html")


@login_required
def logout(request):

    auth.logout(request)

    return redirect("home")
