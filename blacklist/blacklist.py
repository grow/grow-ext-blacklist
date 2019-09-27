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


class BlacklistPreDeployHook(hooks.PreDeployHook):
    """Handle the pre deplow hook."""

    def trigger(self, previous_result, rendered_doc, command, *_args, **_kwargs):
        """Execute pre deploy validation."""
        if not self.extension.blacklist:
            return previous_result
        commands = tuple(self.extension.config.get('commands', ['build', 'deploy', 'stage',]))
        extensions = tuple(self.extension.config.get('extensions', ['.html',]))
        if command not in commands or not rendered_doc.path.endswith(extensions):
            return previous_result

        content = rendered_doc.read()
        for term in self.extension.blacklist:
            if term['pattern'].search(content):
                raise BlacklistError('Blacklisted term found in {}: {}'.format(
                    rendered_doc.path, term['term']))
        return previous_result


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
        return [BlacklistPreDeployHook]
