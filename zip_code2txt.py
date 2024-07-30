import streamlit as st
import zipfile
import os

def process_zip_file(zip_file):
    excluded_files = {
        '.next', 'node_modules', 'components/ui', '.json', '.gitignore', 'next-env.ts', 
        'next.config.js', 'README.md', '.txt'
    }
    extensions = {'.tsx', '.ts', '.js', '.jsx'}
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_count = 0
        for file_name in zip_ref.namelist():
            if any(file_name.startswith(excluded) for excluded in excluded_files):
                continue
            if file_name.endswith(tuple(extensions)):
                with zip_ref.open(file_name) as file:
                    content = file.read().decode('utf-8')
                    st.write(f"파일명: {file_name}")
                    st.code(content, language='javascript')
                    file_count += 1
        return file_count

st.title('코드 파일 처리기 (ZIP 지원)')

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=['zip'])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    
    if zipfile.is_zipfile(uploaded_file):
        file_count = process_zip_file(uploaded_file)
        st.success(f"ZIP 파일에서 총 {file_count}개의 코드 파일을 처리했습니다.")
    else:
        st.error("올바른 ZIP 파일이 아닙니다.")
