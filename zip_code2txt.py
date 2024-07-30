import streamlit as st
import zipfile
import os
import io

# ZIP 파일에서 파일 트리를 생성하는 함수
def generate_file_tree(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_tree = {}
        for file_name in zip_ref.namelist():
            parts = file_name.split('/')
            current = file_tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        return file_tree

# 폴더 체크박스 상태를 업데이트하는 함수
def update_folder_state(state, folder_path, checked):
    for key in st.session_state:
        if key.startswith(folder_path):
            st.session_state[key] = checked

# 파일 트리를 재귀적으로 보여주는 함수
def display_file_tree(file_tree, path=''):
    for key, value in file_tree.items():
        new_path = os.path.join(path, key)
        if isinstance(value, dict):
            folder_checked = st.checkbox(f"폴더: {key}", value=True, key=new_path, on_change=update_folder_state, args=(new_path, st.session_state[new_path]))
            if folder_checked:
                with st.expander(f"폴더: {key}", expanded=True):
                    display_file_tree(value, new_path)
            else:
                update_folder_state(st.session_state, new_path, False)
        else:
            st.checkbox(f"파일: {key}", value=True, key=new_path)

# ZIP 파일을 처리하여 텍스트 파일로 기록하는 함수
def process_zip_file(zip_file, selected_files, output_file_name):
    extensions = {'.tsx', '.ts', '.js', '.jsx'}
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_count = 0
        total_files = 0
        output = io.StringIO()
        
        for file_name in zip_ref.namelist():
            if not selected_files.get(file_name, False):
                continue
            if file_name.endswith(tuple(extensions)):
                with zip_ref.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    output.write(f'// file path : {file_name}\n')
                    output.write(content + '\n\n')
                    file_count += 1
            total_files += 1

        output.seek(0)
        with open(output_file_name, 'w', encoding='utf-8') as out_file:
            out_file.write(output.getvalue())
        
        return total_files, file_count

st.title('코드 파일 처리기 (ZIP 지원)')
st.write("""
이 애플리케이션은 ZIP 파일 내의 코드 파일을 분석하고, 사용자가 제외할 파일이나 폴더를 선택할 수 있도록 도와줍니다. 
선택된 파일과 폴더를 제외한 나머지 파일들의 내용을 하나의 텍스트 파일로 기록하여 다운로드할 수 있습니다.
""")

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=['zip'])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    
    if zipfile.is_zipfile(uploaded_file):
        file_tree = generate_file_tree(uploaded_file)
        st.write("파일 트리")
        display_file_tree(file_tree)
        
        if st.button("선택 완료"):
            selected_files = {key: st.session_state[key] for key in st.session_state if isinstance(st.session_state[key], bool)}
            output_file_name = uploaded_file.name.replace('.zip', '_code2txt.txt')
            
            if st.button("시작"):
                total_files, file_count = process_zip_file(uploaded_file, selected_files, output_file_name)
                
                with open(output_file_name, 'rb') as f:
                    btn = st.download_button(
                        label="코드 파일 다운로드",
                        data=f,
                        file_name=output_file_name,
                        mime="text/plain"
                    )
                
                st.success(f"ZIP 파일에서 총 {file_count}개의 코드 파일을 처리했습니다.")
                st.info(f"총 {total_files}개의 파일이 있습니다.")
    else:
        st.error("올바른 ZIP 파일이 아닙니다.")
