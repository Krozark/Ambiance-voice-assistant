import sys
from os import environ


def _get_platform():
    # ANDROID_ARGUMENT and ANDROID_PRIVATE are 2 environment variables
    # from python-for-android project
    platform_android = 'ANDROID_ARGUMENT' in environ
    platform_ios = (environ.get('KIVY_BUILD', '') == 'ios')
    sys_platform = sys.platform

    # On android, _sys_platform return 'linux2', so prefer to check the
    # import of Android module than trying to rely on _sys_platform.

    # pylint: disable=no-else-return
    if platform_android is True:
        return 'android'
    elif platform_ios is True:
        return 'ios'
    elif sys_platform in ('win32', 'cygwin'):
        return 'win'
    elif sys_platform == 'darwin':
        return 'macosx'
    elif sys_platform.startswith('linux'):
        return 'linux'


platform = _get_platform()
