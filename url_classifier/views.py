from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services.classificar_url import classificar_url

@csrf_exempt
def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        resultados = classificar_url(url)
        return JsonResponse(resultados)

    return render(request, 'home.html')
