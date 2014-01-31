# -*- coding: utf-8 -*-
"""Python packaging."""
from os.path import abspath, dirname, join
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


def packages(project_name):
    """Return list of packages distributed by project based on its name.

    >>> packages('foo')
    ['foo']
    >>> packages('foo.bar')
    ['foo', 'foo.bar']
    >>> packages('foo.bar.baz')
    ['foo', 'foo.bar', 'foo.bar.baz']
    >>> packages('FooBar')
    ['foobar']

    Implements "Use a single name" convention described in :pep:`423`.

    """
    name = str(project_name).lower()
    if '.' in name:  # Using namespace packages.
        parts = name.split('.')
        return ['.'.join(parts[0:i]) for i in range(1, len(parts) + 1)]
    else:  # One root package or module.
        return [name]


def namespace_packages(project_name):
    """Return list of namespace packages distributed in this project, based on
    project name.

    >>> namespace_packages('foo')
    []
    >>> namespace_packages('foo.bar')
    ['foo']
    >>> namespace_packages('foo.bar.baz')
    ['foo', 'foo.bar']
    >>> namespace_packages('Foo.BaR.BAZ') == namespace_packages('foo.bar.baz')
    True

    Implements "Use a single name" convention described in :pep:`423`.

    """
    package_list = packages(project_name)
    package_list.pop()  # Ignore last element.
    # Remaining packages are supposed to be namespace packages.
    return package_list


NAME = 'pussycache'
version = read_relative_file('VERSION').strip()
readme = read_relative_file('README.md')
requirements = []

dependency_links = []

entry_points = {
}


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(name=NAME,
          version=version,
          description="""Cache Backend system for python objects""",
          long_description=readme,
          classifiers=['Development Status :: 4 - Beta',
                       'License :: OSI Approved :: BSD License',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 2.6',
                       'Framework :: Django',
                       ],
          keywords='cache',
          author='Novapost Team',
          author_email='peopleask@novapost.fr',
          url='https://github.com/novapost/%s' % NAME,
          license='BSD',
          packages=packages(NAME),
          namespace_packages=namespace_packages(NAME),
          include_package_data=True,
          zip_safe=False,
          install_requires=requirements,
          dependency_links=dependency_links,
          entry_points=entry_points,
          test_suite='nose.collector',
          setup_requires=['nose'],
          tests_require=['redis', 'django'])
