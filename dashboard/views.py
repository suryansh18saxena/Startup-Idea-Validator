from django.shortcuts import render,redirect
from .models import Ideas,Connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .api_service import get_swot_analysis
from django.db.models import Avg

@login_required
def dashboard(request):
    last_5_ideas = Ideas.objects.filter(user=request.user).order_by('-created_at')[:5]

    user_ideas = Ideas.objects.filter(user=request.user)

    # 2. Total Ideas Count
    ideas_count = user_ideas.count()
    
    # 3. Connections Count (Sirf 'accepted' waale)
    connections_count = Connection.objects.filter(idea__user=request.user, status='accepted').count()
    
    # 4. Average Score Calculate karein
    avg_data = user_ideas.aggregate(avg_score=Avg('score'))
    # Agar koi idea nahi hai, toh score 0 rakhein aur round karein
    average_score = round(avg_data['avg_score'] or 0)

    parameters = {
        "last_5_ideas": last_5_ideas,
        "ideas_count": ideas_count,
        "connections_count": connections_count,
        "average_score": average_score,
    }
    return render(request,"dashboard/user/userdashboard.html", parameters)

# =========================== creating the idea ===========================

@login_required
def create_idea(request):
    if request.method == "POST":
        problem = request.POST.get("problem")
        solution = request.POST.get("solution")
        market = request.POST.get("market")
        unique_value = request.POST.get("usp")
        revenue_model = request.POST.get("revenue")
        competitors = request.POST.get("competitors")

        idea = Ideas(
            problem_statement=problem,
            solution=solution,
            market=market,
            unique_value=unique_value,
            revenue_model=revenue_model,
            known_competitors=competitors
        )
        idea.user = request.user
        idea.save()
        
        result = get_swot_analysis(idea)
        idea.strengths = result[0]
        idea.weaknesses = result[1]
        idea.opportunities = result[2]
        idea.threats = result[3]
        idea.score_strengths = result[4]
        idea.score_weaknesses = result[5]
        idea.score_opportunities = result[6]
        idea.score_threats = result[7]
        idea.score = result[8]
        idea.save()

    


        messages.success(request, "Your idea has been successfully uploaded and analyzed.")
        return redirect("analyze_idea", idea_id=idea.id)

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
        idea.problem_statement = request.POST.get("problem")
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

    parameters = {
        "ideas": Ideas.objects.all()
    }

    return render(request,"dashboard/investor/investor_dashboard.html", parameters)


#=====================================View SWOT Report=====================================

def viewreport(request,idea_id):
        idea = Ideas.objects.get(id=idea_id)
        parameters = {
        "idea": idea,
    }
        return render(request, "dashboard/investor/ViewReport.html", parameters)


# ===================================Request an introduction to an idea====================================

@login_required
def request_introduction(request, idea_id):
    idea = Ideas.objects.get(id=idea_id)

    # Prevent user from connecting with their own idea
    if idea.user == request.user:
        messages.warning(request, "You cannot request an introduction to your own idea.")
        return redirect('investor_dashboard')

    # Create a connection request if one doesn't already exist
    connection, created = Connection.objects.get_or_create(investor=request.user, idea=idea)

    if created:
        messages.success(request, f"Your request for an introduction to '{idea.problem_statement[:30]}...' has been sent.")
    else:
        messages.info(request, f"You have already requested an introduction to this idea. The status is '{connection.status}'.")

    return redirect('investor_dashboard')


# ===================================Handle connection request====================================

@login_required
def handle_connection_request(request, connection_id, action):  # Add 'action' here
    connection = Connection.objects.get(id=connection_id)

    # Security check: Ensure the logged-in user owns the idea
    if connection.idea.user != request.user:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('manage_ideas')

    if action == 'accept':
        connection.status = 'accepted'
        messages.success(request, f"You have accepted the connection request from {connection.investor.username}.")
    elif action == 'reject':
        connection.status = 'rejected'
        messages.info(request, f"You have rejected the connection request from {connection.investor.username}.")
    
    connection.save()
    return redirect('request') # Redirect to the requests page

# ===================================Request page====================================
@login_required
def request(request):
    ideas = Ideas.objects.filter(user=request.user).order_by('-created_at')

    # 1. Pending requests nikalein (jaisa pehle tha)
    pending_requests = Connection.objects.filter(
        idea__user=request.user, 
        status='pending'
    ).order_by('-created_at')

    # 2. Handled (accepted ya rejected) requests bhi nikalein
    handled_requests = Connection.objects.filter(
        idea__user=request.user
    ).exclude(
        status='pending'
    ).order_by('-created_at') # Taaki naye waale upar dikhein

    context = {
        'pending_requests': pending_requests,
        'handled_requests': handled_requests,
    }
    return render(request, 'dashboard/user/request.html', context)

# ===================================Investor's Connections Page====================================
@login_required
def my_connections(request):

    connections = Connection.objects.filter(investor=request.user).order_by('-created_at')

    parameters = {
        'connections': connections
    }
    return render(request, 'dashboard/investor/my_connections.html', parameters)

# ===================================Analyze an idea====================================
@login_required
def analyze_idea(request, idea_id):
    idea = Ideas.objects.get(id=idea_id)
    parameters = {
        "idea": idea,
    }

    return render(request, "dashboard/user/swot_analysis.html", parameters)


# ===================================User Profile====================================
@login_required
def profile(request):
    user = request.user
    parameters = {
        "user": user
    }
    return render(request, "dashboard/user/profile.html", parameters)