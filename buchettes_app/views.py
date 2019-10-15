from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Buchette
from .forms import BuchetteForm

def home(request):
    # On associe dans un dictionnaire chaque user a une liste de buchette
    l_dictionnaire_user_buchette = {}
    for l_user in User.objects.all():
        l_dictionnaire_user_buchette[l_user] = Buchette.objects.buchettes_for_user(l_user)

    # Code en charge de determiner si l'utilisateur courant fait parti du comite des buchettes
    l_comite_super = True if len(request.user.get_group_permissions()) > 27 else False

    return render(request, 'buchettes_app/home.html',
                  {
                      'dico_user_buchettes': l_dictionnaire_user_buchette,
                      'is_comite_buchette': l_comite_super,
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

