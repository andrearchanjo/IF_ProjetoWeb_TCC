import requests
import tldextract
import socket
import whois
from urllib.parse import urlparse
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from .helpers import get_model_name


def is_ip_privado(ip):
    try:
        return socket.inet_aton(ip) in [socket.inet_aton('10.0.0.0'), socket.inet_aton('172.16.0.0'),
                                        socket.inet_aton('192.168.0.0')]
    except socket.error:
        return False


def extrair_url_ip_features(url_info):
    subdomains = tldextract.extract(url_info['url']).subdomain
    url_info['num_subdomains'] = subdomains.count('.') + 1 if subdomains else 0

    url_info['ip_length'] = len(url_info['ip_add'])

    url_info['is_private_ip'] = 1 if is_ip_privado(url_info['ip_add']) else 0

    return url_info


def get_url_info(url):
    print(f"Obtendo informações da URL: {url}")
    url_info = {}
    url_info['url'] = url

    url_info['url_len'] = len(url)

    parsed_url = urlparse(url)
    tld_info = tldextract.extract(url)
    url_info['tld'] = tld_info.suffix

    url_info['https'] = 'yes' if parsed_url.scheme == 'https' else 'no'

    try:
        domain = parsed_url.netloc
        ip_address = socket.gethostbyname(domain)
        url_info['ip_add'] = ip_address
        print(f"Endereço IP obtido: {ip_address}")
    except socket.gaierror:
        url_info['ip_add'] = ''
        print("Erro ao obter endereço IP")

    if not url_info['ip_add']:
        raise ValueError("Erro: Não foi possível classificar a URL, pois o endereço IP não pôde ser acessado.")

    try:
        whois_info = whois.whois(url)
        if len(str(whois_info.registrar)) > 1:
            url_info['who_is'] = 'complete'
        else:
            url_info['who_is'] = 'incomplete'
        print(f"Informações WHOIS: {url_info['who_is']}")
    except Exception as e:
        url_info['who_is'] = 'incomplete'
        print(f"Erro ao obter informações WHOIS: {e}")

    try:
        response = requests.get(f"http://ip-api.com/json/{url_info['ip_add']}")
        geo_info = response.json()
        if geo_info['status'] == 'success':
            url_info['geo_loc'] = geo_info['country']
            print(f"Localização geográfica obtida: {url_info['geo_loc']}")
        else:
            url_info['geo_loc'] = ''
    except Exception as e:
        url_info['geo_loc'] = ''
        print(f"Erro ao obter geolocalização: {e}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            js_files = [script for script in response.text.splitlines() if '<script' in script]
            js_size = sum([len(script) for script in js_files])
            url_info['js_len'] = js_size
        else:
            url_info['js_len'] = 0
        print(f"Tamanho dos scripts JS: {url_info['js_len']}")
    except Exception as e:
        url_info['js_len'] = 0
        print(f"Erro ao obter scripts JS: {e}")

    url_info = extrair_url_ip_features(url_info)

    return url_info


def pre_processar_url(url):
    print(f"Pré-processando a URL: {url}")
    info = get_url_info(url)

    label_encoder = LabelEncoder()

    info['geo_loc'] = label_encoder.fit_transform([info['geo_loc']])[0]
    info['tld'] = label_encoder.fit_transform([info['tld']])[0]

    info['https'] = 1 if info['https'] == 'yes' else 0
    info['who_is'] = 1 if info['who_is'] == 'complete' else 0

    features = [
        info['url_len'],
        info['geo_loc'],
        info['tld'],
        info['who_is'],
        info['https'],
        info['js_len'],
        info['num_subdomains'],
        info['ip_length'],
        info['is_private_ip'],
    ]

    print(f"Características extraídas: {features}")
    return pd.DataFrame([features], columns=['url_len', 'geo_loc', 'tld', 'who_is', 'https', 'js_len', 'num_subdomains',
                                             'ip_length', 'is_private_ip'])


def carregar_modelos():
    print("Carregando modelos de machine learning...")
    modelos = {}
    try:
        modelos['DecisionTree'] = joblib.load("modelos_treinados/DecisionTreeClassifier.joblib")
        print("Modelo DecisionTree carregado.")
    except Exception as e:
        print(f"Erro ao carregar DecisionTree: {e}")

    try:
        modelos['RandomForest'] = joblib.load("modelos_treinados/RandomForestClassifier.joblib")
        print("Modelo RandomForest carregado.")
    except Exception as e:
        print(f"Erro ao carregar RandomForest: {e}")

    try:
        modelos['LogisticRegression'] = joblib.load("modelos_treinados/LogisticRegression.joblib")
        print("Modelo LogisticRegression carregado.")
    except Exception as e:
        print(f"Erro ao carregar LogisticRegression: {e}")

    try:
        modelos['SVC_linear'] = joblib.load("modelos_treinados/SVC_linear.joblib")
        print("Modelo SVC Linear carregado.")
    except Exception as e:
        print(f"Erro ao carregar SVC Linear: {e}")

    try:
        modelos['SVC_rbf'] = joblib.load("modelos_treinados/SVC_rbf.joblib")
        print("Modelo SVC RBF carregado.")
    except Exception as e:
        print(f"Erro ao carregar SVC RBF: {e}")

    return modelos


def classificar_url(url):
    try:
        X = pre_processar_url(url)
    except ValueError as e:
        print(f"Erro ao pré-processar a URL: {e}")
        return str(e)

    try:
        scaler = joblib.load('modelos_treinados/scaler.joblib')
        X_values = scaler.transform(X)
        print(f"Valores escalados: {X_values}")
    except Exception as e:
        print(f"Erro ao carregar o scaler ou transformar os dados: {e}")
        return str(e)

    modelos = carregar_modelos()

    resultados = {}
    for nome_modelo, modelo in modelos.items():
        try:
            kernel = 'rbf' if 'rbf' in nome_modelo else 'linear' if 'linear' in nome_modelo else None
            modelo_formatado = get_model_name(modelo, kernel=kernel)
            predicao = modelo.predict(X_values)
            resultado = 'Maligna' if predicao[0] == 1 else 'Benigna'
            resultados[modelo_formatado] = resultado
            print(f"Classificação com {modelo_formatado}: {resultado}")
        except Exception as e:
            print(f"Erro ao classificar com {nome_modelo}: {e}")

    return resultados
