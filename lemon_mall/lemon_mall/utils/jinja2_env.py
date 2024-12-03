from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_environment(**options):
    """jinja2 environment"""
    # Creating Environment Objects
    env = Environment(**options)
    # Custom syntax: {{static('relative path to static file')}} {{url('namespace of route')}}
    env.globals.update({
        'static': staticfiles_storage.url,  # Get the prefix of a static file
        'url': reverse, # inverse resolution
    })
    # Return the environment object
    return env