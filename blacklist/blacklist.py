"""Blacklist extension for restricting building with blacklisted words in Grow."""

import re
from grow import extensions
from grow.extensions import hooks
from grow.documents import document


class Error(Exception):
    """General blacklist error."""
    pass


class BlacklistError(Error):
    """Blacklist word found in build."""
    pass


class BlacklistPostRenderHook(hooks.PostRenderHook):
    """Handle the post-render hook."""

    def trigger(self, previous_result, doc, raw_content, *_args, **_kwargs):
        """Execute post-render modification."""
        extensions = tuple(self.extension.config.get('extensions', ['.html',]))
        if not isinstance(doc, document.Document) or not doc.view.endswith(extensions):
            return previous_result

        content = previous_result if previous_result else raw_content
        for term in self.extension.blacklist:
            if term['pattern'].search(content):
                raise BlacklistError('Blacklisted term found in {}: {}'.format(
                    doc.pod_path, term['term']))
        return content


class BlacklistExtension(extensions.BaseExtension):
    """Blacklist extension."""

    def __init__(self, pod, config):
        self._config = None
        super(BlacklistExtension, self).__init__(pod, config)

    @property
    def config(self):
        """Extension configuration."""
        return self._config

    @config.setter
    def config(self, config):
        """Set the extension configuration."""
        self._config = config
        blacklist_terms = config.get('blacklist', [])
        self.blacklist = []
        for term in blacklist_terms:
            self.blacklist.append({
                'term': term,
                'pattern': re.compile(term, re.IGNORECASE),
            })

    @property
    def available_hooks(self):
        """Returns the available hook classes."""
        return [BlacklistPostRenderHook]
