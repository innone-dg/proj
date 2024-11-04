from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import os

def practiceview(request):
    return render(request, 'app_folder/listening.html')

def check_audio_file(request, page, question, person, pattern=''):
    # パスを生成
    # file_path = f'teacher/p{page}/Q{question}/{page}_{question}{pattern}_{person}.wav'
    audio_path = os.path.join(settings.MEDIA_ROOT, f'teacher/p{page}/Q{question}/{page}_{question}{pattern}_{person}.wav')
    
    # ファイルの存在確認
    if os.path.exists(audio_path):
        audio_url = f"{settings.MEDIA_URL}teacher/p{page}/Q{question}/{page}_{question}{pattern}_{person}.wav"
        return JsonResponse({"exists": True, "audio_url": audio_url})
    else:
        return JsonResponse({"exists": False, "message": f"{page}ページの問題{question}の音声は存在しません"})
