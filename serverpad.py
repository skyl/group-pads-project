"""
Start all server components of Hotdot.

Each component is a 'Twisted Service':
    - Django (using twisted.web.wsgi)
    - Orbited (using the orbited 'cometsession' and 'proxy' modules)
    - Stomp pub/sub server (using the 'morbid' module from MorbidQ)
    - RestQMessageProxy (Orbited messages filter/logger/modifier)
"""
from twisted.web import static, resource, server
from twisted.application import internet, service

from morbid import StompFactory

# Config
from orbited import logging, config
logging.setup(config.map)
INTERFACE = "localhost"
#Runtime config, is there a cleaner way?:
config.map["[access]"]={(INTERFACE, 9999):"*"}
STATIC_PORT = 8000
RESTQ_PROXY_PORT = 5000
STOMP_PORT = 9999

try:
    import pinax
except ImportError:
    pinax = None


if pinax:
    import sys
    from os.path import join # abspath, dirname
    from django.conf import settings
    from django.core.management import setup_environ, execute_from_command_line
    try:
        import settings as settings_mod # Assumed to be in the same directory.
    except ImportError:
        sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
        sys.exit(1)

# setup the environment before we start accessing things in the settings.
    setup_environ(settings_mod)
    sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
    sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

#The below depend on Orbited's logging.setup(...), from above.
from orbited import cometsession
from orbited import proxy

#local imports
from twisted_wsgi import get_root_resource
from pads.realtime.stompfactory import get_stomp_factory
from pads.realtime.message_handlers import MESSAGE_HANDLERS
from pads.realtime.restq import RestQMessageProxy

#Twisted Application setup:
application = service.Application('hotdot')
serviceCollection = service.IServiceCollection(application)

# Django and static file server:
root_resource = get_root_resource()
root_resource.putChild("static", static.File("static"))
http_factory = server.Site(root_resource, logPath="http.log")
internet.TCPServer(STATIC_PORT, http_factory, interface=INTERFACE).setServiceParent(serviceCollection)

# Orbited server:
proxy_factory = proxy.ProxyFactory()
internet.GenericServer(cometsession.Port, factory=proxy_factory, resource=root_resource, childName="tcp", interface=INTERFACE).setServiceParent(serviceCollection)

# Stomp server:
stomp_factory = get_stomp_factory()
internet.TCPServer(STOMP_PORT, stomp_factory, interface=INTERFACE).setServiceParent(serviceCollection)

# RestQMessageProxy (message filter/logger/modifier):
restq_resource = RestQMessageProxy(MESSAGE_HANDLERS)
restq_proxy_factory = server.Site(restq_resource, logPath="restqproxy.log")
internet.TCPServer(RESTQ_PROXY_PORT, restq_proxy_factory, interface=INTERFACE).setServiceParent(serviceCollection)
