from django.shortcuts import render

from django.http import *

from django.core.urlresolvers import reverse,reverse_lazy


from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView

from braces.views import LoginRequiredMixin # sudo pip install django-braces
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver


from ppal.models import *
from ppal.forms import *

import simplejson as json

import urllib

from django.utils.http import *
from django.db.models import Q

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas

ABC = ['A','B','C','D','E','F','G','H','I','J','K']


def some_view(request, pk):
    # Create the HttpResponse object with the appropriate PDF headers.
    team = Team.objects.get(id=pk)
    player_list = Player.objects.filter(team= team,)

    response = HttpResponse(content_type='application/pdf')
    equipo = "Hoja_de_inscripcion"
    response['Content-Disposition'] = 'attachment; filename="Hoja_de_inscripcion.pdf"'
    ulargo = 841.89/10
    uancho = 595.27/10
    nameOffsetY = 0.07*ulargo

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.

    #team headboards
    p.setFillColorRGB(0,0,0.77)
    p.grid([uancho,9*uancho],[9.5*ulargo,9.25*ulargo])
    p.drawString(2.5*uancho ,9.25*ulargo+nameOffsetY,"II TORNEO INTERCOLEGIOS CIUDAD DE LEGANES")
    p.drawString(3.5*uancho ,9*ulargo+nameOffsetY,"Nombre del equipo")
    p.drawString(7.6*uancho ,9*ulargo+nameOffsetY,"Categoria")
    #teams' name
    xlist = [uancho,7.5*uancho,9*uancho]
    ylist = [9.25*ulargo,9*ulargo, 8.75*ulargo]
    p.drawString(1.1*uancho ,8.75*ulargo+nameOffsetY, to_unicode_or_bust(player_list[0].team.name))
    if player_list[0].team.years == 1:
        categoria = "sub-9"
    else:
        categoria = "sub-12"

    p.drawString(7.6*uancho ,8.75*ulargo+nameOffsetY, categoria)
    # tablerow = tablerow-1*ulargo
    # for object in player_list:
    #     if object.member == 2:
    #         tablerow = tablerow-0.25*ulargo
    #         ylist.append(tablerow)
    #         p.drawString(1.1*uancho ,tablerow+nameOffsetY, to_unicode_or_bust(object.surname1)+" "+to_unicode_or_bust(object.surname2)+", "+to_unicode_or_bust(object.name))
    #         p.drawString(5.1*uancho ,tablerow+nameOffsetY, to_unicode_or_bust(object.birthday))

    p.grid(xlist,ylist)

    #players headboards
    p.setFillColorRGB(0,0,0.77)
    p.grid([uancho,9*uancho],[8.5*ulargo,8.25*ulargo])
    p.drawString(4.5*uancho ,8.25*ulargo+nameOffsetY,"JUGADORAS")
    p.drawString(1.1*uancho ,8*ulargo+nameOffsetY,"Apellidos, Nombre")
    p.drawString(5.1*uancho ,8*ulargo+nameOffsetY,"Fecha de nacimiento")
    #players' names
    xlist = [uancho,5*uancho,9*uancho]
    ylist = [8.25*ulargo,8*ulargo]
    tablerow = 8*ulargo  
    for object in player_list:
        if object.member == 1:
            tablerow = tablerow-0.25*ulargo
            ylist.append(tablerow)
            p.drawString(1.1*uancho ,tablerow+nameOffsetY, to_unicode_or_bust(object.surname1)+" "+to_unicode_or_bust(object.surname2)+", "+to_unicode_or_bust(object.name))
            p.drawString(5.1*uancho ,tablerow+nameOffsetY, str(object.birthday))
    p.grid(xlist,ylist)

    #delegado headboards
    p.grid([uancho,9*uancho],[tablerow-0.5*ulargo,tablerow-0.75*ulargo])
    p.drawString(4.5*uancho ,tablerow-0.75*ulargo+nameOffsetY,"DELEGADO")
    p.drawString(1.1*uancho ,tablerow-1*ulargo+nameOffsetY,"Apellidos, Nombre")
    p.drawString(5.1*uancho ,tablerow-1*ulargo+nameOffsetY,"Fecha de nacimiento")
    #delegado's name
    xlist = [uancho,5*uancho,9*uancho]
    ylist = [tablerow-0.75*ulargo,tablerow-1*ulargo]
    tablerow = tablerow-1*ulargo
    for object in player_list:
        if object.member == 2:
            tablerow = tablerow-0.25*ulargo
            ylist.append(tablerow)
            p.drawString(1.1*uancho ,tablerow+nameOffsetY, to_unicode_or_bust(object.surname1)+" "+to_unicode_or_bust(object.surname2)+", "+to_unicode_or_bust(object.name))
            p.drawString(5.1*uancho ,tablerow+nameOffsetY, str(object.birthday))

    p.grid(xlist,ylist)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

