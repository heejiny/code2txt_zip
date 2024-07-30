import streamlit as st
import zipfile
import io
import os

# ZIP 파일에서 확장자별로 파일 목록을 생성하는 함수
def generate_extension_list(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        extension_list = {}
        for file_name in zip_ref.namelist():
            _, ext = os.path.splitext(file_name)
            if ext:
                if ext not in extension_list:
                    extension_list[ext] = []
                extension_list[ext].append(file_name)
        return extension_list

# ZIP 파일을 처리하여 텍스트 파일로 기록하는 함수
def process_zip_file(zip_file, selected_extensions, output_file_name):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_count = 0
        output = io.StringIO()

        for file_name in zip_ref.namelist():
            _, ext = os.path.splitext(file_name)
            if ext in selected_extensions:
                with zip_ref.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    output.write(f'// file path : {file_name}\n')
                    output.write(content + '\n\n')
                    file_count += 1

        output.seek(0)
        with open(output_file_name, 'w', encoding='utf-8') as out_file:
            out_file.write(output.getvalue())

        return file_count

st.title('코드 파일 처리기 (ZIP 지원)')
st.write("""
이 애플리케이션은 ZIP 파일 내의 코드 파일을 분석하고, 사용자가 특정 확장자의 파일만 선택할 수 있도록 도와줍니다. 
선택된 확장자의 파일들의 내용을 하나의 텍스트 파일로 기록하여 다운로드할 수 있습니다.
""")

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=['zip'])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    
    if zipfile.is_zipfile(uploaded_file):
        extension_list = generate_extension_list(uploaded_file)
        st.write("파일 확장자 목록")
        
        selected_extensions = []
        for ext in extension_list.keys():
            if st.checkbox(ext, value=True):
                selected_extensions.append(ext)
        
        if st.button("선택 완료"):
            output_file_name = uploaded_file.name.replace('.zip', '_code2txt.txt')
            
            if st.button("시작"):
                file_count = process_zip_file(uploaded_file, selected_extensions, output_file_name)
                
                with open(output_file_name, 'rb') as f:
                    btn = st.download_button(
                        label="코드 파일 다운로드",
                        data=f,
                        file_name=output_file_name,
                        mime="text/plain"
                    )
                
                st.success(f"선택한 확장자의 파일 {file_count}개를 처리했습니다.")
    else:
        st.error("올바른 ZIP 파일이 아닙니다.")
