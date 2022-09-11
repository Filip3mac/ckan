
from __future__ import annotations

from ckan.common import CKANConfig

import ckan.plugins as p
import ckan.plugins.toolkit as tk


class TrackingPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ISignal)
    p.implements(p.IMiddleware, inherit=True)

    # IConfigurer
    def update_config(self, config: CKANConfig):
        tk.add_template_directory(config, "templates")
        tk.add_resource("assets", "ckanext-tracking")

    # ISignal
    def get_signal_subscriptions(self):
        return {}

    # IMiddleware
    def make_middleware(self, app, config):
        from .middleware import TrackingMiddleware
        return TrackingMiddleware(app, config)
