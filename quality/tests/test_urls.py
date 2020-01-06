from django.urls import reverse


def test_edit_patterns():
    assert reverse("quality:edit").endswith("quality/edit/")
    assert reverse("quality:add-criterion").endswith("quality/edit/add/")
    assert reverse("quality:update-criterion").endswith("quality/edit/update/")
    assert reverse("quality:remove-criterion").endswith("quality/edit/remove/")
