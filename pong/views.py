from django.shortcuts import render

def index(request):
	return render(request, 'pong/html/index.html')