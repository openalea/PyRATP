from setuptools import setup, find_packages

setup(
    name="PyRATP",
    version="1.0.0",
    description="The Alinea.PyRATP package is a typical package example to help developper to create their own package, compatible with OpenAlea standards.",

    # package installation
    packages= find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['alinea'],
    zip_safe= False,
    include_package_data = True,
    package_data = {'' : ['*.pyd', '*.so'],},

    # Declare scripts and wralea as entry_points (extensions) of your package
    entry_points = {'wralea' : ['pyratp = alinea.pyratp_wralea',] }
)




## LAST VERSION OF SETUP.PY
#
# # -*- coding: utf-8 -*-
# __revision__ = "$Id: $"

# import sys
# import os

# from setuptools import setup, find_packages
# from openalea.deploy.metainfo import read_metainfo

# pj = os.path.join

# # Reads the metainfo file
# metadata = read_metainfo('metainfo.ini', verbose=True)
# for key,value in metadata.iteritems():
#     exec("%s = '%s'" % (key, value))

# # Packages list, namespace and root directory of packages

# pkgs = find_packages('src')

# # Define global variables
# build_prefix = "build-scons"

# # dependencies to other eggs
# setup_requires = ['openalea.deploy']
# install_requires=[]

# # web sites where to find eggs
# dependency_links = ['http://openalea.gforge.inria.fr/pi']

# setup(
#     name=name,
#     version=version,
#     description=description,
#     long_description=long_description,
#     author=authors,
#     author_email=authors_email,
#     url=url,
#     license=license,
#     keywords = '',

#     # package installation
#     packages= pkgs,
#     package_dir={'': 'src'},
#     namespace_packages=['alinea'],

#     # Namespace packages creation by deploy
#     #namespace_packages = [namespace],
#     #create_namespaces = False,
#     zip_safe= False,

#     # Dependencies
#     setup_requires = setup_requires,
#     install_requires = install_requires,
#     dependency_links = dependency_links,


#     # Binary installation (if necessary)
#     # Define what to execute with scons
#     scons_scripts=['SConstruct'],
#     scons_parameters=["build_prefix="+build_prefix],

#     # Eventually include data in your package
#     # (flowing is to include all versioned files other than .py)
#     include_package_data = True,
#     # (you can provide an exclusion dictionary named exclude_package_data to remove parasites).
#     # alternatively to global inclusion, list the file to include
#     package_data = {'' : ['*.pyd', '*.so'],},

#     # postinstall_scripts = ['',],

#     # Declare scripts and wralea as entry_points (extensions) of your package
#     entry_points = {
#         'wralea' : ['pyratp = alinea.pyratp_wralea'],
#         },
#     )


