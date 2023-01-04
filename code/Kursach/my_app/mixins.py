from django.shortcuts import redirect, render
from .model_objects import UserStatus


class UserStatusRequiredMixin:
    allowed_statuses: list[UserStatus] = []
    login_url = "login_url"
    forbidden_template = "my_app/users/forbidden.html"

    def dispatch(self, request, *args, **kwargs):
        status = UserStatus(request.COOKIES.get("user_status"))
        if status == UserStatus.ANONYMOUS:
            return redirect(self.login_url)
        if status not in self.allowed_statuses:
            return render(request, self.forbidden_template)
        return super().dispatch(request, *args, **kwargs)
