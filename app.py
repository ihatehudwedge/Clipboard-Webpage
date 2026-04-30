from flask import Flask, render_template, request, redirect, url_for
import os
import glob
import json
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# 클립보드 파일이 저장될 디렉토리 경로
CLIP_DIR = './clip'
os.makedirs(CLIP_DIR, exist_ok=True)

def time_now():
    return datetime.now()

def clip_template(title:str, content:str):
    data = {
        "title": title,
        "content": content,
        "date": time_now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return data

def get_notes():
    notes = []

    # ./clip/ 폴더 내의 모든 .json 파일 경로를 가져옴
    file_paths = glob.glob(os.path.join(CLIP_DIR, '*.json'))

    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                note_data = json.load(f)

                note_date_str = note_data.get('date', '')
                if note_date_str:
                    note_date = datetime.strptime(note_date_str, '%Y-%m-%d %H:%M:%S')
                    
                    # 3. 작성일로부터 7일 이상 경과했는지 확인합니다.
                    if time_now() - note_date >= timedelta(days=1):
                        os.remove(path)
                        continue

                # 7일이 지나지 않은 유효한 데이터만 리스트에 추가합니다.
                note_data['filename'] = os.path.basename(path)
                notes.append(note_data)
        except Exception as e:
            print(f"파일 읽기 오류 ({path}): {e}")
            
    # 최신 글이 먼저 보이도록 날짜 역순으로 정렬 (선택 사항)
    notes.sort(key=lambda x: x.get('date', ''), reverse=True)

    return notes

@app.route('/')
def index():
    return render_template('index.html', notes=get_notes())


@app.route('/add', methods=['POST'])
def add_note():
    # HTML 폼에서 전송된 제목과 내용을 가져옵니다.
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    # 제목과 내용이 모두 비어있으면 무시하고 메인 페이지로 돌아갑니다.
    if not title and not content:
        return redirect(url_for('index'))
    
    filename = f"note_{time.time()}.json"
    filepath = os.path.join(CLIP_DIR, filename)

    # 5. 지정된 경로에 데이터를 JSON 포맷의 텍스트로 저장합니다.
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(clip_template(title, content), f, ensure_ascii=False, indent=4)

    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_note():
    # HTML 폼에서 전달받은 파일명
    filename = request.form.get('filename')
    print(filename)
    
    if filename:
        # 보안을 위해 파일명에 폴더 이동 경로('..')가 없는지 확인 후 처리
        safe_filename = os.path.basename(filename)

        filepath = os.path.join(CLIP_DIR, safe_filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"파일 삭제 오류: {e}")

    # 삭제 후 메인 화면으로 돌아갑니다.
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)