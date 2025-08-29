import pytest
import test_helpers

from django.urls import reverse


pytestmark = [pytest.mark.django_db]


def tests_Expense_list_view(client):
    instance1 = test_helpers.create_construction_Expense()
    instance2 = test_helpers.create_construction_Expense()
    url = reverse("construction_Expense_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Expense_create_view(client):
    url = reverse("construction_Expense_create")
    data = {
        "expense_type": "text",
        "amount": 1.0,
        "description": "text",
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Expense_detail_view(client):
    instance = test_helpers.create_construction_Expense()
    url = reverse("construction_Expense_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Expense_update_view(client):
    instance = test_helpers.create_construction_Expense()
    url = reverse("construction_Expense_update", args=[instance.pk, ])
    data = {
        "expense_type": "text",
        "amount": 1.0,
        "description": "text",
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Investor_list_view(client):
    instance1 = test_helpers.create_construction_Investor()
    instance2 = test_helpers.create_construction_Investor()
    url = reverse("construction_Investor_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Investor_create_view(client):
    url = reverse("construction_Investor_create")
    data = {
        "first_name": "text",
        "last_name": "text",
        "phone": "text",
        "email": "user@tempurl.com",
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Investor_detail_view(client):
    instance = test_helpers.create_construction_Investor()
    url = reverse("construction_Investor_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Investor_update_view(client):
    instance = test_helpers.create_construction_Investor()
    url = reverse("construction_Investor_update", args=[instance.pk, ])
    data = {
        "first_name": "text",
        "last_name": "text",
        "phone": "text",
        "email": "user@tempurl.com",
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Period_list_view(client):
    instance1 = test_helpers.create_construction_Period()
    instance2 = test_helpers.create_construction_Period()
    url = reverse("construction_Period_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Period_create_view(client):
    url = reverse("construction_Period_create")
    data = {
        "label": "text",
        "year": 1,
        "month_number": 1,
        "month_name": "text",
        "weight": 1,
        "start_date_shamsi": datetime.now(),
        "end_date_shamsi": datetime.now(),
        "start_date_gregorian": datetime.now(),
        "end_date_gregorian": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Period_detail_view(client):
    instance = test_helpers.create_construction_Period()
    url = reverse("construction_Period_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Period_update_view(client):
    instance = test_helpers.create_construction_Period()
    url = reverse("construction_Period_update", args=[instance.pk, ])
    data = {
        "label": "text",
        "year": 1,
        "month_number": 1,
        "month_name": "text",
        "weight": 1,
        "start_date_shamsi": datetime.now(),
        "end_date_shamsi": datetime.now(),
        "start_date_gregorian": datetime.now(),
        "end_date_gregorian": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Project_list_view(client):
    instance1 = test_helpers.create_construction_Project()
    instance2 = test_helpers.create_construction_Project()
    url = reverse("construction_Project_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Project_create_view(client):
    url = reverse("construction_Project_create")
    data = {
        "name": "text",
        "start_date_shamsi": datetime.now(),
        "end_date_shamsi": datetime.now(),
        "start_date_gregorian": datetime.now(),
        "end_date_gregorian": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Project_detail_view(client):
    instance = test_helpers.create_construction_Project()
    url = reverse("construction_Project_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Project_update_view(client):
    instance = test_helpers.create_construction_Project()
    url = reverse("construction_Project_update", args=[instance.pk, ])
    data = {
        "name": "text",
        "start_date_shamsi": datetime.now(),
        "end_date_shamsi": datetime.now(),
        "start_date_gregorian": datetime.now(),
        "end_date_gregorian": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Transaction_list_view(client):
    instance1 = test_helpers.create_construction_Transaction()
    instance2 = test_helpers.create_construction_Transaction()
    url = reverse("construction_Transaction_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Transaction_create_view(client):
    url = reverse("construction_Transaction_create")
    data = {
        "date_shamsi": datetime.now(),
        "date_gregorian": datetime.now(),
        "amount": 1.0,
        "transaction_type": "text",
        "description": "text",
        "day_remaining": 1,
        "day_from_start": 1,
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Transaction_detail_view(client):
    instance = test_helpers.create_construction_Transaction()
    url = reverse("construction_Transaction_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Transaction_update_view(client):
    instance = test_helpers.create_construction_Transaction()
    url = reverse("construction_Transaction_update", args=[instance.pk, ])
    data = {
        "date_shamsi": datetime.now(),
        "date_gregorian": datetime.now(),
        "amount": 1.0,
        "transaction_type": "text",
        "description": "text",
        "day_remaining": 1,
        "day_from_start": 1,
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Unit_list_view(client):
    instance1 = test_helpers.create_construction_Unit()
    instance2 = test_helpers.create_construction_Unit()
    url = reverse("construction_Unit_list")
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance1) in response.content.decode("utf-8")
    assert str(instance2) in response.content.decode("utf-8")


def tests_Unit_create_view(client):
    url = reverse("construction_Unit_create")
    data = {
        "name": "text",
        "area": 1.0,
        "price_per_meter": 1.0,
        "total_price": 1.0,
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302


def tests_Unit_detail_view(client):
    instance = test_helpers.create_construction_Unit()
    url = reverse("construction_Unit_detail", args=[instance.pk, ])
    response = client.get(url)
    assert response.status_code == 200
    assert str(instance) in response.content.decode("utf-8")


def tests_Unit_update_view(client):
    instance = test_helpers.create_construction_Unit()
    url = reverse("construction_Unit_update", args=[instance.pk, ])
    data = {
        "name": "text",
        "area": 1.0,
        "price_per_meter": 1.0,
        "total_price": 1.0,
        "created_at": datetime.now(),
    }
    response = client.post(url, data)
    assert response.status_code == 302
