# Sprint 4 - CitiStarter

Developers Practice

### Project Description

My Startup Investment Platform.
View startup reviews or submit your reviews!

#### How to run:
PostgreSQL (can skip if you are not setting up Postgres)

For this project, you’ll need to set up a PostgreSQL database to use with our application. It’s possible to set up PostgreSQL locally on your own computer, but for this project, we’ll use a database hosted by Heroku, an online web hosting service.
```
1. Navigate to https://www.heroku.com/, and create an account if you don’t already have one.
2. On Heroku’s Dashboard, click “New” and choose “Create new app.”
3. Give your app a name, and click “Create app.”
4. On your app’s “Overview” page, click the “Configure Add-ons” button.
5. In the “Add-ons” section of the page, type in and select “Heroku Postgres.”
6. Choose the “Hobby Dev - Free” plan, which will give you access to a free PostgreSQL database that will support up to 10,000 rows of data. Click “Provision.”
7. Now, click the “Heroku Postgres :: Database” link.
8. You should now be on your database’s overview page. Click on “Settings”, and then “View Credentials.” This is the information you’ll need to log into your database. You can access the database via Adminer, filling in the server (the “Host” in the credentials list), your username (the “User”), your password, and the name of the database, all of which you can find on the Heroku credentials page.
```

Navigate to the project directory (follow to run)
```
For Linux/Unix
1. In a terminal window, navigate into your project1 directory.
2. pipenv install --dev
4. pipenv shell
3. export FLASK_APP=application.py
4. export DATABASE_URL=postgres://rzcijvkpwtktqw:2ea6fa4f77dd778c8947073e4f9569c777e1c49e3052e71cdf8bbbe42c3d2bb6@ec2-184-73-249-9.compute-1.amazonaws.com:5432/d5c2s2umi3g0vt
5. flask run
6. Navigate to the URL provided by flask
```


#### Files Included:
Major HTML files in /templates folder
1. index.html -> The 'homepage' of the website. Contains a form to signup. Links to login.html
2. login.html -> Login page. Contains a form to login. Links back to signup.html
3. search.html -> Search page. Contains a form to search via 1) isbn 2) title and 3) author. 
Search results is displayed at the bottom of the page as an ordered list.
4. bookpage.html -> Contains a form for user to submit his review. 
Displays 1) information about a book, 2) goodreads ratings and 3) users reviews. 2) and 3) are displayed at the bottom of the page.
<br><br><br>
5. layout.html -> showcase inheritance method for html
6. success.html -> used with layout.html for logout success
7. error.html -> used with layout.html for logout error. Also used if user types an invalid isbn into URL/bookpage/isbn.
<br><br><br>
8. application.py -> contains the whole logic of the program and all the routes.
9. import.py -> contains the (deletion), creation of 3 tables - users, books, reviews - and importing of books.csv.
<br><br><br>
10. books.csv (no change)
11. requirements.txt (no change)
12. README.md


#### Page access constraints:
For a non-logged in user:
* The user can access index.html and login.html
* Trying to access the other html pages via changing the url will result in abort(403) forbidden access thrown to the user.
* The user can use the api request by typing URL/api/isbn

For a logged in user:
* The user can access all html pages.
    * However, the user cannot signup and login again. A warning tab will be shown at the top of the page if the user tries any of the two actions.
* The user can use the api request by typing URL/api/isbn
* There will be an additional row on each page to signify that the user is loggedin and allow the user to logout.
    * Welcome username | SEARCH (link) | Logout (link)


### Code Description

We store each username in session["this_user"]

\1. Signup

The user needs to sign up to be able to login. At the index page, the user have to key in 3 fields - username, password, reenter password.
Constraints are used to ensure all 3 fields are filled.
* There will be a sql query to SELECT and check if the username exists in the `users` table. 
    * If username exists, signup will fail. 
    * Else, signup will succeed and another sql query will be made to INSERT the username and password into `users`.

\2. Login

The user needs to log in to access important pages like `search` and `bookpage`. At the login page, the user have to key in 2 fields - username and password.
Constraints are used to ensure all 2 fields are filled.
* There will be a sql query to SELECT and check if the username exists in the `users` table. 
    * If username does not exist, login will fail. 
    * Else, another sql query will be made to SELECT and check if password corresponding to the username is correct.
        * If password is correct, login will succeed.
        * Else, login will fail.
* Once the user is loggedin, he will be redirected to the search page via `return redirect(url_for('search'))`  
      
        
\3 Logout

Once the user is logged in, there will be an additional button on each page to allow the user to logout.
When a user is logged out, all the session information of that user will be clear by `session.clear()`
The route to logout is URL/logout. If a non-logged in user tries to go to the route, it will show an error logout message.

\4 Search

There are 3 search terms available. Users can search using 1) isbn, 2) title and 3) author.
The results are shown as an ordered list below the page.
The search terms are case-insensitive, ie title search term "job" will return title "Jobs". 
* If user clicks search without any terms, a message "Please enter at least one search term!" will be shown.
* If user search is valid, an ordered list of books will be shown, each is clickable to its URL/bookpage/isbn.
* If user search has no results, a message "No results found." will be shown.
* Default message when the user is redirected here: "Your search results will be displayed here." 

The sql query for searching is listed below:
```
SELECT * FROM books WHERE (UPPER(isbn) LIKE :isbn AND UPPER(title) LIKE :title AND UPPER(author) LIKE :author)",
            {"isbn": input_isbn, "title": input_title, "author": input_author})
```

\5 Company

##### Review submission constraints
* user must submit both 1-5 integer rating and a text review.
* user cannot review the same company twice
    * if the sql query below has rowcount != 0, the review will be rejected.
     * else, the username, isbn and review will be inserted into `reviews`
```angular2
SELECT * FROM reviews WHERE username = :username AND company_id = :company_id", 
        {"username": session["this_user"], "company_id": company_id}
```


##### Users reviews (reviews from this webpage users)
* rating and rating_count is fetched from the database, default is 0 for both.
    * rating is the average rating and rating_count is the number of ratings.
* An unordered list in the format of //(username) //(text review) //rating/5 will be displayed at the bottom of the page.


\5 api json fetch

Both loggedin and non-loggedin users can use this URL/api/(isbn) to fetch details of the book in json format.
If the isbn is invalid or the book is not found, abort(404) will be shown.


### Possible Improvements

1. Use more of inheritance method for writing html pages.
2. Sanitise user input especially for user text reviews to prevent SQL injections.