from hvz_utils import *
from HvZ.models import *
from django.views.generic import FormView, DetailView
from django.views.generic.detail import BaseDetailView
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

    def get(self, request, *args, **kwargs):
        self.queryset = Rule.objects.get(id=kwargs['rule_id'])
        if self.queryset.exists():
            rule = queryset.get()
            context = {'description': rule.examples,
                       'youtube': rule.youtube}
            if rule.category != "C":
                context["image"] = rule.image
        else:
            context = {'failure': "No rule with that ID"}

        return self.render_to_response(context)


class MissionJSONView(JSONResponseMixin, BaseDetailView):
    """Currently returns what humans should see regardless of the player's team"""

    model = Mission
    pk_url_kwarg = "mission_id"

    def get(self, request, *args, **kwargs):
        self.queryset = Mission.objects.get(id=kwargs['mission_id'])
        if self.queryset.exists():
            mission = queryset.get()
            context = {'day': DAY[mission.day],
                       'kind': MISSION_LEGEND[mission.kind],
                       'result': VICTORY[mission.result],
                       'title': mission.get_title("H"),
                       'story': mission.get_story("H"),
                       'reward': mission.get_reward("H"),
                       }

        else:
            context = {'failure': "No mission with that ID"}

        return self.render_to_response(context)


class CharacterProfileView(DetailView):

    model = Character
    pk_url_kwarg = "player_id"
    template_name = "new/character_profile.html"

    def get(self, request, *args, **kwargs):
        if self.queryset.exists():
            character = self.queryset.get()
            context["first"] = character.player.user.first_name
            context["last"] = character.player.user.last_name
            context["school"] = character.player.school
            context["year"] = CLASS_YEAR[character.player.class_year]
            context["dorm"] = character.player.dorm
            context["team"] = character.team
            context["class"] = character.upgrade
            context["meals"] = character.meals
        else:
            context["failure"] = "No player with that ID"

        return self.render_to_response(context)


class RegistrationView(FormView):

    class RegForm(forms.Form):
        first = forms.CharField(label='First Name', max_length=30, required=True, help_text="<div class='reminder'>Your First Name</div>")
        last = forms.CharField(label='Last Name', max_length=30, required=True, help_text="<div class='reminder'>Your Last Name</div>")
        email = forms.EmailField(label='Email Address', required=True, help_text="<div class='reminder'>Enter in an email address that you check regularly since you will be receiving game updates approximately 3 times per day during the week of the game. This email address will also be used to log you in to the website</div>")
        password = forms.CharField(required=True, widget=forms.PasswordInput, help_text="<div class='reminder'>Enter a password that will be easy for you to remember but difficult for others to guess.</div>")
        school = forms.ModelChoiceField(queryset=School.objects.all().order_by('name'), required=True, empty_label="None", help_text="<div class='reminder'>Select which school you attend. If you do not attend one of the 7Cs, select \"None\".</div>")
        dorm = forms.ModelChoiceField(queryset=Building.objects.order_by('name'), required=True, empty_label="Off Campus", help_text="<div class='reminder'>Select which dorm you expect to sleep in on most nights during the game. If you do not live on campus, select \"Off Campus\"</div>")
        grad = forms.ChoiceField(
            label='Graduation Year',
            choices=(
                ("2011", "2011"),
                ("2012", "2012"),
                ("2013", "2013"),
                ("2014", "2014"),
                ("2015", "2015"),
                ("2016", "2016"),
                ("2017", "2017"),
                ("", "Not a Student")
            ),
            initial="2011",
            required=False,
            help_text="<div class='reminder'>Select which year you expect to graduate. If you don't know yet, select 5 years after the fall of your first year.</div>")
        cell = forms.DecimalField(max_digits=10, decimal_places=0, required=False, help_text="<div class='reminder'>If you want to be able to text message the game's website enter in your phone number here. Include the area code, but do not include hyphens or the leading 1. We will not use this number except in emergencies or in response to texts from you.</div>")
        oz = forms.BooleanField(label='OZ Pool', required=False, help_text="<div class='reminder'>Check this box if you would like to begin afflicted with the zombie curse.</div>")
        c3 = forms.BooleanField(label='C3 Pool', required=False, help_text="<div class='reminder'>Check this box if you would like to be a human leader and plan on attending each night mission.</div>")
        feed = forms.CharField(label='Feed Code', min_length=5, max_length=5, required=True, help_text="<div class='reminder'>When you are finished entering in all of your other information, have the tabler registering you type in your feed code.<br />TABLERS: Feed codes can only contain the letters A, C, E, K, L, N, P, Q, S, T, W, and Z.</div>")

    form_class = RegForm
    success_url = "/auth/register/"
    template_name = "new/registration.html"

    def form_valid(self):
        pass

    def form_invalid(self):
        pass

    def post(self):
        pass
