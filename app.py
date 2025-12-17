"""
LuxBoat Due Date Calculator - Shiny for Python
===============================================
Students can edit this code directly in the browser!
"""

from shiny import App, render, ui, reactive
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd

# Default data from LuxBoat case study
DEFAULT_DATA = [
    32.5, 35.5, 40, 38.5, 29.5, 37, 40, 49, 44,
    33.5, 44, 37.5, 47, 49, 45, 37.5, 30, 32, 34.5,
    34, 51, 48, 41.5, 39.5, 36, 31, 36, 41, 34
]

# =============================================================================
# STUDENT EXERCISE SECTION - MODIFY THE CODE BELOW!
# =============================================================================

def calculate_statistics(data):
    """
    TODO #1: Calculate basic statistics
    Students: Fill in the calculations below
    """
    # Calculate mean (average)
    mean_time = np.mean(data)  # TODO: What function calculates average?
    
    # Calculate variance (spread of data)
    variance = np.var(data, ddof=1)  # TODO: Why do we use ddof=1?
    
    # Calculate standard deviation
    std_dev = np.std(data, ddof=1)
    
    return mean_time, variance, std_dev


def calculate_autocorrelation(data):
    """
    TODO #2: Calculate lag-1 autocorrelation
    This measures if consecutive times are related
    """
    # Create two series offset by 1
    series_1 = data[:-1]  # All except last
    series_2 = data[1:]   # All except first
    
    # Calculate correlation
    correlation_matrix = np.corrcoef(series_1, series_2)
    autocorr = correlation_matrix[0, 1]
    
    return autocorr


def calculate_due_date(data, boats_needed, confidence_level):
    """
    TODO #3: Calculate due date with confidence interval
    Main calculation combining all concepts
    """
    # Step 1: Basic statistics
    mean_time, variance, std_dev = calculate_statistics(data)
    
    # Step 2: Autocorrelation
    rho_1 = calculate_autocorrelation(data)
    
    # Step 3: Calculate mean time for b boats
    mu_b = boats_needed * mean_time
    
    # Step 4: Calculate variance with autocorrelation adjustment
    # Formula: [(1 + rho) / (1 - rho)] * b * variance
    variance_multiplier = (1 + rho_1) / (1 - rho_1)
    sigma_squared_b = variance_multiplier * boats_needed * variance
    sigma_b = np.sqrt(sigma_squared_b)
    
    # Step 5: Get z-score for confidence level
    z_score = stats.norm.ppf(confidence_level)
    
    # Step 6: Calculate due date in hours
    # Formula: T_due = mu_b + z_score * sigma_b
    due_date_hours = mu_b + z_score * sigma_b
    
    # Step 7: Convert to days (plant works 24 hours/day)
    due_date_days = due_date_hours / 24
    average_days = mu_b / 24
    safety_time_days = due_date_days - average_days
    
    return {
        'mean': mean_time,
        'std': std_dev,
        'variance': variance,
        'autocorr': rho_1,
        'mu_b': mu_b,
        'sigma_b': sigma_b,
        'z_score': z_score,
        'due_date_hours': due_date_hours,
        'due_date_days': due_date_days,
        'average_days': average_days,
        'safety_time_days': safety_time_days
    }

# =============================================================================
# END STUDENT EXERCISE SECTION
# =============================================================================


