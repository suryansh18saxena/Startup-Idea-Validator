from django.shortcuts import render,redirect
from .models import Ideas,Connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .api_service import get_swot_analysis, generate_prd_content, check_idea_similarity, edit_prd_with_ai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Avg
import hashlib
from django.shortcuts import render, redirect
from .models import Ideas
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn
from dotenv import load_dotenv
import os


load_dotenv()  
# Algorand Testnet setup (Free node provided by AlgoNode)
algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient("", algod_address)

# Apna Address aur 25-word mnemonic yahan daalein
MY_ADDRESS = os.getenv("MY_ADDRESS")  
PASSPHRASE = os.getenv("PASSPHRASE")

# Mnemonic se Private Key automatically nikal lenge
MY_PRIVATE_KEY = mnemonic.to_private_key(PASSPHRASE)




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

        # ================= AI Similarity Check (BEFORE saving) =================
        # Gather existing ideas from DB for internal comparison
        existing_ideas = Ideas.objects.filter(user=request.user).values_list('problem_statement', flat=True)[:10]
        existing_ideas_text = "\n".join([f"- {idea}" for idea in existing_ideas]) if existing_ideas else ""
        
        similarity_result = check_idea_similarity(problem, solution, market, existing_ideas_text)
        
        # Store form data and similarity result in session for the results page
        request.session['pending_idea'] = {
            'problem': problem,
            'solution': solution,
            'market': market,
            'unique_value': unique_value,
            'revenue_model': revenue_model,
            'competitors': competitors,
        }
        request.session['similarity_result'] = similarity_result
        
        return redirect('similarity_result')

    return render(request, "dashboard/user/ideauplode.html")


# =========================== Similarity Result Page ===========================

@login_required
def similarity_result_view(request):
    similarity_result = request.session.get('similarity_result', None)
    pending_idea = request.session.get('pending_idea', None)

    if not similarity_result or not pending_idea:
        messages.error(request, "No analysis data found. Please submit your idea first.")
        return redirect('create_idea')

    parameters = {
        'similarity': similarity_result,
        'idea_data': pending_idea,
    }
    return render(request, 'dashboard/user/similarity_result.html', parameters)


# =========================== Confirm & Save Idea ===========================

@login_required
def confirm_idea(request):
    pending_idea = request.session.get('pending_idea', None)
    if not pending_idea:
        messages.error(request, "No pending idea found.")
        return redirect('create_idea')

    problem = pending_idea['problem']
    solution = pending_idea['solution']
    market = pending_idea['market']
    unique_value = pending_idea['unique_value']
    revenue_model = pending_idea['revenue_model']
    competitors = pending_idea['competitors']

    idea = Ideas(
        problem_statement=problem,
        solution=solution,
        market=market,
        unique_value=unique_value,
        revenue_model=revenue_model,
        known_competitors=competitors
    )
    idea.user = request.user

    # ================= Blockchain Integration =================
    try:
        idea_text = f"{problem}{solution}{unique_value}"
        idea_hash = hashlib.sha256(idea_text.encode('utf-8')).hexdigest()
        params = algod_client.suggested_params()
        note_data = f"Idea Hash: {idea_hash}".encode()
        unsigned_txn = PaymentTxn(
            sender=MY_ADDRESS, sp=params, receiver=MY_ADDRESS, amt=0, note=note_data
        )
        signed_txn = unsigned_txn.sign(MY_PRIVATE_KEY)
        tx_id = algod_client.send_transaction(signed_txn)
        idea.idea_hash = idea_hash
        idea.blockchain_tx_hash = tx_id
        print(f"Success! Idea hashed on Algorand Testnet. TX ID: {tx_id}")
    except Exception as e:
        print(f"Blockchain hashing failed: {e}")
        messages.warning(request, "Idea saved, but blockchain timestamping failed.")
    # ==========================================================

    idea.save()

    result = get_swot_analysis(idea)

    try:
        import re
        def safe_int(val):
            try:
                return int(val)
            except (ValueError, TypeError):
                if isinstance(val, str):
                    match = re.search(r'\d+', val)
                    if match:
                        return int(match.group())
                return 0

        if isinstance(result, list):
            idea.strengths = str(result[0]) if len(result) > 0 else "N/A"
            idea.weaknesses = str(result[1]) if len(result) > 1 else "N/A"
            idea.opportunities = str(result[2]) if len(result) > 2 else "N/A"
            idea.threats = str(result[3]) if len(result) > 3 else "N/A"
            idea.score_strengths = safe_int(result[4]) if len(result) > 4 else 0
            idea.score_weaknesses = safe_int(result[5]) if len(result) > 5 else 0
            idea.score_opportunities = safe_int(result[6]) if len(result) > 6 else 0
            idea.score_threats = safe_int(result[7]) if len(result) > 7 else 0
            idea.score = safe_int(result[8]) if len(result) > 8 else 0
        elif isinstance(result, dict):
            idea.strengths = str(result.get("strengths", "N/A"))
            idea.weaknesses = str(result.get("weaknesses", "N/A"))
            idea.opportunities = str(result.get("opportunities", "N/A"))
            idea.threats = str(result.get("threats", "N/A"))
            idea.score_strengths = safe_int(result.get("score_strengths", 0))
            idea.score_weaknesses = safe_int(result.get("score_weaknesses", 0))
            idea.score_opportunities = safe_int(result.get("score_opportunities", 0))
            idea.score_threats = safe_int(result.get("score_threats", 0))
            idea.score = safe_int(result.get("score", 0))
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error parsing SWOT result: {e}")
        idea.strengths = "Analysis could not be completed."
        idea.weaknesses = "Analysis could not be completed."
        idea.opportunities = "Analysis could not be completed."
        idea.threats = "Analysis could not be completed."
        idea.score_strengths = 0
        idea.score_weaknesses = 0
        idea.score_opportunities = 0
        idea.score_threats = 0
        idea.score = 0

    idea.save()

    # Clear session data
    request.session.pop('pending_idea', None)
    request.session.pop('similarity_result', None)

    messages.success(request, "Your idea has been successfully uploaded, verified, and analyzed.")
    return redirect("analyze_idea", idea_id=idea.id)


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


