import random
import string

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from construction import models as construction_models


def random_string(length=10):
    # Create a random string of length length
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def create_User(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_AbstractUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractUser.objects.create(**defaults)


def create_AbstractBaseUser(**kwargs):
    defaults = {
        "username": "%s_username" % random_string(5),
        "email": "%s_username@tempurl.com" % random_string(5),
    }
    defaults.update(**kwargs)
    return AbstractBaseUser.objects.create(**defaults)


def create_Group(**kwargs):
    defaults = {
        "name": "%s_group" % random_string(5),
    }
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_ContentType(**kwargs):
    defaults = {
    }
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_construction_Expense(**kwargs):
    defaults = {}
    defaults["expense_type"] = ""
    defaults["amount"] = ""
    defaults["description"] = ""
    defaults["created_at"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Expense.objects.create(**defaults)
def create_construction_Investor(**kwargs):
    defaults = {}
    defaults["first_name"] = ""
    defaults["last_name"] = ""
    defaults["phone"] = ""
    defaults["email"] = ""
    defaults["created_at"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Investor.objects.create(**defaults)
def create_construction_Period(**kwargs):
    defaults = {}
    defaults["label"] = ""
    defaults["year"] = ""
    defaults["month_number"] = ""
    defaults["month_name"] = ""
    defaults["weight"] = ""
    defaults["start_date_shamsi"] = datetime.now()
    defaults["end_date_shamsi"] = datetime.now()
    defaults["start_date_gregorian"] = datetime.now()
    defaults["end_date_gregorian"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Period.objects.create(**defaults)
def create_construction_Project(**kwargs):
    defaults = {}
    defaults["name"] = ""
    defaults["start_date_shamsi"] = datetime.now()
    defaults["end_date_shamsi"] = datetime.now()
    defaults["start_date_gregorian"] = datetime.now()
    defaults["end_date_gregorian"] = datetime.now()
    defaults["created_at"] = datetime.now()
    defaults["updated_at"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Project.objects.create(**defaults)
def create_construction_Transaction(**kwargs):
    defaults = {}
    defaults["date_shamsi"] = datetime.now()
    defaults["date_gregorian"] = datetime.now()
    defaults["amount"] = ""
    defaults["transaction_type"] = ""
    defaults["description"] = ""
    defaults["day_remaining"] = ""
    defaults["day_from_start"] = ""
    defaults["created_at"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Transaction.objects.create(**defaults)
def create_construction_Unit(**kwargs):
    defaults = {}
    defaults["name"] = ""
    defaults["area"] = ""
    defaults["price_per_meter"] = ""
    defaults["total_price"] = ""
    defaults["created_at"] = datetime.now()
    defaults.update(**kwargs)
    return construction_models.Unit.objects.create(**defaults)