def index(request):
    school_list1 = Team.objects.filter(years=1).order_by('-last_editing_date')[:5]
    school_list2 = Team.objects.filter(years=2).order_by('-last_editing_date')[:5]
    return render(request, 'index.html', {
        'school_list_p': school_list1,
        'school_list_m': school_list2,

    })

def plano_view(request):
    return render(request, 'plano_view.html', {
    })

def index_all(request):
    school_list1 = Team.objects.filter(years=1).order_by('-last_editing_date')
    school_list2 = Team.objects.filter(years=2).order_by('-last_editing_date')
    return render(request, 'index_all.html', {
        'school_list_p': school_list1,
        'school_list_m': school_list2,

    })

def us(request):
    return render(request, 'us.html')

def school_login(request):
    if not request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                dest = request.GET.get('next') if request.GET.get('next') != None else reverse(index)
                return HttpResponseRedirect(dest)
            else:
                return HttpResponse('not valid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required(login_url='/login')
def school_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(index))

def school_view(request, num):
    try:
        user = User.objects.get(id=num)
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    else:
        team_list = Team.objects.filter(school=user.school)
        player_list = Player.objects.filter(school=user.school,)
        return render(request, 'school_view.html', {
            'school': user.school,
            'user': request.user, # footer
            'school_list': team_list,
            'player_list': player_list,
            })

