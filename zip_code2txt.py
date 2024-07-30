import streamlit as st
import zipfile
import os
import io

def process_zip_file(zip_file, output_file_name):
    excluded_files = {
        '.next', 'node_modules', 'components/ui', '.json', '.gitignore', 'next-env.ts', 
        'next.config.js', 'README.md', '.txt'
    }
    extensions = {'.tsx', '.ts', '.js', '.jsx'}
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_count = 0
        total_files = 0
        output = io.StringIO()
        
        for file_name in zip_ref.namelist():
            if any(excluded in file_name for excluded in excluded_files):
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

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=['zip'])

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    
    if zipfile.is_zipfile(uploaded_file):
        output_file_name = uploaded_file.name.replace('.zip', '_code2txt.txt')
        total_files, file_count = process_zip_file(uploaded_file, output_file_name)
        
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

