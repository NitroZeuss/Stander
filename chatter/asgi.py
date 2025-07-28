"""
ASGI config for chatter project.
"""

import os
import django

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # make sure this exists and is correct

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatter.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns  # ✅ fixed the typo here
        )
    ),
})
