"""Blacklist extension for restricting building with blacklisted words in Grow."""

import re
from grow import extensions
from grow.extensions import hooks
from grow.documents import document


SNIPPET_SIZE = 60


class Error(Exception):
    """General blacklist error."""
    pass


class BlacklistError(Error):
    """Blacklist word found in build."""
    pass


class BlacklistPreDeployHook(hooks.PreDeployHook):
    """Handle the pre deplow hook."""

    @staticmethod
    def _term_list_snippets(term_list, content):
        snippets = []
        for term in term_list:
            search_result = term['pattern'].search(content)
            if search_result:
                snippet_start = max(0, search_result.start(0) - SNIPPET_SIZE)
                snippet_end = min(
                    len(search_result.string), search_result.end(0) + SNIPPET_SIZE)
                snippet = search_result.string[snippet_start:snippet_end]
                snippets.append({
                    'term': term['term'],
                    'pattern': term['pattern'],
                    'snippet': snippet,
                })
        return snippets

    def trigger(self, previous_result, rendered_doc, command, *_args, **_kwargs):
        """Execute pre deploy validation."""
        if not self.extension.blacklist:
            return previous_result
        commands = tuple(self.extension.config.get(
            'commands', ['build', 'deploy', 'stage', ]))
        raise_error = self.extension.config.get('raise_error', True)
        extensions = tuple(self.extension.config.get(
            'extensions', ['.html', ]))
        if command not in commands or not rendered_doc.path.endswith(extensions):
            return previous_result

        content = rendered_doc.read()

        # Test for blacklist violation.
        results = self._term_list_snippets(self.extension.blacklist, content)
        if results:
            if raise_error:
                raise BlacklistError(
                    'Blacklisted term ({term}) found in {path}: \n{snippet}'.format(
                        path=rendered_doc.path, term=results[0]['term'], snippet=results[0]['snippet']))

            # Log the warnings when not raising errors.
            for result in results:
                self.pod.logger.warning('Blacklist warning term ({term}) found in {path}: \n{snippet}'.format(
                    path=rendered_doc.path, term=result['term'], snippet=result['snippet']))

        return previous_result


class BlacklistExtension(extensions.BaseExtension):
    """Blacklist extension."""

    def __init__(self, pod, config):
        self._config = None
        super(BlacklistExtension, self).__init__(pod, config)

    @staticmethod
    def _parse_config_patterns(patterns):
        terms = []
        for term in patterns:
            terms.append({
                'term': term,
                'pattern': re.compile(term, re.IGNORECASE),
            })
        return terms

    @property
    def config(self):
        """Extension configuration."""
        return self._config

    @config.setter
    def config(self, config):
        """Set the extension configuration."""
        self._config = config
        blacklist_terms = config.get('blacklist', [])
        self.blacklist = self._parse_config_patterns(blacklist_terms)

    @property
    def available_hooks(self):
        """Returns the available hook classes."""
        return [BlacklistPreDeployHook]
