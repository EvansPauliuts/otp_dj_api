import io
import time
from functools import wraps

from PIL import Image
from django.db import models
from dateutil.parser import parse
from apps.accounts.models import BusinessUnit


def get_or_create_business_unit(*, bs_name):
    business_unit, _ = BusinessUnit.objects.get_or_create(name=bs_name)
    return business_unit


def get_pk_value(*, instance):
    pk_field = instance._meta.pk.name
    pk = getattr(instance, pk_field, None)

    if isinstance(pk, models.Model):
        pk = get_pk_value(instance=pk)
    return pk


def convert_to_date(date_str: str) -> str:
    try:
        return parse(date_str).date().isoformat()
    except ValueError:
        return date_str


def optimize_image(img, size):
    img = img.resize(size, resample=Image.Resampling.BICUBIC)
    img = img.convert('RGB')
    output = io.BytesIO()
    img.save(output, 'webp')
    output.seek(0)

    return output


def calc_time(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper
