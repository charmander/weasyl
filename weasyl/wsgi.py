import sentry_sdk
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from sentry_sdk.integrations.pyramid import PyramidIntegration

from libweasyl.configuration import configure_libweasyl
from weasyl.controllers.routes import setup_routes_and_views
import weasyl.define as d
import weasyl.macro as m
from weasyl.config import config_obj, config_read_bool
from weasyl.media import format_media_link
import weasyl.middleware as mw
from weasyl import staff_config


# Get a configurator and register some tweens to handle cleanup, etc.
config = Configurator()
config.add_tween("weasyl.middleware.status_check_tween_factory")
config.add_tween("weasyl.middleware.session_tween_factory")
config.add_tween("weasyl.middleware.db_timer_tween_factory")
config.add_tween("weasyl.middleware.cache_clear_tween_factory")
config.add_tween("weasyl.middleware.database_session_cleanup_tween_factory")
config.add_tween("weasyl.middleware.http2_server_push_tween_factory")
config.add_tween("weasyl.middleware.query_debug_tween_factory")
config.add_tween("pyramid.tweens.excview_tween_factory")  # Required to catch exceptions thrown in tweens.


# Set up some exception handling and all our views.
def weasyl_404(request):
    userid = d.get_userid()
    return Response(d.errorpage(userid, "**404!** The page you requested could not be found."),
                    status="404 Not Found")


config.add_notfound_view(view=weasyl_404, append_slash=True)
config.add_view(view=mw.weasyl_exception_view, context=Exception, exception_only=True)

setup_routes_and_views(config)


# Setup properties and methods for request objects.
config.add_request_method(mw.pg_connection_request_property, name='pg_connection', reify=True)
config.add_request_method(mw.userid_request_property, name='userid', reify=True)
config.add_request_method(mw.web_input_request_method, name='web_input')
config.add_request_method(mw.set_cookie_on_response)
config.add_request_method(mw.delete_cookie_on_response)


wsgi_app = config.make_wsgi_app()
wsgi_app = mw.InputWrapMiddleware(wsgi_app)
wsgi_app = mw.URLSchemeFixingMiddleware(wsgi_app)
if config_read_bool('profile_responses', section='backend'):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    wsgi_app = ProfilerMiddleware(
        wsgi_app, profile_dir=m.MACRO_STORAGE_ROOT + 'profile-stats')
if config_obj.has_option('sentry', 'dsn'):
    sentry_sdk.init(
        dsn=config_obj.get('sentry', 'dsn'),
        release=d.CURRENT_SHA,
        traces_sample_rate=float(config_obj.get('sentry', 'traces_sample_rate')),
        integrations=[PyramidIntegration()],
        send_default_pii=False,  # can’t be enabled as long as `before_send` doesn’t run for performance tracing!
        before_send=mw.strip_session_cookie,
    )


configure_libweasyl(
    dbsession=d.sessionmaker,
    not_found_exception=HTTPNotFound,
    base_file_path=m.MACRO_STORAGE_ROOT,
    staff_config_dict=staff_config.load(),
    media_link_formatter_callback=format_media_link,
)
