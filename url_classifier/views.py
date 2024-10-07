# url_classifier/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .services.classificar_url import classificar_url  # Importa o service

def home(request):
    if request.method == 'POST':
        url = request.POST.get('url')  # Pega a URL enviada do frontend
        resultados = classificar_url(url)  # Chama o service para processar a URL
        return JsonResponse(resultados)  # Retorna o resultado da classificação como JSON

    return render(request, 'home.html')  # Renderiza a página inicial se for uma requisição GET
