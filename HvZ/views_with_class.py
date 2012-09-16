from hvz_utils import *
from hvz.models import *
from django.views.generic import TemplateView,FormView,ListView,BaseDetailView,DetailView
from django import http
from django.utils import simplejson as json

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)
    
class RuleJSONView(JSONResponseMixin, BaseDetailView):
    
    model = Rule
    pk_url_kwarg = "rule_id"
    
    queryset = Rule.objects.get(id=self.kwargs['rule_id'])
    
    def get(self, request, *args, **kwargs):
        if self.queryset.exists():
            rule = queryset.get()
            context = {'description':rule.examples,
                       'youtube':rule.youtube}
            if rule.category != "C":
                context["image"]=rule.image
        else:
            context={'failure':"No rule with that ID"}
        
        return self.render_to_response(context)

"""Currently returns what humans should see regardless of the player's team"""
class MissionJSONView(JSONResponseMixin, BaseDetailView):
    
    model = Mission
    pk_url_kwarg = "mission_id"
    
    queryset = Mission.objects.get(id=self.kwargs['mission_id'])
    
    def get(self,request,*args,**kwargs):
        if self.queryset.exists():
            mission = queryset.get()
            context = {'day':DAY[mission.day],
                       'kind':MISSION_LEGEND[mission.kind],
                       'result':VICTORY[mission.result],
                       'title':mission.get_title("H"),
                       'story':mission.get_story("H"),
                       'reward':mission.get_reward("H"),
                       }
            
        else:
            context={'failure':"No mission with that ID"}
            
        return self.render_to_response(context)

class CharacterProfileView(DetailView):
    
    model = Character
    pk_url_kwarg = "player_id"
    template_name = "new/character_profile.html"
    
    def get(self, request, *args, **kwargs):
        if self.queryset.exists():
            character = self.queryset.get()
            context["first"] = character.player.user.first_name
            context["last"] =  character.player.user.last_name
            context["school"] = character.player.school
            context["year"] = CLASS_YEAR[character.player.class_year]
            context["dorm"]=  character.player.dorm
            context["team"] = character.team
            context["class"] = character.upgrade
            context["meals"] = character.meals
        else:
            context["failure"] = "No player with that ID"
            
        return self.render_to_response(context)
    
    
class RegistrationView(FormView):

    class RegForm(forms.Form):
        first = forms.CharField(label='First Name',max_length=30,required=True,help_text="<div class='reminder'>Your First Name</div>")
        last = forms.CharField(label='Last Name',max_length=30,required=True,help_text="<div class='reminder'>Your Last Name</div>")
        email = forms.EmailField(label='Email Address',required=True,help_text="<div class='reminder'>Enter in an email address that you check regularly since you will be receiving game updates approximately 3 times per day during the week of the game. This email address will also be used to log you in to the website</div>")
        password = forms.CharField(required=True,widget=forms.PasswordInput,help_text="<div class='reminder'>Enter a password that will be easy for you to remember but difficult for others to guess.</div>")
        school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'),required=True,empty_label="None",help_text="<div class='reminder'>Select which school you attend. If you do not attend one of the 7Cs, select \"None\".</div>")
        dorm = forms.ModelChoiceField(queryset=Building.objects.filter(building_type='D').order_by('name'),required=True,empty_label="Off Campus",help_text="<div class='reminder'>Select which dorm you expect to sleep in on most nights during the game. If you do not live on campus, select \"Off Campus\"</div>")
        grad = forms.ChoiceField(label='Graduation Year', choices = (("2011","2011"),("2012","2012"),("2013","2013"),("2014","2014"),("2015","2015"),("2016","2016"),("2017","2017"),("","Not a Student")), initial="2011",required=False,help_text="<div class='reminder'>Select which year you expect to graduate. If you don't know yet, select 5 years after the fall of your first year.</div>")
        cell = forms.DecimalField(max_digits=10,decimal_places=0,required=False,help_text="<div class='reminder'>If you want to be able to text message the game's website enter in your phone number here. Include the area code, but do not include hyphens or the leading 1. We will not use this number except in emergencies or in response to texts from you.</div>")
        oz = forms.BooleanField(label='OZ Pool',required=False,help_text="<div class='reminder'>Check this box if you would like to begin afflicted with the zombie curse.</div>")
        c3 = forms.BooleanField(label='C3 Pool',required=False,help_text="<div class='reminder'>Check this box if you would like to be a human leader and plan on attending each night mission.</div>")
        feed = forms.CharField(label='Feed Code',min_length=5,max_length=5,required=True,help_text="<div class='reminder'>When you are finished entering in all of your other information, have the tabler registering you type in your feed code.<br />TABLERS: Feed codes can only contain the letters A, C, E, K, L, N, P, Q, S, T, W, and Z.</div>")
        
    form_class = self.RegForm
    success_url = "/auth/register/"
    template_name = "new/registration.html"
    
    def form_valid(self):
        pass
    
    def form_invalid(self):
        pass
    
    def post(self):
        pass
    

