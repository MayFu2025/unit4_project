# Project Unit 4: Reddit Clone
## Brief Description of Task
1. A login/registration system, hashed of course.
2. A posting system to EDIT/CREATE/DELETE comments.
3. A system to add/remove likes.
4. A system to follow/unfollow users, follow/unfollow topics or groups.
5. A profile page with relevant information
6. [HLs] upload images
7. [HL++] send emails *(Did not do)*

## Criteria C: Development
### Techniques Used
- If/Else statements
- For loops
- Endpoints, HTTP methods such as GET, POST (Flask)
- Databases (SQLite)
- Codeblocks and extend (Jinja2)
- Functions
- Input validation
- Classes and methods
- Hashing
- File Input and Output

### Modules and Libraries Used
- flask
- sqlite3
- os
- string
- datetime
- random
- hashlib

### Other tools and frameworks
- ChatGPT was used to reduce the time spent on populating the database with some examples content such as posts and category descriptions. An example is below:

![](assets_for_md/chatgpt_example.png)
**Fig. 1** *Example of ChatGPT being used to generate a description for a category*

- Cirrus was used as a CSS framework for the product. Using a CSS framework allows for more consistency in the design of the product, increasing the usability of the product. 

### Development
#### Use of `{% block content %}` and `{% extends 'base.html' %}` in Jinja2
The use of `{% block content %}` and `{% extends 'base.html' %}` in Jinja2 allows for variables created in other html files to be used in the base template file. This is useful as it reduces repetition by allowing for some html code to be reused in several pages.

When creating a navigation menu that was intended to be used on multiple pages, I initially had the same html code for the navigation bar on each template. Hence, to reduce redundant code, I used this technique so that the html for the navigation bar only needed to be written once.

Below is the code for the navigation bar in the file `navbar.html` (in this case, commonly referred to as the base template):
```html
<!doctype html>
<html lang="en">
<head>
    OMMITTED FOR DEMONSTRATION
    <title>{% block title %}{% endblock %}</title>  # page title that will be defined in the child template
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/cirrus-ui/dist/cirrus.min.css">  #Cirrus CSS framework
    <link rel="stylesheet" href="/style.css">  #Custom CSS
</head>
<body>
    <div id="navbar" class="w-20p">  # div tag that contains the navigation bar
        <div id="navbar-top">
            <h3>Navigate:</h3>
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('all_categories') }}">All Categories</a>
            
            <h4>Following Clubs:</h4>
            {% for cat_id in categories[0] %}
                <a href="{{ url_for('get_category', cat_id=cat_id) }}">{{ categories[1][loop.index0] }}</a>
            {% endfor %}
        </div>
        <div id="navbar-bottom">
            <a href="{{ url_for('get_profile', user_id=user_id) }}">Profile</a>
            <br>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    <div id="website" class="w-80p">  # div tag that contains the rest of the content
        {% block content %}{% endblock %}  # content that will be defined in the child template
    </div>
</body>
</html>
```
In the header, I define the title of the given page. Considering that this is the base template in which other html pages will add onto, I use `{% block title %}` so that the title given to each page extending on the base template can be cutomized. The content that represents `{% block title %}` can be defined in the child template by placing the content between the `{% block title %}` and `{% endblock %}` tags. The same thing is done within the `body` tag, where after the program for the navigation bar, I use `{% block content %}` which describes the rest of the content that should go into the body of the page. By assigning the CSS classes `w-20p` and `w-80p` from Cirrus to a `div` that contains the navigation bar and the content block respectively, I define the width of the navigation bar and the content. This is done as the intention is that the navigation bar should always be shown on a portion of the left hand side of the screen (20%) and the webpage contents are displayed on the remaining 80% of the screen. Furthermore, each of the `div` tags are given the ids `navbar` and `website` respectively, so that their position on the screen can be adjusted in the stylesheet `style.css` linked in the header.

Below is the CSS specified in the `style.css` file to make this work:
```css
#navbar {
    height: 100%;
    position: fixed;
    left: 0;
}

#website {
    position: absolute;
    left:20%;
}
```
The attribute `position: fixed` given to `navbar` allow for the navigation bar to be fixed on the left hand side of the screen by specifying the attribute `left: 0`. The attribute `fixed` also ensures that the navigation bar remains in the same position at all times, including when the user may scroll down the page content.

The `position: absolute` attribute given to `website` in combination with the `left: 20%` attribute specifies that the content should be displayed 20% from the left hand side of the screen. This is done so the content is displayed on the immediate right hand side of the navigation bar.

In combination with the child file, this effectively allows for the navigation bar to be displayed on the left with varying content on the right. The child template is linked to the base template by using `{% extends 'base.html' %}`.

Below is a portion of the file `home.html` which is an example of a child template that extends the base template in my program:
```html
{% extends "navbar.html" %}  # extends the base template

{% block title %}Homepage{% endblock %}  # title of the page

{% block content %}  # content of the page
        <h2>Welcome to the CLUBHOUSE, {{ user[1] }}!</h2>
        <h3><em>Where ISAKers talk all things clubs and activities.</em></h3>

        OMMITTED FOR DEMONSTRATION

{% endblock %}
```
The `{% extends "navbar.html" %}` links the blocks defined in this page to the blocks of the same name in `navbar.html`. For example, this page defines "Homepage" as the content to be passed for `{% block content %}`. Similarly, the content of the page is placed between the `{% block content %}` and `{% endblock %}` tags.

The end result looks like this:
![](assets_for_md/navbar_example.png)
*Fig.2* **Example of the navigation bar on the home page through the use of block content and extend**

#### Use of Jinja operators and expressions to create dynamic content 
In making the product, I pass variables from Python code in `app.py` when rendering HTML templates to create dynamic content customized to the user. For example, in 


## Criteria D: Functionality
### Video Demonstration of Product

## Criteria E: Evaluation
### Self-evaluation

### Client Feedback

### Advisor Feedback

### Summary of Strengths, Weaknesses, and Future Improvements