# UI Definition
app_ui = ui.page_fluid(
    ui.panel_title("🚤 LuxBoat Due Date Calculator"),
    
    ui.markdown("""
    **Interactive Calculator** - Modify the code and see results update!
    
    This calculator helps determine reliable due dates for boat production orders.
    """),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "data_source",
                "Data Source:",
                choices={"default": "Use Example Data", "custom": "Enter Custom Data"}
            ),
            
            ui.panel_conditional(
                "input.data_source === 'custom'",
                ui.input_text_area(
                    "custom_data",
                    "Inter-throughput times (comma-separated):",
                    value=", ".join(map(str, DEFAULT_DATA[:10])),
                    rows=4
                )
            ),
            
            ui.input_slider(
                "boats_needed",
                "Number of boats needed:",
                min=1,
                max=50,
                value=25,
                step=1
            ),
            
            ui.input_slider(
                "confidence",
                "Confidence level (%):",
                min=50,
                max=99,
                value=90,
                step=1
            ),
            
            ui.hr(),
            
            ui.markdown("""
            **Student Instructions:**
            1. Click "Edit code" button (top right)
            2. Find TODO sections in the code
            3. Modify and experiment!
            """),
            
            width=3
        ),
        
        ui.navset_tab(
            ui.nav_panel("📊 Results",
                ui.layout_columns(
                    ui.value_box(
                        "Due Date",
                        ui.output_text("due_date_box"),
                        showcase=ui.span("📅", style="font-size: 3rem;")
                    ),
                    ui.value_box(
                        "Average Time",
                        ui.output_text("avg_time_box"),
                        showcase=ui.span("⏱️", style="font-size: 3rem;")
                    ),
                    ui.value_box(
                        "Safety Time",
                        ui.output_text("safety_time_box"),
                        showcase=ui.span("🛡️", style="font-size: 3rem;")
                    ),
                    col_widths=[4, 4, 4]
                ),
                
                ui.hr(),
                
                ui.h4("Calculation Breakdown"),
                ui.output_table("stats_table"),
                
                ui.hr(),
                
                ui.output_ui("interpretation")
            ),
            
            ui.nav_panel("📈 Visualizations",
                ui.h4("Distribution of Inter-Throughput Times"),
                ui.output_plot("histogram"),
                
                ui.hr(),
                
                ui.h4("Confidence Interval Visualization"),
                ui.output_plot("confidence_plot"),
                
                ui.hr(),
                
                ui.h4("Time Series"),
                ui.output_plot("timeseries")
            ),
            
            ui.nav_panel("📚 Learn More",
                ui.markdown("""
                ### Key Concepts
                
                **Inter-Throughput Time**: Time between consecutive boat completions
                
                **Autocorrelation (ρ₁)**: Measures if consecutive times are related
                - Positive: When one boat takes longer, next probably will too
                - Negative: Times alternate (high, low, high, low)
                - Zero: Times are independent
                
                **Confidence Level**: Probability of meeting the due date
                - 90% confidence = 90% chance of finishing on time
                - Higher confidence requires more safety time
                
                **Safety Time**: Extra buffer beyond average time
                - Accounts for variability
                - Accounts for autocorrelation
                - Ensures reliability
                
                ### Formula
                
                ```
                Due Date = μ_b + z_α × σ_b
                
                where:
                μ_b = b × X̄  (expected time)
                σ_b = √[((1+ρ)/(1-ρ)) × b × S²]  (std dev with autocorrelation)
                z_α = z-score for confidence level
                ```
                
                ### Student Exercises
                
                1. **Change confidence level**: Try 80%, 90%, 95%, 99%
                   - What happens to safety time?
                
                2. **Modify the data**: Add your own times
                   - How does autocorrelation change?
                
                3. **Different boat counts**: Try 10, 25, 50 boats
                   - Is the relationship linear?
                
                4. **Code modifications**:
                   - Add a new visualization
                   - Calculate percentiles (50%, 75%, 90%)
                   - Add more statistics
                
                ### Questions to Think About
                
                1. Why can't we just use the average time?
                2. What would happen if autocorrelation was 0?
                3. Why does higher confidence need more safety time?
                4. How would you explain this to a customer?
                """)
            ),
            
            ui.nav_panel("💻 Code Exercises",
                ui.markdown("""
                ### TODO Exercises in the Code
                
                Click "Edit code" (top right) to see and modify the Python code!
                
                #### TODO #1: Calculate Statistics
                - Find the `calculate_statistics()` function
                - Understand what each line does
                - Try adding median calculation
                
                #### TODO #2: Autocorrelation
                - Find the `calculate_autocorrelation()` function  
                - Why do we use `[:-1]` and `[1:]`?
                - What does `corrcoef` return?
                
                #### TODO #3: Main Calculation
                - Find the `calculate_due_date()` function
                - Follow the 7 steps
                - Try calculating 95th percentile instead
                
                ### Challenge Exercises
                
                **Easy:**
                1. Add a calculation for the median
                2. Change the histogram colors
                3. Add grid lines to plots
                
                **Medium:**
                4. Calculate 80%, 90%, 95% confidence levels simultaneously
                5. Add a box plot visualization
                6. Calculate coefficient of variation
                
                **Hard:**
                7. Implement lag-2 autocorrelation
                8. Add a forecast for next 10 boats
                9. Compare with vs without autocorrelation
                
                ### Example Modifications
                
                **Change visualization:**
                ```python
                # In histogram function, try:
                plt.hist(data, bins=15, color='steelblue', alpha=0.7)
                plt.grid(True, alpha=0.3)
                ```
                
                **Add new statistic:**
                ```python
                # In calculate_statistics, add:
                median_time = np.median(data)
                return mean_time, variance, std_dev, median_time
                ```
                """)
            )
        )
    )
)


