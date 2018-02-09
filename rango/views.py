from django.shortcuts import render
from django.http import HttpResponse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

# Import the Category model
from rango.models import Category

# Import the CategoryForm
from rango.forms import CategoryForm

# Import the Page model
from rango.models import Page

# Import the PageForm
from rango.forms import PageForm

def index(request):
    request.session.set_test_cookie()
    # Query the database for a list of ALL categories currently stored
    # Order the categories by number of likes in descending order
    # Retrieve the top 5 only - or all if less than 5
    # Place the list in our context_dict dictionary
    # that will be passed to the template engine
    # Construct a dictionary to pass to the template as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories' : category_list, 'pages' : page_list}

    visitor_cookie_handler(request)

    context_dict['visits'] = request.session['visits']

    # Render the response and send it back!
    response = render(request, 'rango/index.html', context_dict)

    # Return response back to user, updating any cookies that need changed
    return response

def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
        
    visitor_cookie_handler(request)
    context_dict = {'visits' : request.session['visits']}
    
    return render(request, 'rango/about.html', context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception
        # So the .get() method returns one models instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds out results list to te template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the datavase to the context dictionary.
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category
        # Don't do anything -
        # the template will display the "no category" message for us
        context_dict['category'] = None
        context_dict['pages'] = None

    # Go render the response and return it to the client
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved, direct the user back to the index page
            return index(request)
        else:
            # Print the errors to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try :
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)
    
def register(request):
    # Boolean for when registration was successful, false initially,
    # then set to true if successful
    registered = False

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # Attempt to get information from the form
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Hash the password then update the user object
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # Check if there's a profile picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Sve the UserProfile model instance
            profile.save()

            registered = True

        else:

            print(user_form.errors, profile_form.errrors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form':profile_form,
                   'registered': registered})

def user_login(request):
    # If the request is HTTP POST, try to get the relevant information
    if request.method == 'POST':
        # Use request.POST.get('<variable>') instead of .get['<v as
        # it returns None if the value does not exist instead of an error
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if login combination is valid
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct
        if user:
            # Is the account active?
            if user.is_active:
                # If valid and active, log in
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # Inactive account
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details provided
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        # Not a POST so display the login form
        return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    # Since we know they are logged in, we can log them out
    logout(request)
    return HttpResponseRedirect(reverse('index'))

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # If the cookie doesn't exist, the default value of 1 is used
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
        
    # Update/set the visits cookie
    request.session['visits'] = visits
