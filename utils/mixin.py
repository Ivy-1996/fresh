from django.contrib.auth.decorators import login_required
from django.views import View


class LoginRequredMixIn(View):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequredMixIn, cls).as_view(**initkwargs)
        return login_required(view)

