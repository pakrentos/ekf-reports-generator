import os
import pandas as pd
import shutil
import subprocess
from image_overlay import create_iq_image
from modify_factor import create_histograms
from generate_recommendation import generate_recommendation_table

# Read the Excel file
df = pd.read_excel("data/список_7класс.xlsx", header=[0,1])

# Read the template
with open("template.tex", "r", encoding="utf-8") as file:
    template_content = file.read()

with open("factors.tex", "r", encoding="utf-8") as file:
    factors_template_content = file.read()

# Ensure the subjects and subjects_pdfs directories exist
if not os.path.exists("subjects"):
    os.makedirs("subjects")
if not os.path.exists("subjects_pdfs"):
    os.makedirs("subjects_pdfs")

RECOMENDATION_HEADER = r"""\begin{center}
    \textbf{\large Рекомендации}
\end{center}

Для проблемных когнитивных функций рекомендуются \textbf{внеклассные занятия}, способствующие их развитию.
Данный набор рекомендаций составлен на основе тщательного анализа большого объема научных публикаций."""

RECOMENDATION_TEX_FNAME = "recomendation_table.tex"

iq_image_text = r"\includegraphics[width=0.7\linewidth]{output_image.png}"
iq_image_empty_text = r"Отсутствуют данные прохождения теста"

factors_empty_text = r"Отсутствуют данные прохождения опросника"
factors_text = r"\input{factors.tex}"

TASKS = ['CombFunction', 'MentalArithmetic', 'VisualSearch', 'WorkingMemory']

# redo = [710, 711, 714, 722, 702, 747, 751]
redo = [701]
with_recomendations = 0
# Process each row in the dataframe
for _, row in df.iterrows():
    subject_code = str(row[('код', 'Unnamed: 0_level_1')])
    # if int(subject_code) not in redo:
    #     print(f"Skipping {subject_code}")
    #     continue

    iq = row[('IQ', 'Unnamed: 5_level_1')]
    subject_name = row[('ФИО', 'Unnamed: 2_level_1')]
    subst_dict = {}
    factors_subst_dict = {}

    # Create subject directory
    subject_dir = f"subjects/{subject_code}"
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)
    
    # Skip subjects without IQ value
    if pd.isna(iq):
        print(f"Skipping subject {subject_code} due to missing IQ value")
        subst_dict['<iq_image>'] = iq_image_empty_text
    else:
        create_iq_image(subject_code, iq)
        subst_dict['<iq_image>'] = iq_image_text
        
    # Check if all Kettel factors are missing
    kettel_factors = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']
    if all(pd.isna(row[('Кеттел', factor)]) for factor in kettel_factors):
        print(f"Skipping subject {subject_code} due to missing all Kettel factor values")
        subst_dict['<factors>'] = factors_empty_text
    else:
        for factor in kettel_factors:
            factor_value = row[('Кеттел', factor)]
            if pd.isna(factor_value):
                continue

            scale_image = f"scale_{int(factor_value)}.png"
            scale_image_fullpath = f"assets/{scale_image}"
            factors_subst_dict[f'<factor_{factor.lower()}>'] = scale_image
            
            # Copy scale image to subject directory
            shutil.copy(scale_image_fullpath, os.path.join(subject_dir, scale_image))
        subst_dict['<factors>'] = factors_text
    
    
    recomendations = [] 
    # Generate histograms
    for test in TASKS:
        groups, is_existing_data = create_histograms(test, subject_code)
        score = [int(v in ['C']) for v in groups.values()]
        sum_score = sum(score)
        if sum_score >= 1 and is_existing_data:
            recomendations.append(test)
    print(recomendations)
    with_recomendations += 1 if recomendations else 0
    
    # Prepare substitution dictionary
    
    if recomendations:
        subst_dict['<RecomendationHeader>'] = RECOMENDATION_HEADER
        generate_recommendation_table(recomendations)
        recomendations_tex_path = os.path.join(subject_dir, RECOMENDATION_TEX_FNAME)
        subst_dict['<Recomendation>'] = r"\input{" + RECOMENDATION_TEX_FNAME + "}"
        shutil.copy(os.path.join("recomendations", RECOMENDATION_TEX_FNAME), recomendations_tex_path)
    else:
        subst_dict['<RecomendationHeader>'] = ""
        subst_dict['<Recomendation>'] = ""

    # Generate customized tex file
    customized_content = template_content
    for key, value in subst_dict.items():
        customized_content = customized_content.replace(key, value)
    
    customized_factors_content = factors_template_content
    for key, value in factors_subst_dict.items():
        customized_factors_content = customized_factors_content.replace(key, value)
    
    # Write customized tex file
    tex_file_path = os.path.join(subject_dir, f"{subject_code}.tex")
    with open(tex_file_path, "w", encoding="utf-8") as file:
        file.write(customized_content)
    
    factors_tex_file_path = os.path.join(subject_dir, 'factors.tex')
    with open(factors_tex_file_path, 'w', encoding='utf-8') as file:
        file.write(customized_factors_content)
        
    # Render TEX file to PDF using LuaLaTeX
    print(f"Generating PDF for {subject_name}")
    try:
        # Change to the subject directory before running LuaLaTeX
        current_dir = os.getcwd()
        os.chdir(subject_dir)
        
        subprocess.run(['lualatex', f"{subject_code}.tex"], 
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Change back to the original directory
        os.chdir(current_dir)
        
        # Move and rename the PDF to subjects_pdfs directory
        pdf_source = os.path.join(subject_dir, f"{subject_code}.pdf")
        pdf_destination = os.path.join("subjects_pdfs", f"{subject_name}.pdf")
        shutil.move(pdf_source, pdf_destination)
        print(f"Generated PDF for {subject_name}")
    except subprocess.CalledProcessError:
        print(f"Failed to generate PDF for {subject_name}")
        # Change back to the original directory in case of error
        os.chdir(current_dir)
    
print(f'{with_recomendations=}')

print("Tex files and PDFs generated successfully.")
