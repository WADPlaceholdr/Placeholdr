from placeholdr.models import UserProfile
from datetime import datetime

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

def user(request):
	context_dict={}
	if request.user.is_authenticated():
		# get logged in user object
		user = request.user
		context_dict["loggedUser"]=user
		# get logged in userProfile object
		userProfile = UserProfile.objects.get(pk=user.id)
		context_dict["userProfile"]=userProfile
	visitor_cookie_handler(request)
	context_dict["visits"]=request.session['visits']
	return context_dict