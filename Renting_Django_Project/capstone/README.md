# RENTAL

By Anton Horakh

Video overview: https://youtu.be/47ZaDRY3vpQ

## Distinctiveness and Complexity

### General Description 
Project represents a web application which provide to users functionality to create and post ads on rent real property.
Main(index) page shows all active ads of other's users. User's own ads has different background color.
User can create ad by filling the form on the "create" page.
User can sort and filter ads.
Other's users ads has buttons to save ad. 
User can open ad (ad opens dynamically using JS without loading new page) to see full description and, for logged user, contact form.
User can start dialog with author of the ad just by sending message via contact form. User cannot start dialog with himself.
All logged users have access to the profile page, which contains dynamically loaded sections:
"My data", "My ads", "Saved ads", "Dialogs". Profile page also has "Refresh" button to dynamically update(reload) content.
"My ads" section lists all user's ads with buttons to edit or activate/archive ad. Not active(archived) ads are not show on the main page.
"Saved ads" section lists all ads saved by users. There are button for each to remove from the saved list.
"Dialogs" section show all user's dialogs with other users. There are shown last messages for each dialog. If there is a dialog 
which contains unread message it would be marked "New message!". User can open dialog, which would be dynamically loaded, to see
all messages and new message form. Also there is a button "update" to check and load new messages.

### Distinctiveness
While project uses some features common to other projects like pagination, list of saved ads, 
register/log-in pages, I have implemented many complex features which I haven't used in other projects:

    - Sorting on main page allows to sort ads in a chosen order: newest first, price - high to low, low to high.
    - Filtering on main page allows to filter ads by city, price, number of rooms, presents of furniture.
    (Both sorting and filters work together without problem and also work with paggination feature as expected).
    (Also show/hide animation by means of CSS was implemented for the filter block).
    - Dynamic history - main(index) page and profile page are dynamic single-pages with sections which could be opened dynamically,
        so dynamic browser history by means of JS was implemented. Also every section could be opened by url directly.
    - Dialogs - user can start a dialog with owner of the ad by using a contact form and continue dialog at the dialog section on the profile page.
        New messages are marked. Also there is a counter span near the "Dialogs" section button is shown when there is new messages.
    - Dynamically loaded list of options for a city input in the filter and on the created/edit page which is implemented by JS 
        fetch function which makes request to the "Cities and Countries" API. By default I chose US cities, but it can be easily changed. 
    - Files - user loads image as a file in the form, not providing an image url.
    - Mobile responsive design - different CSS style applied on page depend on width of screen (more than/equal to 600px or less).
    - Optional input field at creation page. If user uncheck "Available now" user should choose date (not earlier than current), otherwise 
        error message will be shown. Done by implementing custom clean method in forms.py
    - regex format validation of the phone number for registration form (both on html page and in view function).

## What’s contained in the created/modified files.
### Rental app files (in "rental" directory):
    models.py - contains 4 models: User, Ad, Dialog, Message + custom validator function.
    forms.py - contains forms NewAd, NewMessage.
    urls.py - all urls for app + last line for serving media files (MEDIA_URL)
    views.py - contains 20+ functions. Most functions I provided with docstring explaining function purpose.
    admin.py - registered all models.
    static/rental/
            index.js - JS code for index.html page.
            profile.js - JS code for profile.html page.
            layout.js - JS code, where getCookie and getCities function are implemented.
            styles.scss - styles for all pages.
            styles.css.map and styles.css were created automatically by command ssac styles.scss:styles.css.
    templates/rental/
            layout.html - template to be used with all pages. Added here meta tag with the name viewport.
            index.html - main page of application. Dynamic page. It also includes: 
                filter.html and pagination.html. Contains several blocks (all ads, ad page, filter) dynamically 
                    showing and hiding on JS logic.
            profile.html - requires authorization. Dynamic page. Contains blocks with info about user, list of 
                user's ads, list of ads saved by user, dialogs with other users, form to send message in dialog.
            create.html - page where user can create or edit his ad. Includes JS code in script block to get list of cities.
            pagination.html and filter.html were created to separate them from index.html for convenience purposes.
            login.html, register.html - contains forms to login and register.
### MODIFIED standard files:
        capstone/settings.py
            Added line "LOGIN_URL = 'login'" to ensure redirect to login page if required.
            Added app "rental" to INSTALLED.
            Registered user model. Line: AUTH_USER_MODEL = "rental.User"
        capstone/urls.py
            Added urls of rental app.

## How to run application.
I wrote this project using:
    Python 3.10.11,
    Django version 5.0.1,
    pillow 10.3.0 - to upload images.
Before initial run execute commands:
    python manage.py makemigrations,
    python manage.py migrate

## Additional information
Doing this project I tried to write clean documented code in consistence with PEP8 (for python),
avoid code repetitions by writing separated functions, paid attention for security aspects like not
allow users to modified ads of other users, manage possible cases when user can 
submit not valid data by implementing backend logic in views.py functions, clean methods in forms.py and validators in models.py.
