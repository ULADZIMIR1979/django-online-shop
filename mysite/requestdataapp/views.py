from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UserBioForm, UploadFileForm


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
    context = {
        "form": UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data['file']

            # Проверка размера файла (1 МБ = 1048576 байт)
            MAX_FILE_SIZE = 1048576  # 1 МБ

            if myfile.size > MAX_FILE_SIZE:
                error_message = f'Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // 1048576} МБ'
                return render(request, 'requestdataapp/file-upload.html', {
                    'form': form,
                    'error': error_message
                })
            else:
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                print("saved file", filename)
                return render(request, 'requestdataapp/file-upload.html', {
                    'form': UploadFileForm(),
                    'success': f'Файл {filename} успешно загружен',
                    'file_size': myfile.size
                })
    else:
        form = UploadFileForm()

    return render(request, 'requestdataapp/file-upload.html', {'form': form})