def to_unicode_or_bust(
    obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        return obj

def create_school(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            school = School(user=user)
            school.name = to_unicode_or_bust(request.POST["name"])
            school.numberp = 1
            school.numberm = 1
            school.superuser = False
            school.save()
            u = authenticate(username=request.POST['username'],
                             password=request.POST['password'])
            login(request, u)
            return HttpResponseRedirect(reverse(index))
        else:
            return HttpResponse('user not valid')
    else:
        form = UserForm()
    return render(request, 'school_form.html', {'form': form})

def team_view(request, pk):
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    else:
        team_list = Team.objects.filter(school=user.school)
        team = Team.objects.get(id=pk)
        player_list = Player.objects.filter(team= team,)

        return render(request, 'team_view.html', {
            'school': user.school,
            'user': request.user, # footer
            'team': team,
            'school_list': team_list,
            'player_list': player_list,
            })


class TeamDefinitiveView(DetailView):
    template_name = 'team_view.html'

    def get_context_data(self, **kwargs):
        context = super(TeamDefinitiveView, self).get_context_data(**kwargs)
        player_list = Player.objects.filter(school=self.request.user.school,)
        context['player_list']= player_list
        return context


class TeamView(LoginRequiredMixin, TeamDefinitiveView):
    model = Team

@login_required(login_url='/login')
def create_team(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if "cancel" in request.POST:
                return HttpResponseRedirect(reverse(index))
        if form.is_valid():
           team = form.save(commit = False)
           team.school = request.user.school
           team.playersnumber = 0
           if team.years == 1:
                team.name = request.user.school.name +" '"+ABC[request.user.school.numberp-1]+"'"
                number = request.user.school.numberp +1 
                school = School.objects.filter(name=request.user.school.name).update(numberp=number)
           else:
                team.name = request.user.school.name +" '"+ABC[request.user.school.numberm-1]+"'"
                number = request.user.school.numberm +1 
                school = School.objects.filter(name=request.user.school.name).update(numberm=number)
           team.save()
           return render(request, 'team_success.html', {
                'team': team,
            })
        
    else:
        form = TeamForm()
    return render(request, 'team_form.html', {'form': form})

class TeamDefinitiveDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('index') # in the future, this will redirect to the user profile
    template_name = 'confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super(TeamDefinitiveDelete, self).get_object()
        if not obj.school == self.request.user.school:
            raise Http404
        return obj

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.success_url
            return HttpResponseRedirect(url)
        else:
            return super(TeamDefinitiveDelete, self).post(request, *args, **kwargs)



class TeamDelete(TeamDefinitiveDelete):
    model = Team

class TeamUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'team_form.html'
    login_url = '/login'
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            
            return HttpResponseRedirect(reverse(index))
        else:
            #return HttpResponseRedirect(reverse(index))
            return super(TeamUpdate, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(TeamUpdate, self).get_object()
        # only the creator can delete his own application
        return obj


@login_required(login_url='/login')
def create_player(request, pk):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    if request.user.school == Team.objects.get(id=pk).school:
        if request.method == 'POST':
            form = PlayerEditForm(request.POST)
            if "cancel" in request.POST:
                    return HttpResponseRedirect(reverse('view_team', kwargs={'pk':pk}))
            if form.is_valid():
                player = form.save(commit = False)
                player.school = request.user.school
                player.team = Team.objects.get(id=pk)
                player.save()
                numero = Team.objects.get(id=pk).playersnumber+1
                team = Team.objects.filter(name=Team.objects.get(id=pk).name, years=Team.objects.get(id=pk).years).update(playersnumber=numero)
                return HttpResponseRedirect(reverse('add_player', kwargs={'pk':pk}))
        else:
            form = PlayerEditForm()
        return render(request, 'player_form.html', {'form': form})
    else:
        raise Http404


def player_view(request, pk):
    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse(index))
    player = Player.objects.get(id=pk)
    return render(request, 'player_view.html', {
        'player': player,
        })


class PlayerDefinitiveDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('index') # in the future, this will redirect to the user profile
    template_name = 'confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super(PlayerDefinitiveDelete, self).get_object()
        if not obj.school == self.request.user.school:
            raise Http404
        return obj

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = self.success_url
            return HttpResponseRedirect(url)
        else:
            return super(PlayerDefinitiveDelete, self).post(request, *args, **kwargs)



class PlayerDelete(PlayerDefinitiveDelete):
    model = Player


@login_required(login_url='/login')
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return HttpResponse('user not valid')
    else:
        form = MatchForm()
    return render(request, 'match_form.html', {'form': form})


def view_all_match(request):
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    match_list1 = Match.objects.filter(years=1,).order_by('hora','minutes','place')
    match_list2 = Match.objects.filter(years=2,).order_by('hora','minutes','place')
    if request.user.is_anonymous():
        return render(request, 'match_all_view.html', {
        'match_list1': match_list1,
        'match_list2': match_list2,

    })
    return render(request, 'match_all_view.html', {
        'school':user.school,
        'match_list1': match_list1,
        'match_list2': match_list2,

    })

def match_view(request, pk):
    match = Match.objects.get(id=pk)
    return render(request, 'match_view.html', {
        'match': match,
        })

class MatchUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            
            return HttpResponseRedirect(reverse(index))
        else:
            #return HttpResponseRedirect(reverse(index))
            return super(MatchUpdate, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(MatchUpdate, self).get_object()
        # only the creator can delete his own application
        return obj


class ResultUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchResultForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse(index))
        else:
            post_mutable = request.POST.copy()
        # Now you can change values:
            if(post_mutable['team2Score'] > post_mutable['team1Score']):
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(matchs=Team.objects.get(id=post_mutable['local']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(lose=Team.objects.get(id=post_mutable['local']).lose+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalc=Team.objects.get(id=post_mutable['local']).goalc+int(post_mutable['team2Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalf=Team.objects.get(id=post_mutable['local']).goalf+int(post_mutable['team1Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(matchs=Team.objects.get(id=post_mutable['away']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(wins=Team.objects.get(id=post_mutable['away']).wins+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(point=Team.objects.get(id=post_mutable['away']).point+3)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalc=Team.objects.get(id=post_mutable['away']).goalc+int(post_mutable['team1Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalf=Team.objects.get(id=post_mutable['away']).goalf+int(post_mutable['team2Score']))
            elif(post_mutable['team1Score'] > post_mutable['team2Score']):
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(matchs=Team.objects.get(id=post_mutable['away']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(lose=Team.objects.get(id=post_mutable['away']).lose+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalc=Team.objects.get(id=post_mutable['away']).goalc+int(post_mutable['team1Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalf=Team.objects.get(id=post_mutable['away']).goalf+int(post_mutable['team2Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(matchs=Team.objects.get(id=post_mutable['local']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(wins=Team.objects.get(id=post_mutable['local']).wins+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(point=Team.objects.get(id=post_mutable['local']).point+3)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalc=Team.objects.get(id=post_mutable['local']).goalc+int(post_mutable['team2Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalf=Team.objects.get(id=post_mutable['local']).goalf+int(post_mutable['team1Score']))
            else:
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(matchs=Team.objects.get(id=post_mutable['away']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(draw=Team.objects.get(id=post_mutable['away']).draw+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(point=Team.objects.get(id=post_mutable['away']).point+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalc=Team.objects.get(id=post_mutable['away']).goalc+int(post_mutable['team1Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(goalf=Team.objects.get(id=post_mutable['away']).goalf+int(post_mutable['team2Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(matchs=Team.objects.get(id=post_mutable['local']).matchs+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(draw=Team.objects.get(id=post_mutable['local']).draw+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(point=Team.objects.get(id=post_mutable['local']).point+1)
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalc=Team.objects.get(id=post_mutable['local']).goalc+int(post_mutable['team2Score']))
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(goalf=Team.objects.get(id=post_mutable['local']).goalf+int(post_mutable['team1Score']))
            #return HttpResponseRedirect(reverse(index))
            return super(ResultUpdate, self).post(post_mutable, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(ResultUpdate, self).get_object()
        # only the creator can delete his own application
        return obj

class OctavosUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchCuartosForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse(index))
        else:
            post_mutable = request.POST.copy()
        # Now you can change values:
            if(post_mutable['team2Score'] > post_mutable['team1Score']):
                if post_mutable['octavos']>6:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(cuartos=4)
                elif post_mutable['octavos']>4:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(cuartos=3)
                elif post_mutable['octavos']>2:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(cuartos=2)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(cuartos=1)                    
            elif(post_mutable['team1Score'] > post_mutable['team2Score']):
                if post_mutable['octavos']>6:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(cuartos=4)
                elif post_mutable['octavos']>4:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(cuartos=3)
                elif post_mutable['octavos']>2:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(cuartos=2)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(cuartos=1)

            #return HttpResponseRedirect(reverse(index))
            return super(OctavosUpdate, self).post(post_mutable, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(OctavosUpdate, self).get_object()
        # only the creator can delete his own application
        return obj

class CuartosUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchSemisForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse(index))
        else:
            post_mutable = request.POST.copy()
        # Now you can change values:
            if(post_mutable['team2Score'] > post_mutable['team1Score']):
                if post_mutable['cuartos']>2:
                    print("S1  ")
                    print(post_mutable['cuartos'])
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(semis=1)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(semis=2)
                    print("S2  ")
                    print(post_mutable['cuartos'])

            elif(post_mutable['team1Score'] > post_mutable['team2Score']):
                if(post_mutable['cuartos']>2):
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(semis=1)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(semis=2)

            #return HttpResponseRedirect(reverse(index))
            return super(CuartosUpdate, self).post(post_mutable, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(CuartosUpdate, self).get_object()
        # only the creator can delete his own application
        return obj

class FinalUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchFinalForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse(index))
        else:
            post_mutable = request.POST.copy()
        # Now you can change values:
            if(post_mutable['team2Score'] > post_mutable['team1Score']):
                if post_mutable['semis']>2:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(final=1)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(final=2)

            elif(post_mutable['team1Score'] > post_mutable['team2Score']):
                if(post_mutable['semis']>2):
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(final=1)
                else:
                    team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(final=2)

            #return HttpResponseRedirect(reverse(index))
            return super(FinalUpdate, self).post(post_mutable, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(FinalUpdate, self).get_object()
        # only the creator can delete his own application
        return obj

# def create_group(request):
#     if request.method == 'POST':
#         form = GroupForm(request.POST)
#         if form.is_valid():
#             match = form.save()
#             return HttpResponseRedirect(reverse(index))
#         else:
#             return HttpResponse('user not valid')
#     else:
#         form = GroupForm()
#     return render(request, 'group_form.html', {'form': form})

class EliminatoriaUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'match_form.html'
    login_url = '/login'
    model = Match
    form_class = MatchResultForm
    success_url = reverse_lazy('index')

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse(index))
        else:
            post_mutable = request.POST.copy()
        # Now you can change values:
            if(post_mutable['team2Score'] > post_mutable['team1Score']):
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['away']).name,years=Team.objects.get(id=post_mutable['away']).years).update(cuartos=2)
            else:
                team = Team.objects.filter(name=Team.objects.get(id=post_mutable['local']).name,years=Team.objects.get(id=post_mutable['local']).years).update(cuartos=2)
            #return HttpResponseRedirect(reverse(index))
            return super(ResultUpdate, self).post(post_mutable, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(ResultUpdate, self).get_object()
        # only the creator can delete his own application
        return obj

def group_view1(request, pk):
    team_group = Team.objects.filter(group=pk,years=1).order_by('-point','-goalf','goalc')
    group_matchs = Match.objects.filter(group=pk,years=1).order_by('hora','minutes','place')
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return render(request, 'group_view.html', {
            'group': team_group,
            'group_matchs': group_matchs,
            'group_name': ABC[int(pk)-1],

            })
    return render(request, 'group_view.html', {
        'school': user.school,
        'group': team_group,
        'group_matchs': group_matchs,
        'group_name': ABC[int(pk)-1],

        })

def group_view1_all(request):
    return render(request, 'choose_group_sub9.html', {

    })

def group_view2_all(request):
    return render(request, 'choose_group_sub12.html', {

    })

def select_years(request):
    return render(request, 'choose_years.html', )


def group_view2(request, pk):
    team_group = Team.objects.filter(group=pk,years=2).order_by('-point','-goalf','goalc')
    group_matchs = Match.objects.filter(group=pk,years=2).order_by('hora','minutes','place')
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return render(request, 'group_view.html', {
            'group': team_group,
            'group_matchs': group_matchs,
            'group_name': ABC[int(pk)-1],

            })
    return render(request, 'group_view.html', {
        'school': user.school,
        'group': team_group,
        'group_matchs': group_matchs,
        'group_name': ABC[int(pk)-1],
        })

def eliminatoria_view1(request):
    team_cuartos = Team.objects.filter(years=1).order_by('cuartos','group')
    team_cuartos_filter = filter(lambda x: x.cuartos > 0, team_cuartos)
    team_semis = Team.objects.filter(years=1).order_by('semis','cuartos')
    team_semis_filter = filter(lambda x: x.semis > 0, team_semis)
    team_final = Team.objects.filter(years=1).order_by('semis')
    team_final_filter = filter(lambda x: x.final > 0, team_final)

    match_cuartos = Match.objects.filter(years=1).order_by('hora','minutes','cuartos')
    match_cuartos_filter = filter(lambda x: x.cuartos > 0, match_cuartos)
    match_semis = Match.objects.filter(years=1).order_by('hora','minutes','semis')
    match_semis_filter = filter(lambda x: x.semis > 0, match_semis)
    match_final = Match.objects.filter(years=1).order_by('hora','minutes')
    match_final_filter = filter(lambda x: x.final > 0, match_final)    
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return render(request, 'eliminatoria_view_sub9.html', {
            'cuartos': team_cuartos_filter,
            'semis': team_semis_filter,
            'final': team_final_filter,
            'match_cuartos' : match_cuartos_filter,
            'match_semis' : match_semis_filter,
            'match_final' : match_final_filter,

            })
    return render(request, 'eliminatoria_view_sub9.html', {
            'school': user.school,
            'cuartos': team_cuartos_filter,
            'semis': team_semis_filter,
            'final': team_final_filter,
            'match_cuartos' : match_cuartos_filter,
            'match_semis' : match_semis_filter,
            'match_final' : match_final_filter,

            })

def eliminatoria_view2(request):
    team_octavos = Team.objects.filter(years=2).order_by('octavos','point','group')
    team_octavos_filter = filter(lambda x: x.octavos > 0, team_octavos)
    team_cuartos = Team.objects.filter(years=2).order_by('cuartos','octavos')
    team_cuartos_filter = filter(lambda x: x.cuartos > 0, team_cuartos)
    team_semis = Team.objects.filter(years=2).order_by('semis','cuartos')
    team_semis_filter = filter(lambda x: x.semis > 0, team_semis)
    team_final = Team.objects.filter(years=2).order_by('semis')
    team_final_filter = filter(lambda x: x.final > 0, team_final)

    match_octavos = Match.objects.filter(years=2).order_by('hora','minutes','octavos')
    match_octavos_filter = filter(lambda x: x.octavos > 0, match_octavos)
    match_cuartos = Match.objects.filter(years=2).order_by('hora','minutes','cuartos')
    match_cuartos_filter = filter(lambda x: x.cuartos > 0, match_cuartos)
    match_semis = Match.objects.filter(years=2).order_by('hora','minutes','semis')
    match_semis_filter = filter(lambda x: x.semis > 0, match_semis)
    match_final = Match.objects.filter(years=2).order_by('hora','minutes',)
    match_final_filter = filter(lambda x: x.final > 0, match_final)    
    try:
        user = request.user
    except User.DoesNotExist:
        raise Http404()
    if request.user.is_anonymous():
        return render(request, 'eliminatoria_sub12_view.html', {
        'octavos': team_octavos_filter,
        'cuartos': team_cuartos_filter,
        'semis': team_semis_filter,
        'final': team_final_filter,
        'match_octavos' : match_octavos_filter,
        'match_cuartos' : match_cuartos_filter,
        'match_semis' : match_semis_filter,
        'match_final' : match_final_filter,
        })
    return render(request, 'eliminatoria_sub12_view.html', {
        'school': user.school,
        'octavos': team_octavos_filter,
        'cuartos': team_cuartos_filter,
        'semis': team_semis_filter,
        'final': team_final_filter,
        'match_octavos' : match_octavos_filter,
        'match_cuartos' : match_cuartos_filter,
        'match_semis' : match_semis_filter,
        'match_final' : match_final_filter,
        })