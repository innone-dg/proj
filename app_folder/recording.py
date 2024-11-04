# app_folder/recording.py
import sounddevice as sd
import wavio
import datetime
import parselmouth
import numpy as np
from django.views import View
from django.shortcuts import render

# class RecordingApp(View):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)  # 親クラスの初期化
#         self.samplerate = 44100
#         self.channels = 1
#         self.recordings = []
#         self.is_recording = False

#     def record_view(request):
#         page = request.GET.get('page')
#         question = request.GET.get('question')

#          # 必要なデータを取得し、recording.htmlに渡す
#         context = {
#             'page': page,
#             'question': question,
#             'content_text': content,  # コンテンツをテンプレートに渡す
#         }
    
#         return render(request, 'app_folder/recording2.html', context)

import os
import numpy as np
import matplotlib.pyplot as plt
import parselmouth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings

# Ensure media path is set up correctly
MEDIA_ROOT = settings.MEDIA_ROOT

def plot_pitch(audio_path):
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
        
    #     # Return image URL to frontend
    #     return JsonResponse({"image_url": f"/media/pitch_plot.png"})
    # else:
    #     return JsonResponse({"error": "No audio file received."}, status=400)
