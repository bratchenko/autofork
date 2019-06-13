# Autofork

Autofork is a Python & Flask project that uses GitHub API & OAuth to provide
an alternative way to fork its own repostory.  
Designed with simplicity in mind, and as an example of serverless application
suitable for deployment on [ZEIT Now](https://zeit.co/now).

- [Getting started](#getting-started)
  - [Obtaining the code](#obtaining-the-code)
  - [Setup ZEIT Now](#setup-zeit-now)
  - [GitHub OAuth credentials](#github-oauth-credentials)
  - [Configure environment secrets](#configure-environment-secrets)
  - [Deploy with Now](#deploy-with-now)
- [Technical info](#technical-info)
- [Development](#development)
- [Contact](#contact)

## Getting started

### Obtaining the code

1. Use the [live Autofork application](https://autofork.orlovol.now.sh/) or
    fork the [original repository](https://github.com/hey-sancho/autofork) manually.  
    This will make your own copy of the Autofork repository in your GitHub account.
2. [Clone](https://help.github.com/en/articles/cloning-a-repository-from-github)
    the repository to download the code to your local machine.

### Setup ZEIT Now

The simplest way to publish this project is by leveraging serverless solutions.
[Zeit Now](https://zeit.co/now) is a web platform that makes serverless application deployment easy.
It allows to deploy project from local console as well as a
[GitHub CI/CD integration](https://zeit.co/github).

3. [Sign up with GitHub on ZEIT Now](https://zeit.co/github-setup) and follow the instructions.  
    You will be asked to login into your GitHub account and authorize the application to access your info.
4. [Configure Now GitHub application](https://github.com/settings/installations/1105103) by allowing
    `All repositories` access.  
    This allows Now to rebuild your repository on each commit.
5. [Install Now CLI](https://zeit.co/download) on your system.  
    If you're on Mac/Windows, installing **Recommended** package would provide both GUI & CLI apps.

### GitHub OAuth credentials

Since autofork's goal is to create repository forks, it needs credentials to access GitHub.
OAuth allows users to easily login with their account into autofork, while application gains
access to their shared data.

6. Navigate to *Settings - Developer Settings - OAuth Apps - 
    [New OAuth App](https://github.com/settings/applications/new)*  on GitHub.

7. Fill the fields with the following info and click `Register application`:
    - Application Name: `Autofork`
    - Homepage URL: `https://autofork.<now_username>.now.sh`
    - Authorization callback URL: `https://autofork.<now_username>.now.sh/login/authorized`

    Where `now_username` is [Your Username on ZEIT Now](https://zeit.co/account) from step 3.

8. Now you have your own credentials. Note the created `Client ID` & `Client Secret`
    values, and keep them secret.

### Configure environment secrets

Before deploying your own copy of the application, you need to configure it with your credentials.

9. Generate a secret key by running the following command in terminal:
    ```
    python -c 'import os, binascii; print(binascii.hexlify(os.urandom(16)).decode())'
    ```

    Or you can come up with a passphrase of your choice, at least 10-characters long.
    It will be used to securely store cookies used by your application.

10. Run the following commands to add secret keys to your Now account:
    ```
    now secrets add autofork-id <client_id>
    now secrets add autofork-secret <client_secret>
    now secrets add autofork-key <client_key>
    ```
    Where `<client_id>`, `<client_secret>` are your GitHub OAuth credentials from step 8,
    and `<client_key>` is the passphrase from the step 9.

### Deploy with Now

When you're done with all the previous steps, you're ready to deploy your Autofork
copy as a serverless application.

11. Simply run `now` in your project directory.  
    This will build and deploy your application automatically, returning the deployment URLs.

12. **_You're done!_**  
    Visit the link to your application and celebrate :)

**_Note_**: By default, Autofork is configured to fork the original repository.
If you wish to make it fork your own copy, there are two ways to handle this:

1. In `now.json` modify the line `"GITHUB_ORIGIN": <url>` to point to the repository remote URL.
2. Run deployment as `now -e GITHUB_ORIGIN=<url>`  
    Where `<url>` is the clone URL of the GitHub repository.

## Technical info

Autofork is written in Python3.6, and uses these awesome libraries:

1. [Flask](http://flask.pocoo.org/)
    microframework for web applications, that handles http requests.

3. [Flask-Dance](https://flask-dance.readthedocs.io/en/latest/)
    library to perform authorization via GitHub OAuth.

Autofork provides a basic frontend UI that allows user to perform actions needed
to sign in/out and fork the repo.

1. First, user has to **Sign in** with their GitHub account and allow access to public data.  
    This allows Autofork to call the GitHub API to act on the shared data.

2. After sign in, user is presented with two buttons: fork the repo or sign out.  
   The user session is stored in the cookie, which keeps the user logged in.

3. Clicking the **Fork** button will create the repository fork in user's account.

4. Clicking the **Sign out** button will clear the session and revoke GitHub access.  
    To modify or revoke access to their data, user can also check
    [GitHub application settings](https://github.com/settings/applications/).  

In case of runtime errors, user is presented with the page that contains error message,
and mostly technical description.

## Development

If you need to tweak the application code, the easiest way to setup the development
environment with [pipenv](https://docs.pipenv.org/en/latest/).

1. Run `pipenv install` in the project directory to install all needed dependencies
    in a virtual python environment.

2. Use `flask run` to run the local server with the application on http://127.0.0.1:5000/

3. Create `.env` file in your project directory with the used environment variables:
    ```
    SECRET_KEY=<client_key>
    GITHUB_OAUTH_CLIENT_ID=<client_id>
    GITHUB_OAUTH_CLIENT_SECRET=<client_secret>
    GITHUB_ORIGIN=<url>
    # allow app reload on code changes
    FLASK_ENV="development"
    # allow non-https callback URL
    OAUTHLIB_INSECURE_TRANSPORT=1
    ```

4. After pushing your changes to the GitHub, Now will rebuild the code and deploy
    the project automatically.

**_Note_**: To use OAuth locally, you need to change "Authorization callback URL" 
in your credentials to your local server address.


## Contact

If you have questions or encounter any issues, feel free to [open up an issue](https://github.com/hey-sancho/autofork/issues/new).