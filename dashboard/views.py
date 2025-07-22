from django.shortcuts import render,redirect
from .models import Ideas
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request,"dashboard/user/userdashboard.html")

# =========================== creating the idea ===========================

@login_required
def userdashboard(request):
    if request.method == "POST":
        problem = request.POST.get("problem")
        solution = request.POST.get("solution")
        market = request.POST.get("market")
        unique_value = request.POST.get("usp")
        revenue_model = request.POST.get("revenue")
        competitors = request.POST.get("competitors")

        idea = Ideas(
            problem_statement = problem,
            solution = solution,
            market = market,
            unique_value = unique_value,
            revenue_model = revenue_model,
            known_competitors = competitors
        )
        idea.user = request.user
        idea.save()

        idea = Ideas.objects.all()
        parameters = {
            "ideas": idea
        }
        return render(request,"dashboard/user/userdashboard.html",parameters)

    return render(request,"dashboard/user/ideauplode.html")


# ====================================Displays a list of ideas owned by the logged-in user====================================

@login_required
def manage_ideas(request):
    idea = Ideas.objects.filter(user = request.user).order_by('-created_at')

    parameter = {
        "ideas": idea
    }
    return render(request, "dashboard/user/manage_ideas.html", parameter)


# ====================================edit an idea====================================

@login_required
def edit_ideas(request,idea_id):
    idea = Ideas.objects.get(id = idea_id)

    if request.method == "POST":
        idea.problem_statement = request.POST.get("porblem")
        idea.solution = request.POST.get("solution")
        idea.market = request.POST.get("market")
        idea.unique_value = request.POST.get("usp")
        idea.revenue_model = request.POST.get("revenue")
        idea.known_competitors = request.POST.get("competitors")

        idea.save()
        return redirect("manage_ideas")
    parameters = {
        "ideas" : idea
    }
    return render(request, "dashboard/user/edit_ideas.html", parameters)

# ====================================delete an idea====================================

@login_required
def delete_ideas(request, idea_id):
    idea = Ideas.objects.get(id=idea_id)
    if request.method == "POST":
        idea.delete()
        return redirect("manage_ideas")
    parameters = {
        "ideas": idea
    }
    return render(request, "dashboard/user/manage_ideas.html", parameters)

# ====================================Investor Dashboard====================================

@login_required
def investor_dashboard(request):
    return render(request,"dashboard/investor/investor_dashboard.html")
