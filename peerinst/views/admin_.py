from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def new_user_approval(req: HttpRequest) -> HttpResponse:
    new_users = [
        {
            "username": f"test{i}",
            "signed_on": f"test{i}",
            "email": f"test{i}",
            "url": f"test{i}",
            "type": f"test{i}",
        }
        for i in range(10)
    ]
    context = {"new_users": new_users}
    return render(req, "admin/peerinst/new_user_approval.html", context)