def server(input, output, session):
    
    @reactive.calc
    def get_data():
        """Get data based on user selection"""
        if input.data_source() == "custom":
            try:
                data_str = input.custom_data()
                data = [float(x.strip()) for x in data_str.split(',')]
                if len(data) < 2:
                    return DEFAULT_DATA
                return data
            except:
                return DEFAULT_DATA
        else:
            return DEFAULT_DATA
    
    @reactive.calc
    def get_results():
        """Calculate all results"""
        data = get_data()
        boats = input.boats_needed()
        conf = input.confidence() / 100.0
        return calculate_due_date(data, boats, conf)
    
    @output
    @render.text
    def due_date_box():
        results = get_results()
        conf = input.confidence()
        return f"{results['due_date_days']:.1f} days\n({conf}% confidence)"
    
    @output
    @render.text
    def avg_time_box():
        results = get_results()
        return f"{results['average_days']:.1f} days\n(50% confidence)"
    
    @output
    @render.text
    def safety_time_box():
        results = get_results()
        pct = (results['safety_time_days'] / results['average_days'] * 100)
        return f"{results['safety_time_days']:.1f} days\n(+{pct:.1f}%)"
    
    @output
    @render.table
    def stats_table():
        results = get_results()
        boats = input.boats_needed()
        conf = input.confidence()
        
        df = pd.DataFrame({
            'Parameter': [
                'Boats needed',
                'Mean inter-throughput',
                'Standard deviation',
                'Autocorrelation (ρ₁)',
                'Expected time (μ_b)',
                'Std dev with autocorr (σ_b)',
                'Z-score',
                'Due date'
            ],
            'Value': [
                f"{boats}",
                f"{results['mean']:.2f} hours",
                f"{results['std']:.2f} hours",
                f"{results['autocorr']:.3f}",
                f"{results['mu_b']:.1f} hours ({results['average_days']:.1f} days)",
                f"{results['sigma_b']:.2f} hours",
                f"{results['z_score']:.2f}",
                f"{results['due_date_hours']:.1f} hours ({results['due_date_days']:.1f} days)"
            ]
        })
        return df
    
    @output
    @render.ui
    def interpretation():
        results = get_results()
        boats = input.boats_needed()
        conf = input.confidence()
        
        autocorr_text = ""
        if results['autocorr'] > 0.3:
            autocorr_text = "⚠️ **Moderate positive autocorrelation detected!** When one boat takes longer, the next tends to take longer too."
        elif results['autocorr'] > 0.1:
            autocorr_text = "ℹ️ Weak positive autocorrelation detected."
        else:
            autocorr_text = "✓ Negligible autocorrelation - times are fairly independent."
        
        return ui.div(
            ui.markdown(f"""
            ### Interpretation
            
            With **{conf}% confidence**, the order of **{boats} boats** will be completed 
            within **{results['due_date_days']:.1f} days**.
            
            This includes **{results['safety_time_days']:.1f} days** of safety time beyond 
            the average of **{results['average_days']:.1f} days**.
            
            {autocorr_text}
            """),
            class_="alert alert-info"
        )
    
    @output
    @render.plot
    def histogram():
        data = get_data()
        results = get_results()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data, bins=12, edgecolor='black', alpha=0.7, color='steelblue')
        ax.axvline(results['mean'], color='red', linestyle='--', linewidth=2,
                   label=f"Mean: {results['mean']:.1f} hrs")
        ax.set_xlabel('Inter-Throughput Time (hours)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title('Distribution of Inter-Throughput Times', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @output
    @render.plot
    def confidence_plot():
        results = get_results()
        conf = input.confidence() / 100.0
        
        # Create x-axis range
        mu = results['mu_b']
        sigma = results['sigma_b']
        x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
        y = stats.norm.pdf(x, mu, sigma)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot distribution
        ax.plot(x, y, 'b-', linewidth=2, label='Distribution')
        
        # Shade confidence area
        x_fill = x[x <= results['due_date_hours']]
        y_fill = stats.norm.pdf(x_fill, mu, sigma)
        ax.fill_between(x_fill, y_fill, alpha=0.3, color='green',
                        label=f'{conf*100:.0f}% confidence area')
        
        # Add vertical lines
        ax.axvline(mu, color='orange', linestyle='--', linewidth=2,
                  label=f"Average: {mu:.0f} hrs")
        ax.axvline(results['due_date_hours'], color='red', linestyle='--', linewidth=2,
                  label=f"Due date: {results['due_date_hours']:.0f} hrs")
        
        ax.set_xlabel('Time to Complete (hours)', fontsize=11)
        ax.set_ylabel('Probability Density', fontsize=11)
        ax.set_title(f'Due Date with {conf*100:.0f}% Confidence', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @output
    @render.plot
    def timeseries():
        data = get_data()
        results = get_results()
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(range(1, len(data)+1), data, marker='o', linestyle='-',
                color='steelblue', linewidth=1.5, markersize=6)
        ax.axhline(results['mean'], color='red', linestyle='--', linewidth=2,
                  label=f"Mean: {results['mean']:.1f} hrs")
        ax.set_xlabel('Observation Number', fontsize=11)
        ax.set_ylabel('Inter-Throughput Time (hours)', fontsize=11)
        ax.set_title('Time Series of Inter-Throughput Times', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        return fig


# Create the app
app = App(app_ui, server)
