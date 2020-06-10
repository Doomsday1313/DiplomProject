from django.shortcuts import render

import requests
from django.http import HttpResponse, HttpResponseBadRequest
import json
from .models import History, Criteria
from os import path

def index(request):
    return render(request, 'myapp/index.html', {})


def search(request):
    inn = request.GET['inn']

    if len(inn) != 10 and len(inn) != 12:
        return HttpResponseBadRequest('Введите корректный ИНН')

    card = json.loads(requests.post('https://zachestnyibiznesapi.ru/paid/data/card',
                           data={'id': inn, 'api_key': 'HUgm966fLob0QOq-kpbKA2RaKGEj3a0x'}).text)

    criteria = json.loads(requests.post('https://www.testfirm.ru/api/',
                           data={'key': '420d63a7d4769d014e16e7b0570c42bb', 'method': 'getOrganization', 'inn': inn},
                           headers={'Content-type': 'application/x-www-form-urlencoded'}).text)

    if not card['status'] == '200':
        return HttpResponseBadRequest('Организация с данным ИНН не найдена')

    card = card['body']['docs'][0]

    if not criteria['data']:
        criteria = 'no info'
    else:
        criteria = criteria['data']['details']

    result = {'org': {'info': {'type': [card['ТипДокумента'], 'Тип'], 'name': [card['НаимЮЛПолн'], 'Название'], 'found_date': [card['ОбрДата'], 'Дата открытия'],
              'address': [card['Адрес'], 'Адрес'], 'index': [card['Индекс'], 'Индекс'], 'status': [card['Активность'], 'Статус']},
              'addinfo': {'inn': [card['ИНН'], 'ИНН'], 'ogrn': [card['ОГРН'], 'ОГРН'], 'ogrn_date': [card['ДатаОГРН'], 'Дата присвоения ОГРН'],
              'kpp': [card['КПП'], 'КПП'], 'okato': [card['ОКАТО'], 'ОКАТО'], 'oktmo': [card['ОКТМО'], 'ОКТМО'],
              'okved_code': [card['КодОКВЭД'], 'Код ОКВЭД'], 'okved': [card['НаимОКВЭД'], 'ОКВЭД'], 'okpo': [card['ОКПО'], 'ОКПО'],
              'opf_code': [card['КодОПФ'], 'Код ОПФ'], 'opf': [card['ПолнНаимОПФ'], 'ОПФ'], 'capital': [card['СумКап'], 'Сумма уставного капитала'],
              'tax_type': [card['НалогРежим'], 'Налоговый режим'], 'workers': [card['ЧислСотруд'], 'Количество сотрудников']},
              'fininfo': {'2015': list(card['ФО2015'].values()), '2016': list(card['ФО2016'].values()), '2017': list(card['ФО2017'].values()), '2018': list(card['ФО2018'].values())},
              'criteria': criteria}}

    if request.user.is_authenticated:
        filepath = path.join(path.dirname(path.abspath(__file__)), 'history/' + inn + '.json')
        with open(filepath, 'w+') as f:
            f.write(json.dumps(result['org']))
            f.close()

        if not History.objects.filter(user=request.user, inn=result['org']['addinfo']['inn'][0]).exists():
            h = History()
            h.name = result['org']['info']['name'][0]
            h.inn = result['org']['addinfo']['inn'][0]
            h.user = request.user
            h.datafile = filepath
            h.save()

    return render(request, 'myapp/resultTable.html', result)


def register(request):
    if len(request.POST) == 0:
        return render(request, 'myapp/register.html', {})
    else:
        from django.contrib.auth.models import User
        from django.contrib.auth import login

        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except Exception:
            return HttpResponseBadRequest('Не удалось зарегистрировать пользователя. Возможно пользователь с данным именем или почтой уже зарегистрирован')
        login(request, user)

        return render(request, 'myapp/header.html', {'user': user})


def login(request):
    if len(request.POST) == 0:
        return render(request, 'myapp/login.html', {})
    else:
        from django.contrib.auth import authenticate, login
        from django.contrib.auth.models import User
        username = request.POST['name']
        password = request.POST['password']

        try:
            user = authenticate(request, username=username, password=password)
        except Exception:
            return HttpResponseBadRequest('Не удалось войти')
        if user is not None:
            login(request, user)
            return render(request, 'myapp/header.html', {'user': user})
        else:
            return HttpResponseBadRequest('Не удалось войти')


def logout(request):
    from django.contrib.auth import logout

    logout(request)
    return render(request, 'myapp/header.html', {})


def history(request):
    if len(request.GET) == 0:
        history = History.objects.filter(user=request.user)
        counter = 0
        page_counter = 1
        page = []
        orgs = {}

        for h in history:
            if counter > 9:
                orgs.update({str(page_counter): page})
                page = []
                counter = 0
                page_counter += 1
                page.append(h)
            else:
                page.append(h)
            counter += 1
        if len(page) != 0:
            orgs.update({str(page_counter): page})

        return render(request, 'myapp/history.html', {'orgs': orgs})
    else:
        with open(path.join(path.dirname(path.abspath(__file__)), 'history/' + request.GET['inn'] + '.json')) as f:
            org_info = json.loads(f.read())
            f.close()
        return render(request, 'myapp/resultTable.html', {'org': org_info})


def save_criteria(request):
    if request.user.is_authenticated:
        criteria = Criteria.objects.filter(user=request.user)

        if criteria.exists():
            criteria = Criteria.objects.get(user=request.user)
            for key, value in request.GET.items():
                if 0 <= int(value) <= 10:
                    setattr(criteria, key, int(value))
                else:
                    return HttpResponseBadRequest("Недопустимое значение критерия (0-10)")

            criteria.user = request.user
            criteria.save()
            return HttpResponse("Изменения успешно сохранены")
        else:
            criteria = Criteria()
            for key, value in request.GET.items():
                if 0 <= int(value) <= 10:
                    setattr(criteria, key, int(value))
                else:
                    return HttpResponseBadRequest("Недопустимое значение критерия (0-10)")

            criteria.user = request.user
            criteria.save()
            return HttpResponse("Изменения успешно сохранены")
    else:
        return HttpResponseBadRequest('Сначала войдите в аккаунт')


def get_criteria(request):
    if request.user.is_authenticated:
        criteria = Criteria.objects.filter(user=request.user)

        if(criteria.exists()):
            return HttpResponse(json.dumps(criteria.values().first()))
        else:
            return HttpResponse()
    else:
        return HttpResponseBadRequest('Сначала войдите в аккаунт')