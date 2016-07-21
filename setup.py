from setuptools import setup, find_packages

setup(
   name='wwsync',
   version='2.0',
   author='Matt Bachmann',
   url='https://github.com/Bachmann1234/weight-watchers-sync',
   description='Syncs Weight Watcher food log to Fitbit',
   license='MIT',
   packages=find_packages(),
   install_requires=['requests==2.9.1', 'beautifulsoup4==4.4.1']
)