class TwilioSMSView(TemplateView):
    from HvZ.models import Player, Registration, PlayerSetting, School, Meal, Game
    import re
    
    template_name = "new/sms.xml"
    
    def get_context_data(**kwargs):
        if request.GET.get("To",0)=="+19095254551":
            #received something from twilio
            msg = request.GET.get("Body","Help")
            cmd = msg.partition(" ")[0].lower()
            arg = msg.partition(" ")[2].lower()
            sender_pots = Player.objects.filter(cell=str(request.GET.get("From","+10"))[2:])
            if sender_pots.exists():
                sender_player = sender_pots.get()
                sender_team = get_team(sender_player)
                resp = "You have been identified as: "+str(sender_player)
                if True:
                    sender_pots = Registration.objects.filter(player=sender_player,game=get_current_game())
                    if sender_pots.exists():
                        sender_reg = sender_pots.get()
                        if cmd=="mod":
                            od = get_on_duty()
                            if arg=="":
                                resp = "The on duty moderator is "+od["name"]+". You can reach them by calling this number."
                        elif cmd=="stop" or cmd=="quit" or cmd=="unsubscribe" or cmd=="leave":
                            sender_player.cell="";
                            sender_player.save()
                            resp = "You have been removed from all ZOMCOM and TacNet texting services. You are still playing the game. To sign up again, go to the website."
                        elif cmd=="status":
                            regs = Registration.objects.filter(game=get_current_game())
                            H = regs.filter(team="H").count()
                            Z = regs.filter(team="Z").count()
                            if len(arg)==0:
                                resp = "Humans: "+str(H)+" \nZombies: "+str(Z)
                            elif School.objects.filter(name=arg).exists():
                                hcount = str(H.filter(player__school__name=arg).count())
                                zcount = str(Z.filter(player__school__name=arg).count())
                                resp = str(School.objects.get(name=arg))+" has \nHumans: "+hcount+" \nZombies: "+zcount
                            elif Building.objects.filter(name=arg).exists():
                                hcount = str(H.filter(player__dorm__name=arg).count())
                                zcount = str(Z.filter(player__dorm__name=arg).count())
                                resp = str(Building.objects.get(name=arg))+" has \nHumans: "+hcount+" \nZombies: "+zcount
                            elif re.match(r"\d{4}",arg)>-1:
                                hcount = str(H.filter(player__grad_year=arg).count())
                                zcount = str(Z.filter(player__grad_year=arg).count())
                                resp = "Class of "+str(arg)+" has \nHumans: "+hcount+" \nZombies: "+zcount
                            else:
                                resp = "Please enter status with either a 4 digit year, the name of the school (Mudd, CMC, Pitzer, Pomona, Scripps, Keck, CGU, or None), dorm, or alone to find out human and zombie counts."
                        elif cmd=="feed" or cmd=="eat":
                            code = arg.partition(" ")[0].upper()
                            desc = arg.partition(" ")[2]
                            eaten_reg = Registration.objects.get(feed=clean_feed_code(code))
                            resp = eat(eater=sender_player,eaten=eaten_reg.player,description=desc,time=datetime.now())
                        elif cmd=="mission":
                            missions = Mission.objects.filter(result="N").order_by('-day','-kind')
                            if sender_team=="N":
                                resp = "You can only get missions if you are in the current game."
                            elif sender_team=="H":
                                missions = missions.exclude(show_players="M").exclude(show_players="Z")
                            else:
                                missions = missions.exclude(show_players="M").exclude(show_players="H")
    
                            if arg=="npc":
                                missions = missions.filter(kind="X")
                            elif arg=="legendary":
                                missions = missions.filter(kind="Y")
                            if missions.exists():
                                m = missions[0]
                                if sender_team=="H":
                                    resp = m.human_title+" ("+m.get_day()+" "+m.get_kind()+"): "+m.human_SMS
                                else:
                                    resp = m.zombie_title+" ("+m.get_day()+" "+m.get_kind()+"): "+m.zombie_SMS
                            else:
                                resp = "No mission of that type is visible to you yet."
                        elif cmd=="time":
                            resp = datetime.now()
                        else:
                            resp="Valid commands are status, mod, mission, feed, stop, and help."
                    else:
                        resp="You are not registered for the current game."
                else:
                    resp="You have sending commands disabled. Please go to the webite to enable this feature."
            elif "@" in cmd:
                sender = User.objects.filter(email__iexact=cmd)
                if sender.exists():
                    player = Player.objects.get(user=sender.get())
                    player.cell = str(request.GET.get("From","+10"))[2:]
                    player.save()
                    resp = "You have been added to ZOMCOM and TacNet."
                else:
                    resp = "No one with that email address is registered for ClaremontHvZ."
            else:
                resp = "You are not signed up for ZOMCOM and TacNet. Please text the email address you used for this game to this number to join."
        else:
            resp = "You viewed this page manually, it should only be viewed by phones."
        return render_to_response('sms.xml',
            {"response":resp, "to_mod": False
            },
            context_instance=RequestContext(request),
            mimetype="text/xml")
