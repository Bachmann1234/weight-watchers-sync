from setuptools import setup, find_packages

setup(
   name='wwsync',
   version='1.0',
   author='Matt Bachmann',
   url='https://github.com/Bachmann1234/weight-watchers-sync',
   description='Syncs Weight Watcher food log to Fitbit',
   license='MIT',
   packages=find_packages(),
   install_requires=['requests==2.9.1']
)

