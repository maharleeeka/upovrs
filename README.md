# University of the Philippines Online Venue Reservation System (UPOVRS)

The aim of this project is to give a convenient way for organizations (within the university) to process their reservations and easier management for the offices involved in the reservation process.

### Requirements
    - Python 3
    - Postgres (database)
    - Django
    - virtualenvwrapper


### Developement Setup

1. Install Python3 (if you don't have it) via Homebrew in MacOs or apt-get in Ubuntu.
2. Setup project environment with `virtualenv`. You can follow these intallation guide [here](https://askubuntu.com/a/244642).
3. Now add environment variables to your shell startup file (.zshrc or .bashrc) and activate the `virtualenvwrapper`.
    ```
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/Devel
    source /usr/local/bin/virtualenvwrapper.sh
    ```

4. Install and run [PostgreSQL](https://www.postgresql.org/download/).
    Ubuntu/Debian:
    ```
    sudo apt-get install postgresql postgresql-contrib
    ```

    Enter `psql` mode by:
    ```
    sudo -u postgres psql
    ```
    Then create database and grant privileges to the created user. Let's have `upovrs` as sample database name and `personnel` as user.
    ```
    CREATE DATABASE upovrs;
    CREATE USER personnel WITH PASSWORD 'upovrs';
    GRANT ALL PRIVILEGES ON DATABASE upovrs TO personnel;
    ```
5. Clone the `upovrs` project.
6. Activate the project's `virtualenv` and run this command to install the initial package requirements:
```
pip install -r <path_to_requirements.txt>
```
7. Import the database models.
```
python manage.py migrate
```
8. Now you're ready to go. Give the project a little nudge and then check your `localhost`.
```
python manage.py runserver
```
