# grow-ext-blacklist

Simple extension for blacklisting words during builds.

## Usage

### Initial setup

1. Create an `extensions.txt` file within your pod.
1. Add to the file: `git+git://github.com/grow/grow-ext-blacklist`
1. Run `grow install`.
1. Add the following section to `podspec.yaml`:

```
ext:
- extensions.blacklist.BlacklistExtension:
    blacklist:
    - super-size
```

When rendering HTML pages Grow will check for the provided regular expressions in the generated content.

### Extensions

The configuration can also control which files are checked for blacklisted terms. Defaults to only search `.html` files.

For example:

```
ext:
- extensions.blacklist.BlacklistExtension:
    blacklist:
    - super-size
    extensions:
    - .html
    - .js
```
