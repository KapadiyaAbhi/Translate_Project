from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from .forms import UploadForm
from .models import Upload
import os
import speech_recognition as sr
import requests
from reportlab.pdfgen import canvas

def home(request):
    return render(request, 'main/home.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('upload')
    return render(request, 'main/login.html')

def register_user(request):
    if request.method == "POST":
        User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        return redirect('login')
    return render(request, 'main/register.html')

def logout_user(request):
    logout(request)
    return redirect('login')

import requests
import requests
import requests

def translate_text(text, source_lang, target_lang):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": f"{source_lang}|{target_lang}"
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data['responseData']['translatedText']
    except Exception as e:
        print("Translation error:", e)
        return "Translation failed"


def create_pdf(text, file_path):
    c = canvas.Canvas(file_path)
    c.drawString(100, 800, "Translated Text:")
    lines = text.split('\n')
    y = 780
    for line in lines:
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(100, y, line[:100])
        y -= 20
    c.save()

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            file = request.FILES['file']
            extension = os.path.splitext(file.name)[1]

            # Process file
            if extension in ['.txt']:
                text = file.read().decode('utf-8')
            elif extension in ['.wav', '.mp3']:
                recognizer = sr.Recognizer()
                with sr.AudioFile(file) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
            else:
                return render(request, 'main/upload.html', {
                    'form': form,
                    'error': 'Unsupported file format'
                })

            translated = translate_text(
                text,
                form.cleaned_data['source_language'],
                form.cleaned_data['language']
            )

            upload.translated_text = translated
            upload.save()

            # Save as TXT
            txt_path = f'media/translated_{upload.id}.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(translated)

            # Save as PDF
            pdf_path = f'media/translated_{upload.id}.pdf'
            create_pdf(translated, pdf_path)

            return render(request, 'main/result.html', {
                'translated': translated,
                'upload': upload
            })
    else:
        form = UploadForm()
    return render(request, 'main/upload.html', {'form': form})

@login_required
def download_file(request, file_id):
    upload = Upload.objects.get(id=file_id, user=request.user)
    path = f'media/translated_{upload.id}.txt'
    return FileResponse(open(path, 'rb'), as_attachment=True, filename="translated.txt")

@login_required
def download_pdf(request, file_id):
    upload = Upload.objects.get(id=file_id, user=request.user)
    path = f'media/translated_{upload.id}.pdf'
    return FileResponse(open(path, 'rb'), as_attachment=True, filename="translated.pdf")

@login_required
def dashboard(request):
    uploads = Upload.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'main/dashboard.html', {'uploads': uploads})
