import streamlit as st
import zipfile
import os
import io

def process_zip_file(zip_file, output_file_name, excluded_files, extensions):
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

st.markdown("""
이 앱은 ZIP 파일에서 코드 파일을 추출하고, 사용자가 선택한 파일 및 확장자에 따라 필터링하여 하나의 텍스트 파일로 결합합니다.
- **ZIP 파일 업로드**: 분석할 ZIP 파일을 업로드합니다.(최대 200MB)
- **텍스트 파일(.txt)로 기록할 파일을 선택해주세요.**
- **체크된 폴더, 파일, 확장자만 기록합니다.
- **코드 파일 다운로드**: 처리된 코드를 다운로드할 수 있습니다.
""")

uploaded_file = st.file_uploader("ZIP 파일을 업로드하세요", type=['zip'])

if uploaded_file is not None:
    excluded_files_options = [
        '.next', 'node_modules', 'components/ui', '.json', '.gitignore', 'next-env.ts',
        'next.config.js', 'README.md', '.txt'
    ]
    extensions_options = ['.tsx', '.ts', '.js', '.jsx', '.py', '.java', '.rb', '.cpp', '.c']
    
    st.write("### 텍스트 파일에 기록할 파일을 선택해주세요.")

    extensions_selected = [ext for ext in extensions_options if st.checkbox(ext, value=ext in ['.tsx', '.ts', '.js', '.jsx'])]
    excluded_files_selected = [item for item in excluded_files_options if not st.checkbox(item, value=False)]
    
    if st.button('기록하기'):
        if zipfile.is_zipfile(uploaded_file):
            output_file_name = uploaded_file.name.replace('.zip', '_code2txt.txt')
            total_files, file_count = process_zip_file(uploaded_file, output_file_name, excluded_files_selected, extensions_selected)
            
            with open(output_file_name, 'rb') as f:
                st.download_button(
                    label="코드 파일 다운로드",
                    data=f,
                    file_name=output_file_name,
                    mime="text/plain"
                )
            
            st.success(f"ZIP 파일에서 총 {file_count}개의 코드 파일을 처리했습니다.")
            st.info(f"총 {total_files}개의 파일이 있습니다.")
        else:
            st.error("올바른 ZIP 파일이 아닙니다.")
