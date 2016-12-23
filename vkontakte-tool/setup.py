#!/usr/bin/env python
# -*- coding: UTF8 -*-

from distutils.core import setup

setup(name='vkontakte-tool',
      version='0.7.1',
      description='Alternative vkontakte.ru client',
      author='Alexey Osipov',
      author_email='simba@lerlan.ru',
      url='https://launchpad.net/vkontakte-tool',
      packages=['vkontakte'],
      py_modules=['vkontaktecli', 'vkontaktegui'],
      license='GPL',
      data_files = [('/usr/share/doc/vkontakte-tool', ['README', 'COPYING']),
                    ('/usr/share/applications', ['links/vkontakte-tool.desktop']),
                    ('/usr/share/pixmaps', ['icons/vkontakte.png', 'icons/vkontakte-64x64.png'])],
      scripts = ['bin/vkontakte-cli', 'bin/vkontakte-gui']
     )
