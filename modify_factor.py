import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_histograms(subject_number, df):
    # Ensure subject_number is of the same type as df['subject']
    subject_number = int(subject_number)
    
    # Calculate error percentage
    df['error_percentage'] = (1 - df['answer']) * 100
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Increase font size for all text elements
    plt.rcParams.update({'font.size': 14})
    
    # Subplot 1: Histogram of error percentages
    n1, bins1, patches1 = ax1.hist(df['error_percentage'], bins=3, edgecolor='black')
    ax1.set_xlabel('Процент ошибок', fontsize=16)
    ax1.set_ylabel('Число детей', fontsize=16)
    
    # Determine the group based on error percentage
    def assign_group(error_percentage):
        if error_percentage < bins1[1]:
            return 'A'
        elif error_percentage < bins1[2]:
            return 'B'
        else:
            return 'C'
    
    df['group'] = df['error_percentage'].apply(assign_group)
    
    ax1.set_xticks(bins1)
    ax1.set_xticklabels([f'{tick:.2f}%' for tick in bins1], fontsize=12)
    ax1.tick_params(axis='y', labelsize=12)
    
    # Subplot 2: Histogram of response times
    n2, bins2, patches2 = ax2.hist(df['response_time'], bins=3, edgecolor='black')
    ax2.set_xlabel('Время ответа (в секундах)', fontsize=16)
    ax2.set_ylabel('Число детей', fontsize=16)
    ax2.tick_params(axis='both', labelsize=12)
    
    # Mark the subject's data points on both histograms
    subject_data = df[df['subject'] == subject_number]
    if not subject_data.empty:
        subject_error = subject_data['error_percentage'].values[0]
        subject_response_time = subject_data['response_time'].values[0]
        subject_group = subject_data['group'].values[0]
        
        # Find the bar height for error percentage
        error_bar_height = n1[np.digitize(subject_error, bins1, right=True) - 1]
        ax1.plot(subject_error, error_bar_height*0.25, 'D', color='red', markersize=20, label=f'Subject {subject_number}')
        
        # Find the bar height for response time
        response_time_bar_height = n2[np.digitize(subject_response_time, bins2, right=True) - 1]
        ax2.plot(subject_response_time, response_time_bar_height*0.25, 'D', color='red', markersize=20, label=f'Subject {subject_number}')
        
        ax1.set_title(f'Доля ошибок {subject_error:.2f}%\nРезультат - группа {subject_group}', fontsize=18)
        ax2.set_title(f'Среднее время ответа {subject_response_time:.2f} сек\nРезультат - группа {subject_group}', fontsize=18)
    else:
        ax1.set_title('Histogram of Error Percentages', fontsize=18)
        ax2.set_title('Histogram of Response Times', fontsize=18)
    
    plt.tight_layout()
    return fig

# Example usage
def create_histograms(test_name, subject_number):
    df = pd.read_csv(f"data/{test_name}7.csv")
    # Ensure 'subject' column is of type int
    df['subject'] = df['subject'].astype(int)
    # Plot histograms for the given subject number
    fig = plot_histograms(subject_number, df)
    # Save the figure as a PNG file
    fig.savefig(f'subjects/{subject_number}/{test_name}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory
