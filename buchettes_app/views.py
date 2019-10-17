from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Buchette
from .forms import BuchetteForm, UserCreationFormEmail

from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView


def home(request):
    # On associe dans un dictionnaire chaque user a une liste de buchette
    l_dictionnaire_user_buchette = {}
    # Si c'est un membre du comité, liste a valider / refuser
    l_liste_buchette_a_valider = []
    #Identifie si on a un membre du comite
    l_comite_user = False
    # Nombre de buchette qu'a l'utilisateur courant
    l_buchette_current_user = 0

    for l_user in User.objects.all():
        l_dictionnaire_user_buchette[l_user] = Buchette.objects.buchettes_for_user(l_user)

    # Code activé que si l'utilisateur est identifié
    if request.user.is_authenticated:
        # On identifie le nombre de buchettes qu'a l'utilisateur courant
        l_buchette_current_user = Buchette.objects.buchette_a_payer_for_user(request.user).count()

        # Code en charge de determiner si l'utilisateur courant fait parti du comite des buchettes
        l_comite_user = True if len(request.user.get_group_permissions()) > 27 else False

        # Liste des buchettes a valider par le comite si le user en est membre
        if l_comite_user:
            l_liste_buchette_a_valider = Buchette.objects.buchettes_a_valider()

        # Si l'utilisateur est identifié et qu'un id est en paramètre de la requete et que l'utilisateur est autorisé
        # à valider des buchettes, on change l'état de la buchette

    return render(request, 'buchettes_app/home.html',
                  {
                      'dico_user_buchettes': l_dictionnaire_user_buchette,
                      'is_comite_buchette': l_comite_user,
                      'list_buchette_a_valider': l_liste_buchette_a_valider,
                      'nombre_buchette_utilisateur_courant' : l_buchette_current_user,
                  })


@login_required
def new_buchette(request):
    if request.method == "POST":
        l_buchette = Buchette(status_buchette='D')
        #  On vérifie si la data est valide en lui donnant un model prérempli avec l'utilisa
        # teur courant
        form = BuchetteForm(instance=l_buchette, data=request.POST)
        # Cette méthode est tres importante et doit etre applée systématiquement
        #  Si c'est valide on repart sur le home, sinon le form non validé est renvoyé
        # a l'utilisateur
        if form.is_valid():
            #  On enregistre en data base
            form.save()
            return redirect("player_home")
    else:
        # L'utilisateur demande un nouveau FORM vierge, on lui affiche
        form = BuchetteForm()
    return render(request, "buchettes_app/new_buchette_form.html", {'form': form})

@login_required
def accept_buchette(request, id):

    # On revérifie que l'utilisateur est membre du comité
    l_comite_user = True if len(request.user.get_group_permissions()) > 27 else False

    l_utilisateur_autorise = False
    l_message_erreur = ""

    if l_comite_user:
        # Méthode en charge d'accepter une buchette.
        buchette_a_valider = get_object_or_404(Buchette, pk=id)

        # On verifie que la bucette ne soit pas attribuée au membre en train de faire la vérification
        if buchette_a_valider.victime == request.user:
            l_message_erreur ='Impossible de valider sa propre buchette'
            l_utilisateur_autorise = False
        else:
            l_utilisateur_autorise = True
            buchette_a_valider.status_buchette = 'A'
            buchette_a_valider.save()
    else:
        l_utilisateur_autorise = False
        l_message_erreur = 'Il faut être menmbre du comité pour valider une buchette'

    if l_utilisateur_autorise:
        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse(l_message_erreur, status=401)

@login_required
def buchette_payees(request):
    # L'utilisateur veut payer ses buchettes
    # Liste des buchettes associées
    l_liste_buchette_user = Buchette.objects.buchette_a_payer_for_user(request.user)
    # On commence par verifier s'il en a plus de 3
    if len(l_liste_buchette_user) >= 3:
        # On trouve les 3 buchettes les plus anciennes dans la liste
        l_buchette_sorted = l_liste_buchette_user.order_by('date_buchette')
        # On prend les 3 premières buchettes qui sont les plus anciennes et on change leur status
        for i in range(3):
            list(l_buchette_sorted)[i].status_buchette = 'P'
            l_buchette_sorted[i].save()

        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse("Il faut avoir au moins 3 buchettes pour les payer !", status=401)


    # On revérifie que l'utilisateur est membre du comité
    l_comite_user = True if len(request.user.get_group_permissions()) > 27 else False


@login_required
def deny_buchette(request, id):
    # On revérifie que l'utilisateur est membre du comité
    l_comite_user = True if len(request.user.get_group_permissions()) > 27 else False

    l_utilisateur_autorise = False
    l_message_erreur = ""

    if l_comite_user:
        # Méthode en charge d'accepter une buchette.
        buchette_a_valider = get_object_or_404(Buchette, pk=id)

        # On verifie que la bucette ne soit pas attribuée au membre en train de faire la vérification
        if buchette_a_valider.victime == request.user:
            l_message_erreur = 'Impossible de refuser sa propre buchette'
            l_utilisateur_autorise = False
        else:
            l_utilisateur_autorise = True
            buchette_a_valider.status_buchette = 'R'
            buchette_a_valider.save()
    else:
        l_utilisateur_autorise = False
        l_message_erreur = 'Il faut être menmbre du comité pour refuser une buchette'

    if l_utilisateur_autorise:
        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse(l_message_erreur, status=401)


def singup_view(request):
    """
    Méthode permettant de créer une vue de création d'un nouvel utilisateur
    """
    l_form = None
    if request.method == 'POST':
        l_form = UserCreationFormEmail(request.POST)
        if l_form.is_valid():
            l_form.save()
            print("Form save")
            return redirect("player_login")
    else:
        l_form = UserCreationFormEmail()

    return render(request, "buchettes_app/signup_form.html", {'form': l_form})
