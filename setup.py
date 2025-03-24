from setuptools import find_packages
from setuptools import setup

long_description = '\n\n'.join(
    [
        open('README.rst').read(),
        open('CHANGES.rst').read(),
    ]
)


setup(
    # zest.releaser needs version here for now
    name="collective.coursetool",
    version="2.0.0a1.dev0",
    description="Manage Courses, Lecturers, Students, Exams, Certificates",
    long_description=long_description,
    keywords="Plone, Course Management",
    author="Peter Mathis",
    author_email="peter.mathis@kombinat.at",
    maintainer="Kombinat Media Gestalter GmbH",
    maintainer_email="office@kombinat.at",
    url="https://github.com/kombinat/collective.coursetool.git",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone :: 6.1",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.11",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        "bda.plone.shop",
        "bda.plone.stripe",
        "dateparser",
        "collective.address",
        "collective.z3cform.datagridfield >= 3.0.0.dev0",
        "Products.membrane >= 6.0.0.dev0",
        "dexterity.membrane >= 3.0.0",
        "openpyxl",
        "reportlab",
        "pypdf",
        "pdf2image",
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale_fvv_theme = plonetheme.fvv.locales.update:update_locale
    """,
)
