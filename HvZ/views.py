from django.views.generic import FormView, DetailView
from django.views.generic.detail import BaseDetailView
from django import http
from django.utils import simplejson as json

from forms import RegForm
from hvz_utils import *
from models import *


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

    form_class = RegForm
    success_url = "/auth/register/"
    template_name = "new/registration.html"

    def form_valid(self):
        pass

    def form_invalid(self):
        pass

    def post(self):
        pass
