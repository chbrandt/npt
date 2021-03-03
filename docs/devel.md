# Version number

npt version number is directly related to Git tags (last _tag_ -> current _version_).

The process of keeping tag/version sync'd may be done manually or with help from some tool.
For instance, there are two libraries in Python of very good quality:

* [versioneer](https://pypi.org/project/versioneer/)
* [dunamai](https://pypi.org/project/dunamai/)

Versioneer integrates neatly to your (Python) code repository, giving your software always a
notion of version -- under your repo/source code, or when released/installed. To accomplish
that you have to install versioneer into your source code, which will effectively
add file/configs to your repository; It works smooth with Git repositories (at least).
Once the install is done, though, you can forget versioneer, it will handle versions on its
own based on your repo tags.

Dunamai is basically an interface to read tags from different SCM (git, svn, etc) and then
printing it out in accordance to [PEP440](https://www.python.org/dev/peps/pep-0440/).
It can be somehow integrated with setup.{py|cfg} scripts, but it does not provide the
dynamics of versioneer.

I am used to versioneer, but currently I'm experimenting with dunamai; I'm taking a more
manual approach with dunamai.


## How to tag and version this repo

When versioning a release, pre-release, release-candidate in this repo we use the classic
three numbers `X.Y.Z` (_major_`.`_minor_`.`_fix_) **preceeded** by a '`v`' (e.g, `v0.1`).

Once the repository is in a release state, a tag is first added to the current HEAD/commit,
then `npt/__version__.py` is updated with the current version/tag (without '`v`') and
then a new commit -- just with the version modification -- is done and pushed.

For example,
```bash
$ git tag -m "v0.0.1" v0.0.1
$ dunamai from git | tee npt/__version__.py
$ git add npt/__version__.py
$ git commit -m "Update version"
```


# Tests

Run the tests with [Pytest](pytest.org):
```
% cd /path/to/npt/
% pip install -e .
% pytest tests/
```
