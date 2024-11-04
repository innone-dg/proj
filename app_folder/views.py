from django.shortcuts import render, redirect  
from django.views import View
from django.contrib import messages
import matplotlib.pyplot as plt

class SampleView(View):  
	def get(self, request, *args, **kwargs):  
		return render(request, 'app_folder/top_page.html')
top_page = SampleView.as_view()

from django.http import HttpResponse, JsonResponse
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from .models import AudioFile
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
import sounddevice as sd
import matplotlib.font_manager as fm
import wavio
import numpy as np
import parselmouth
#import simpleaudio as sa
from django.http import JsonResponse
import os
import soundfile as sf
import datetime
from django.contrib.auth.models import User
from django.db import IntegrityError

def entryview(request):
    if request.method == 'POST':
        username_data = request.POST['username_data']
        password_data = request.POST['password_data']
        try:
            User.objects.create_user(username_data, '', password_data)
        except IntegrityError:
            return render(request, 'entry.html', {'error': 'このユーザーは既に登録されています'}) 
        user = User.objects.create_user(username_data, '', password_data)
    else:
        return render(request, 'app_folder/entry.html', { })
    return render(request, 'app_folder/entry.html', { })

def loginview(request):
    if request.method == 'POST':
        username_data = request.POST['username_data']
        password_data = request.POST['password_data']
        user = authenticate(request, username=username_data, password=password_data)
        if user is not None:
            login(request, user)
            return redirect('list')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません')
            return redirect(request, 'app_folder/login.html')
    return render(request, 'app_folder/login.html')

def logoutview(request):
    logout(request)
    return redirect('login')


# 日本語フォントの設定（WindowsではMeiryoフォントを使用）
jp_font = fm.FontProperties(fname="C:/Windows/Fonts/meiryo.ttc")

# ページごとの問題数を定義（例：57ページには10問、75ページには3問など）
pages = {
    57: 10,
    58: 10,
    68: 5,
    75: 3,
    77: 10,
    80: 5,
    82: 8,
    84: 6
}

# ページ選択ビュー
def select_page_view(request):
    # ページごとの問題番号リストを生成
    pages_with_questions = {
        page: list(range(1, questions + 1)) for page, questions in pages.items()
    }
    # テンプレートに渡す
    return render(request, 'app_folder/select_page.html', {'pages': pages_with_questions})

# Django View for recording
def record_view(request, page=None, question=None):
    page = request.GET.get('page')
    question = request.GET.get('question')
    
    return render(request, 'app_folder/recording2.html', {
        'page': page,
        'question': question,
    })


# def plot_pitch(audio_path):
#     # 音声ファイルを読み込み
#     sound = parselmouth.Sound(audio_path)
#     # ピッチを取得
#     pitch = sound.to_pitch()

#     # フレーム数とピッチ周波数を取得
#     pitch_values = pitch.selected_array['frequency']  # 周波数
#     times = pitch.xs()  # 時間（フレームごとのタイミング）

#     # 周波数が0（無音）でない部分のみプロット
#     pitch_values = np.where(pitch_values == 0, np.nan, pitch_values)

#     # プロット設定
#     plt.figure(figsize=(10, 6))
#     plt.plot(times, pitch_values, label="Pitch (frequency)")
#     plt.xlabel("Time (s)")
#     plt.ylabel("Frequency (Hz)")
#     plt.title("Pitch Analysis")
#     plt.legend()
#     plt.grid()
#     plt.show()

# Ensure media path is set up correctly
MEDIA_ROOT = settings.MEDIA_ROOT

def plot_pitch(audio_path):
    try:
        # soundfileを使って音声ファイルを読み込み
        data, sample_rate = sf.read(audio_path)
    except Exception as e:
        print(f"音声ファイルの読み込みエラー: {e}")
        return None
    try:
        sound = parselmouth.Sound(audio_path)
        pitch = sound.to_pitch()
        pitch_values = pitch.selected_array['frequency']
        times = pitch.xs()

        pitch_values = np.where(pitch_values == 0, np.nan, pitch_values)

        plt.figure(figsize=(10, 6))
        plt.plot(times, pitch_values, label="Pitch (frequency)")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Pitch Analysis")
        plt.legend()
        plt.grid()

        # Save the plot image to a file
        image_path = os.path.join(MEDIA_ROOT, "pitch_plot.png")
        plt.savefig(image_path)
        plt.close()

        return image_path
    except Exception as e:
        print(f"プロットエラー: {e}")
        return None

@csrf_exempt
def plot_pitch_view(request):
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]

        # 拡張子をチェックしてWAV形式以外はエラーにする
        if not audio_file.name.endswith(".wav"):
            return JsonResponse({"error": "WAV形式の音声ファイルを送信してください。"}, status=400)

        # 一時ファイルとして保存
        try:
            audio_path = default_storage.save("temp_audio.wav", audio_file)
            audio_full_path = default_storage.path(audio_path)
            print(f"音声ファイルの保存パス: {audio_full_path}")

            # ピッチ解析
            image_path = plot_pitch(audio_full_path)
            if image_path is None:
                return JsonResponse({"error": "ピッチ解析中にエラーが発生しました。"}, status=500)
            return JsonResponse({"image_url": f"/media/pitch_plot.png"})
        except parselmouth.PraatError as e:
            print("Praatエラー: ", e)
            return JsonResponse({"error": "ピッチ解析中にエラーが発生しました。"}, status=500)
        except Exception as e:
            print("その他のエラー: ", e)
            return JsonResponse({"error": "予期しないエラーが発生しました。"}, status=500)
        finally:
            # 保存した一時音声ファイルを削除
            if 'audio_path' in locals():
                default_storage.delete(audio_path)
    else:
        return JsonResponse({"error": "音声ファイルがありません。"}, status=400)
        
# 履歴閲覧機能
class HistoryReview:
    def __init__(self):
        pass

    def view_history(self, request):
        """過去の録音を表示"""
        recordings_dir = "static/recordings/"
        if not os.path.exists(recordings_dir):
            return JsonResponse({"status": "error", "message": "録音履歴が存在しません"})
        recordings = os.listdir(recordings_dir)
        return JsonResponse({"status": "success", "recordings": recordings})
