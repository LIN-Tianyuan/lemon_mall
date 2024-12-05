from django.shortcuts import render
from django.views import View
# Create your views here.

class IndexView(View):
    """Home Advertisement"""
    def get(self, request):
        """Provide homepage advertisement page"""
        return render(request, 'index.html')
