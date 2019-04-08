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

    def __init__(self, extension):
        super(BlacklistPostRenderHook, self).__init__(extension)
        blacklist_terms = extension.config.get('blacklist', [])

        self.blacklist = []
        for term in blacklist_terms:
            self.blacklist.append({
                'term': term,
                'pattern': re.compile(term, re.IGNORECASE),
            })

    def trigger(self, previous_result, doc, raw_content, *_args, **_kwargs):
        """Execute post-render modification."""
        extensions = tuple(self.extension.config.get('extensions', ['.html',]))
        if not isinstance(doc, document.Document) or not doc.view.endswith(extensions):
            return previous_result

        content = previous_result if previous_result else raw_content
        for term in self.blacklist:
            if term['pattern'].search(content):
                raise BlacklistError('Blacklisted term found in {}: {}'.format(
                    doc.pod_path, term['term']))
        return content


class BlacklistExtension(extensions.BaseExtension):
    """Blacklist extension."""

    @property
    def available_hooks(self):
        """Returns the available hook classes."""
        return [BlacklistPostRenderHook]
