import pandas as pd
from typing import List

TASKS = {
    'CombFunction': 'Комбинация функций',
    'MentalArithmetic': 'Ментальная арифметика',
    'VisualSearch': 'Визуальный поиск',
    'WorkingMemory': 'Рабочая память'
}

def merge_recommendations(tasks: List[str]) -> pd.DataFrame:
    """
    Preprocesses the recommendations data for given tasks.
    
    Args:
        tasks: List of task identifiers (e.g. ['VisualSearch', 'WorkingMemory'])
    
    Returns:
        DataFrame with merged recommendations for the specified tasks
    """
    df = pd.read_parquet('data/recommendations.parquet')
    
    # Create query string for multiple tasks
    query_parts = [f"`ЭКФ*` == '{TASKS[task]}'" for task in tasks]
    query = ' | '.join(query_parts)
    
    # Filter dataframe and drop duplicates
    filtered_df = df.query(query)[df.columns[1:]]
    return filtered_df.drop_duplicates()

def get_recommendation_table(df: pd.DataFrame, title: str) -> str:
    # Convert DataFrame to LaTeX manually to have more control
    rows = []

    # Add the header row
    rows.append('\\begin{center}\n    \\centering')
    rows.append('    \\begin{longtable}{|p{0.25\\textwidth}|p{0.20\\textwidth}|p{0.54\\textwidth}|}')
    # Use the provided title
    rows.append(f'\\multicolumn{{3}}{{l}}{{ \\textbf{{{title}}}}}\\\\')
    rows.append('\\multicolumn{3}{c}{}\\\\\\hline')
    rows.append('    \\textbf{Рекомендация (занятие/курс)*} & \\textbf{График освоения программы} &   \\textbf{Описание программы} \\\\ \\hline')

    # Add each data row
    for _, row in df.iterrows():
        rows.append(f"    {row[0]} & {row[1]} & {row[2]} \\\\ \\hline")

    # Add the closing tags
    rows.append('\\end{longtable}')
    rows.append('\\end{center}')

    # Join all rows and print
    latex_table = '\n'.join(rows)
    return latex_table

def generate_recommendation_table(tasks: List[str]): 
    merged_df = merge_recommendations(tasks)
    
    # Generate title by mapping tasks to their Russian names and formatting
    task_names = [TASKS[task] for task in tasks]
    # Capitalize first word, lowercase others
    task_names = [task_names[0]] + [name.lower() for name in task_names[1:]]
    title = ', '.join(task_names)
    
    latex_table = get_recommendation_table(merged_df, title)
    with open('recomendations/recomendation_table.tex', 'w') as f:
        f.write(latex_table)