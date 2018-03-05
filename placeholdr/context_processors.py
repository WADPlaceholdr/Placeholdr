from placeholdr.models import UserProfile
def user(request):
	context_dict={}
	if request.user.is_authenticated():
		# get logged in user object
		user = request.user
		context_dict["user"]=user
		# get logged in userProfile object
		userProfile = UserProfile.objects.get(pk=user.id)
		context_dict["userProfile"]=userProfile
	return context_dict