#!/bin/dash
pip install -e /openedx/requirements/edx-newsletters

cd /openedx/requirements/edx-newsletters
cp /openedx/edx-platform/setup.cfg .
mkdir test_root
cd test_root/
ln -s /openedx/staticfiles .

cd /openedx/requirements/edx-newsletters

DJANGO_SETTINGS_MODULE=lms.envs.test EDXAPP_TEST_MONGO_HOST=mongodb pytest edxnewsletters/tests.py