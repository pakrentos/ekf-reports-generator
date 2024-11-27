import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def determine_group(value, histogram_bins):
    """Determine group (A, B, or C) based on value and histogram boundaries"""
    _, q1, left_bord, _, q2, _, right_bord, q3, _ = histogram_bins
    
    if value <= left_bord:
        return 'A'
    elif right_bord >= value > left_bord:
        return 'B'
    else:
        return 'C'

def plot_single_histogram(ax, data, subject_value, title, xlabel, make_plots=True):
    """Plot a single histogram with group boundaries and subject marker"""
    data = data[pd.notna(data)]
    
    # Create histogram bins to determine boundaries
    histogram = np.histogram(data, 8)
    hist_bins = histogram[1]
    _, q1, left_bord, _, q2, _, right_bord, q3, _ = hist_bins
    
    if make_plots:
        # Create histogram plot
        ax.hist(data, 8, edgecolor='black', facecolor='lightgrey')
        
        # Set labels
        ax.set_xlabel(xlabel, fontsize=26)
        ax.set_ylabel('Число детей', fontsize=26)
        
        # Add vertical lines for group boundaries
        ax.axvline(left_bord, color='red', linewidth=4)
        ax.axvline(right_bord, color='red', linewidth=4)
        
        # Set up twin axis for group labels
        ax2 = ax.twiny()
        xmin, xmax = np.percentile(data, [0, 100])
        ax.set_xlim([xmin, xmax])
        ax2.set_xlim([xmin, xmax])
        
        # Add group labels
        labels_position = [q1, q2, q3]
        labels = ['A', 'B', 'C']
        ax2.set_xticks(labels_position)
        ax2.set_xticklabels(labels)
        
        # Add subject marker and title
        if subject_value is not None:
            bar_index = np.digitize(subject_value, histogram[1][:-1], right=True) - 1
            bar_height = histogram[0][bar_index]
            ax.plot(subject_value, bar_height/4, 'D', color='black', markersize=20)
            
            group = determine_group(subject_value, hist_bins)
            ax.set_title(f"{title} {subject_value:.2f}\nРезультат - группа {group}", fontsize=30)
            return group
            
        ax.set_title(title, fontsize=30)
        return None
    
    # If not plotting, just return the group
    if subject_value is not None:
        return determine_group(subject_value, hist_bins)
    return None

def plot_histograms(subject_number, df, make_plots=True):
    """Create a 2x2 grid of histograms and return groups for each metric"""
    subject_number = int(subject_number)
    figsize = (20, 14)
    
    # Get subject data
    subject_data = df[df['subject'] == subject_number]
    
    if subject_data.empty:
        if make_plots:
            fig, ax = plt.subplots(figsize=figsize)
            ax.set_axis_off()
            ax.text(0.5, 0.5, "Отсутствуют данные прохождения теста",
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=40,
                    transform=ax.transAxes)
            return fig, {}, False
        return None, {}, False
    
    # Create figure only if plotting is needed
    if make_plots:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        plt.rcParams.update({'font.size': 26})
    else:
        fig = None
        ax1 = ax2 = ax3 = ax4 = None
    
    groups = {}
    
    # Get subject values
    subject_error = subject_data['error_percentage'].values[0] if 'error_percentage' in df else None
    subject_time = subject_data['response_time'].values[0] if 'response_time' in df else None
    subject_exhaust = subject_data['diff'].values[0] if 'diff' in df else None
    subject_attention = subject_data['attention'].values[0] if 'attention' in df else None
    
    # Process each metric
    if subject_error is not None and not np.isnan(subject_error):
        groups['errors'] = plot_single_histogram(ax1, df['error_percentage'], subject_error, 
                                            'Процент ошибок', 'Процент ошибок', make_plots)
    elif make_plots:
        ax1.set_visible(False)
    
    if subject_time is not None and not np.isnan(subject_time):
        groups['time'] = plot_single_histogram(ax2, df['response_time'], subject_time, 
                                            'Время ответа', 'Время ответа (в секундах)', make_plots)
    elif make_plots:
        ax2.set_visible(False)
    
    if subject_exhaust is not None and not np.isnan(subject_exhaust):
        groups['exhaust'] = plot_single_histogram(ax3, df['diff'], subject_exhaust, 
                                                'Уровень усталости', 'Усталость (условные единицы)', make_plots)
    elif make_plots:
        ax3.set_visible(False)
    
    if subject_attention is not None and not np.isnan(subject_attention):
        groups['attention'] = plot_single_histogram(ax4, df['attention'], subject_attention, 
                                        'Уровень неустойчивости внимания', 'Неусточивость внимания (условные единицы)', make_plots)
    elif make_plots:
        ax4.set_visible(False)
    
    if make_plots:
        plt.tight_layout()
    
    return fig, groups, True

def create_histograms(test_name, subject_number, make_plots=True):
    """Create and save histograms for a given subject"""
    df = pd.read_csv(f"data/{test_name}7_modified.csv")
    df['subject'] = df['subject'].astype(int)
    
    # Create plots and get groups
    fig, groups, is_existing_data = plot_histograms(subject_number, df, make_plots)
    
    # Save the figure only if plots were created
    if make_plots and fig is not None:
        fig.savefig(f'subjects/{subject_number}/{test_name}.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    return groups, is_existing_data
