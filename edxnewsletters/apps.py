from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import (
    PluginSettings,
    PluginURLs,
    ProjectType,
    SettingsType,
)


class EdxNewslettersConfig(AppConfig):
    name = 'edxnewsletters'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: "edxnewsletters-data",
                PluginURLs.REGEX: r"^edxnewsletters/",
                PluginURLs.RELATIVE_PATH: "urls",
            }}
    }
