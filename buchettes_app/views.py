# coding: utf-8
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Buchette
from .forms import BuchetteForm, UserCreationFormEmail, DefenceForm
from .expressions import s_ListeExpressions
from django.core.mail import send_mail
import random



def home(request):
    # On associe dans un dictionnaire chaque user a une liste de buchette
    l_dictionnaire_user_buchette = {}
    # Contient la meme information que le dictionnaire user buchette mais seuleument les buchette
    # dont le status vaut A
    l_dictionnaire_user_buchette_A = {}
    # Si c'est un membre du comité, liste a valider / refuser
    l_liste_buchette_a_valider = []
    l_liste_buchette_attente = []
    #Identifie si on a un membre du comite
    l_comite_user = False
    # Nombre de buchette qu'a l'utilisateur courant
    l_buchette_current_user = 0
    # Dictionnaire contenant en clé les utilisateur ayant des buchettes payées a confirmer et en value
    # les buchettes payées a confirmées de l'utilisateur.
    # Les buchettes payées à confirmer de l'utilisateru courant sont exclues
    l_dict_user_buchette_payee_confirmation = {}
    # Contient les utilisateur triés dans l'ordre de nombre de buchettes
    l_list_user_tries = []
    # Contient la liste des buchettes a defendre
    l_liste_user_a_defendre = []
    # Contient un dico dont la clé est les users et la valeur la medaille du plus de buchette
    l_dictionnaire_user_buchette_sans_R = {}
    l_dico_user_medaille = {}
    # Contient une expression aléatoire
    l_expression = ""

    # On verifie sur  l'ensemble des buchettes si certaines d'entre elles ne sont plus défendable (timeout)
    Buchette.objects.update_buchette_temps_restant()

    # Dictionnaire temporaire contenant les buchettes a payer pour les users


    for l_user in User.objects.all():
        l_dictionnaire_user_buchette[l_user] = Buchette.objects.buchettes_for_user(l_user)
        l_dictionnaire_user_buchette_A[l_user] = Buchette.objects.buchette_a_payer_for_user(l_user)
        l_dictionnaire_user_buchette_sans_R[l_user] = Buchette.objects.buchette_totale_sans_R_for_user(l_user)
    # Afin d'afficher les utlisaterus par nombres de buchettes décroissants,
    # On créé une liste contenant les user triés dans l'ordre
    # En effet, les dictionnaires ne conserve pas l'ordre
    for l_user_sort in sorted(l_dictionnaire_user_buchette_A,
                         key=lambda l_user_sort: l_dictionnaire_user_buchette_A[l_user_sort].count(), reverse=True):
        l_list_user_tries.append(l_user_sort)

    # Attribution des medailles aux 3 champions
    for i, l_user_sort in enumerate(sorted(l_dictionnaire_user_buchette_sans_R,
                         key=lambda l_user_sort: l_dictionnaire_user_buchette_sans_R[l_user_sort].count(),
                         reverse=True)):
        if l_dictionnaire_user_buchette_sans_R[l_user_sort].count() != 0:
            l_dico_user_medaille[l_user_sort] = i
        else:
            l_dico_user_medaille[l_user_sort] = 99

    # Attibution de l'expression aléatoire
    l_rand = random.randrange(0, len(s_ListeExpressions), 1)
    l_expression = s_ListeExpressions[l_rand]

    # Code activé que si l'utilisateur est identifié
    if request.user.is_authenticated:
        # On identifie le nombre de buchettes qu'a l'utilisateur courant
        l_buchette_current_user = Buchette.objects.buchette_a_payer_for_user(request.user).count()

        # On identifie ici les buchettes pourlesquelles l'utilisateur counrant doit se défendre
        l_liste_user_a_defendre = Buchette.objects.buchette_a_defendre_for_user(request.user)

        # On identifie ici les buchettes qui ont été payées et qui doivent être validées
        # On ne prend que les buchette p et v qui ne sont pas celles de l'utilisateur courant
        l_buchette_payee_confirmation = Buchette.objects.buchette_payees_a_confirmer_exclude_user(request.user)
        # On reparcours les user pour créer le dict user confimation payée
        for l_user in User.objects.all():
            # On incrémente le dict que s'i y a des buchettes payées a confirmer
            if l_buchette_payee_confirmation.buchettes_for_user(l_user).count() > 0:
                l_dict_user_buchette_payee_confirmation[l_user] = \
                    l_buchette_payee_confirmation.buchettes_for_user(l_user)
        # Code en charge de determiner si l'utilisateur courant fait parti du comite des buchettes
        l_comite_user = True if len(request.user.groups.filter(name='Comite')) == 1 else False

        # Liste des buchettes a valider par le comite si le user en est membre
        if l_comite_user:
            l_liste_buchette_comite = Buchette.objects.buchettes_a_valider()
            l_liste_buchette_a_valider = []
            l_liste_buchette_attente = []
            # Pour chaque buchette dans le comité on regarde si le user a voté
            for l_buchette in l_liste_buchette_comite:
                if len(l_buchette.comite_a_voter.filter(username=request.user.username)) == 0:
                    l_liste_buchette_a_valider.append(l_buchette)
                else:
                    l_liste_buchette_attente.append(l_buchette)

    return render(request, 'buchettes_app/home.html',
                  {
                      'list_user_tries': l_list_user_tries,
                      'dictionnaire_user_buchette': l_dictionnaire_user_buchette,
                      'dictionnaire_user_buchette_A': l_dictionnaire_user_buchette_A,
                      'is_comite_buchette': l_comite_user,
                      'list_buchette_a_valider': l_liste_buchette_a_valider,
                      'list_buchette_attente': l_liste_buchette_attente,
                      'nombre_buchette_utilisateur_courant' : l_buchette_current_user,
                      'dico_user_buchettes_payees_a_confirmer' : l_dict_user_buchette_payee_confirmation,
                      'liste_user_a_defendre': l_liste_user_a_defendre,
                      'dico_user_medaille': l_dico_user_medaille,
                      'expression': l_expression
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
            # On informe l'utilisateur qu'il s'est pris une buchette et qu'il doit se défendre
            l_string_email = "Bonjour "+l_buchette.victime.username+",\n\n"\
                "J'ai le regret de vous annoncer que vous venez de vous prendre une buchette " +\
                "pour le motif suivant : \n\n " + l_buchette.message_buchette + "\n\n" + \
                "Vous avez 48h pour vous défendre, rendez vous sur http://renseignerAuDeploiement/"

            send_mail(
                '[ Buchette Factory ] Nouvelle Buchette',
                l_string_email,
                'Deploiement@soprasteria.com',
                [l_buchette.victime.email],
                fail_silently=True,
                )
            return redirect("player_home")
    else:
        # L'utilisateur demande un nouveau FORM vierge, on lui affiche
        form = BuchetteForm()

    return render(request, "buchettes_app/new_buchette_form.html", {'form': form})

@login_required
def accept_buchette(request, id):

    # On revérifie que l'utilisateur est membre du comité
    l_comite_user = True if len(request.user.groups.filter(name='Comite')) == 1 else False

    l_utilisateur_autorise = False
    l_message_erreur = ""

    if l_comite_user:
        # Méthode en charge d'accepter une buchette.
        buchette_a_valider = get_object_or_404(Buchette, pk=id)

        l_utilisateur_autorise = True
        buchette_a_valider.vote_pour += 1
        buchette_a_valider.comite_a_voter.add(request.user)
        if buchette_a_valider.nom_membre_comite == "":
            buchette_a_valider.nom_membre_comite += request.user.username
        else:
            buchette_a_valider.nom_membre_comite += ", " + request.user.username
        buchette_a_valider.save()
        vote_comite(buchette_a_valider)

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


@login_required
def deny_buchette(request, id):
    # On revérifie que l'utilisateur est membre du comité
    l_comite_user = True if len(request.user.groups.filter(name='Comite')) == 1 else False

    l_utilisateur_autorise = False
    l_message_erreur = ""

    if l_comite_user:
        # Méthode en charge d'accepter une buchette.
        buchette_a_valider = get_object_or_404(Buchette, pk=id)

        buchette_a_valider.vote_contre += 1
        buchette_a_valider.comite_a_voter.add(request.user)
        buchette_a_valider.save()
        vote_comite(buchette_a_valider)
        l_utilisateur_autorise = True

    else:
        l_utilisateur_autorise = False
        l_message_erreur = 'Il faut être menmbre du comité pour refuser une buchette'

    if l_utilisateur_autorise:
        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse(l_message_erreur, status=401)

@login_required
def confirmation_buchette_soldees(request, user_id):
    # On verifie que le user en train de confirmer n'est pas celui qui a payé ses buchettes
    if request.user.id != user_id:
        # On identifie les buchettes concernees par le paiement grace au user id
        # On commence par retrouver notre user
        l_user_concerne = get_object_or_404(User, pk=user_id)
        # On établit ensuite la liste des buchettes a confirmer pour ce user
        l_buchette_a_confirmer = Buchette.objects.buchette_payees_a_confirmer_for_user(l_user_concerne)
        print(l_buchette_a_confirmer.count())
        # On vient confirmer les 3 ou - buchettes les plus anciennes
        # On trouve les 3 buchettes les plus anciennes dans la liste
        l_buchette_sorted = l_buchette_a_confirmer.order_by('date_buchette')
        # On détermine le nombre à confirmer (3 ou moins)
        l_nombre_a_confirmer = 3 if l_buchette_sorted.count() >= 3 else l_buchette_sorted.count()
        # On prend les 3 premières buchettes qui sont les plus anciennes et on change leur status
        for i in range(l_nombre_a_confirmer):
            # Si le status était P on passe à V car 1a valisation a été faite
            # Si c'était V on passe à S
            if list(l_buchette_sorted)[i].status_buchette == 'P':
                list(l_buchette_sorted)[i].status_buchette = 'S'
            l_buchette_sorted[i].save()
        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse("Impossible de confirmer vos propres buchettes !", status=401)

@login_required
def buchette_non_payee(request, user_id):
    # On verifie que le user en train de confirmer n'est pas celui qui a payé ses buchettes
    if request.user.id != user_id:
        # On identifie les buchettes concernees par le paiement grace au user id
        # On commence par retrouver notre user
        l_user_concerne = get_object_or_404(User, pk=user_id)
        # On établit ensuite la liste des buchettes a confirmer pour ce user
        l_buchette_a_confirmer = Buchette.objects.buchette_payees_a_confirmer_for_user(l_user_concerne)
        print(l_buchette_a_confirmer.count())
        # On vient confirmer les 3 ou - buchettes les plus anciennes
        # On trouve les 3 buchettes les plus anciennes dans la liste
        l_buchette_sorted = l_buchette_a_confirmer.order_by('date_buchette')
        # On détermine le nombre à confirmer (3 ou moins)
        l_nombre_a_confirmer = 3 if l_buchette_sorted.count() >= 3 else l_buchette_sorted.count()
        # On prend les 3 premières buchettes qui sont les plus anciennes et on change leur status
        for i in range(l_nombre_a_confirmer):
            # On repasse le status des 3 buchettes a non payées
            list(l_buchette_sorted)[i].status_buchette = 'A'
            l_buchette_sorted[i].save()
        # Redirige ensuite vers le home
        return redirect("player_home")
    else:
        return HttpResponse("Impossible de confirmer vos propres buchettes !", status=401)


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

@login_required
def defence(request, id):
    # Méthode en charge d'e generer le form pour la défence d'une buchette.
    buchette_a_defendre = get_object_or_404(Buchette, pk=id)
    #On stocke le message de la buchette
    message_buchette = buchette_a_defendre.message_buchette

    # On verifie que l'utilisateru courant est bien celui touché par la buchette
    if buchette_a_defendre.victime != request.user:
        return HttpResponse("Impossible de défendre les buchettes des autres !", status=401)
    # On verifie que la buchette soit bien en état defence attendue
    if buchette_a_defendre.status_buchette != 'D':
        return HttpResponse("Cette buchette n'est plus défendable !", status=401)

    if request.method == "POST":
        #  On vérifie si la data est valide en lui donnant un model prérempli avec l'utilisa
        # teur courant
        form = DefenceForm(instance=buchette_a_defendre, data=request.POST)
        # Cette méthode est tres importante et doit etre applée systématiquement
        #  Si c'est valide on repart sur le home, sinon le form non validé est renvoyé
        # a l'utilisateur
        if form.is_valid():
            #  On enregistre en data base
            buchette_a_defendre.status_buchette = 'E'
            #Vérification que l'utilisateur n'a pas modifié le champs message en passant par le HTML
            # Si c'est le cas, buchette auto !
            if(buchette_a_defendre.message_buchette != buchette_a_defendre):
                buchette_a_defendre.message_buchette = message_buchette
                # L'utilisateur est sanctionné d'une buchette
                new_buchette = Buchette(status_buchette='A')
                new_buchette.victime = request.user
                new_buchette.message_buchette = "Buchette Factory : Cet utilisateur a tenté de tricher en modifiant" \
                                                " le message de sa buchette lors de l'écriture de la défense ! Une " \
                                                "buchette lui a été attribué automatiquement !"
                new_buchette.message_defense = "Pas de défense possible pour les tricheurs !"
                new_buchette.save()

            form.save()
            return redirect("player_home")
    else:
        # L'utilisateur demande un nouveau FORM vierge, on lui affiche
        form = DefenceForm(instance=buchette_a_defendre)

    return render(request, "buchettes_app/defence_form.html",
                  {
                      'form': form,
                      'buchette_a_defendre' : buchette_a_defendre,
                  })


@login_required
def indefendable(request, id):
    # Méthode en charge de preremplir le champs défense
    buchette_a_defendre = get_object_or_404(Buchette, pk=id)

    #  On verifie que l'utilisateru courant est bien celui touché par la buchette
    if buchette_a_defendre.victime != request.user:
        return HttpResponse("Impossible de défendre les buchettes des autres !", status=401)
    #  On verifie que la buchette soit bien en état defence attendue
    if buchette_a_defendre.status_buchette != 'D':
        return HttpResponse("Cette buchette n'est plus défendable !", status=401)

    buchette_a_defendre.message_defense = 'J\'accepte mon sort, je suis indéfendable !'
    buchette_a_defendre.status_buchette = 'E'
    buchette_a_defendre.save()

    return redirect("player_home")


@login_required
def liste_buchettes(request, user_id):
    # On commence par retrouver notre user
    l_user_concerne = get_object_or_404(User, pk=user_id)
    # Liste de toutes les buchettes classées de la puls récente à la plus vieille
    l_liste_buchette = Buchette.objects.buchettes_for_user(l_user_concerne)
    l_buchette_sorted = l_liste_buchette.order_by('date_buchette')
    l_buchette_sorted = l_buchette_sorted.reverse()
    return render(request, "buchettes_app/liste_buchettes.html",
                  {
                      'user': l_user_concerne,
                      'liste_buchette': l_buchette_sorted,
                  })


def vote_comite(buchette):
        # On vient vérifier que tous les membres du comité ont votés
        if (buchette.vote_pour +  buchette.vote_contre) >= len(User.objects.filter(groups__name='Comite')):
            # On vérifie si il y eu plus de vote pour
            if(buchette.vote_pour >= buchette.vote_contre):
                # Si c'est la cas on valide la buchette, sinon on la rejette
                buchette.status_buchette = 'A'
                buchette.save()
            else:
                buchette.status_buchette = 'R'
                buchette.save()