# ===================================Generate PRD====================================
@login_required
def generate_prd_view(request, idea_id):
    idea = Ideas.objects.get(id=idea_id, user=request.user)
    regenerate = request.GET.get('regenerate', False)

    # Agar PRD pehle se DB mein hai aur regenerate nahi maanga, toh wahi use karo
    if idea.prd_content and not regenerate:
        prd_content = idea.prd_content
    else:
        # API call sirf tab hogi jab pehli baar ho ya regenerate maanga ho
        prd_content = generate_prd_content(idea)
        idea.prd_content = prd_content
        idea.save()

    parameters = {
        "idea": idea,
        "prd_content": prd_content,
    }
    return render(request, "dashboard/user/prd_report.html", parameters)


# ===================================User Profile====================================
@login_required
def profile(request):
    user = request.user
    parameters = {
        "user": user
    }
    return render(request, "dashboard/user/profile.html", parameters)



# ===================================Manage PRDs====================================
@login_required
def my_prds_view(request):
    # Fetch all ideas that belong to the user and actually have PRD content
    prds = Ideas.objects.filter(user=request.user).exclude(prd_content__isnull=True).exclude(prd_content__exact='')
    parameters = {
        "prds": prds
    }
    return render(request, "dashboard/user/my_prds.html", parameters)


@login_required
def edit_prd_view(request, idea_id):
    idea = Ideas.objects.get(id=idea_id, user=request.user)

    if request.method == "POST":
        new_content = request.POST.get("prd_content")
        if new_content:
            idea.prd_content = new_content
            idea.save()
            messages.success(request, "PRD updated successfully!")
            return redirect('generate_prd', idea_id=idea.id)

    parameters = {
        "idea": idea
    }
    return render(request, "dashboard/user/edit_prd.html", parameters)


# ===================================AI Edit PRD (AJAX)====================================
@login_required
@require_POST
def ai_edit_prd(request, idea_id):
    """AJAX endpoint: AI applies user-requested changes to the PRD."""
    try:
        idea = Ideas.objects.get(id=idea_id, user=request.user)
    except Ideas.DoesNotExist:
        return JsonResponse({"success": False, "error": "Idea not found or access denied."}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON payload."}, status=400)

    instruction = data.get("instruction", "").strip()
    current_content = data.get("current_content", "").strip()

    if not instruction:
        return JsonResponse({"success": False, "error": "Please provide an instruction."}, status=400)

    if not current_content:
        current_content = idea.prd_content or ""

    result = edit_prd_with_ai(current_content, instruction)

    if result["success"]:
        # Save the updated PRD to the database
        idea.prd_content = result["updated_content"]
        idea.save()
        return JsonResponse({"success": True, "updated_content": result["updated_content"]})
    else:
        return JsonResponse({"success": False, "error": result.get("error", "AI processing failed.")}, status=500)
