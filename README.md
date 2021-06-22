# Eol Newsletters

![https://github.com/eol-uchile/edx-newsletters/actions](https://github.com/eol-uchile/edx-newsletters/workflows/Python%20application/badge.svg)

# Install App

    docker-compose exec lms pip install -e /openedx/requirements/edx-newsletters
    docker-compose exec lms python manage.py lms --settings=prod.production makemigrations
    docker-compose exec lms python manage.py lms --settings=prod.production migrate

## TESTS
**Prepare tests:**

    > cd .github/
    > docker-compose run lms /openedx/requirements/edx-newsletters/.github/test.sh
