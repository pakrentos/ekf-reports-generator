import os
import pandas as pd
import shutil
import subprocess
from image_overlay import create_iq_image
from modify_factor import create_histograms

# Read the Excel file
df = pd.read_excel("data/список_7класс.xlsx", header=[0,1])

# Read the template
with open("template.tex", "r", encoding="utf-8") as file:
    template_content = file.read()

# Ensure the subjects and subjects_pdfs directories exist
if not os.path.exists("subjects"):
    os.makedirs("subjects")
if not os.path.exists("subjects_pdfs"):
    os.makedirs("subjects_pdfs")

# Process each row in the dataframe
for _, row in df.iterrows():
    subject_code = str(row[('код', 'Unnamed: 0_level_1')])
    iq = row[('IQ', 'Unnamed: 5_level_1')]
    subject_name = row[('ФИО', 'Unnamed: 2_level_1')]
    
    # Skip subjects without IQ value
    if pd.isna(iq):
        print(f"Skipping subject {subject_code} due to missing IQ value")
        continue
    
    # Check if all Kettel factors are missing
    kettel_factors = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'O', 'Q3', 'Q4']
    if all(pd.isna(row[('Кеттел', factor)]) for factor in kettel_factors):
        print(f"Skipping subject {subject_code} due to missing all Kettel factor values")
        continue
    
    # Create subject directory
    subject_dir = f"subjects/{subject_code}"
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)
    
    # Generate IQ image
    create_iq_image(subject_code, iq)
    
    # Generate histograms
    for test in ['CombFunction', 'MentalArithmetic', 'VisualSearch', 'WorkingMemory']:
        create_histograms(test, subject_code)
    
    # Prepare substitution dictionary
    subst_dict = {}
    
    # Process Kettel factors
    for factor in kettel_factors:
        factor_value = row[('Кеттел', factor)]
        if pd.isna(factor_value):
            continue
        scale_image = f"assets/scale_{int(factor_value)}.png"
        subst_dict[f'<factor_{factor.lower()}>'] = scale_image
        
        # Copy scale image to subject directory
        shutil.copy(scale_image, os.path.join(subject_dir, scale_image))
    
    # Generate customized tex file
    customized_content = template_content
    for key, value in subst_dict.items():
        customized_content = customized_content.replace(key, value)
    
    # Write customized tex file
    tex_file_path = os.path.join(subject_dir, f"{subject_code}.tex")
    with open(tex_file_path, "w", encoding="utf-8") as file:
        file.write(customized_content)
    
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

print("Tex files and PDFs generated successfully.")
