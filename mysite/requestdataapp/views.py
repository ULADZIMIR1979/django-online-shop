from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.conf import settings
import os


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    return render(request, 'requestdataapp/user-bio-form.html')


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    context = {}

    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']

        # Проверка размера файла (1 МБ = 1048576 байт)
        MAX_FILE_SIZE = 1048576  # 1 МБ

        if myfile.size > MAX_FILE_SIZE:
            context['error'] = f'Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // 1048576} МБ'
        else:
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print("saved file", filename)
            context['success'] = f'Файл {filename} успешно загружен'
            context['file_size'] = myfile.size

    return render(request, 'requestdataapp/file-upload.html', context=context)