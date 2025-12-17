"""
LuxBoat Due Date Calculator - BEGINNER VERSION
===============================================
Simplified version for students with no programming experience.

This version has:
- Fewer features (easier to understand)
- More comments (explains every line)
- Clear TODO sections
- Simpler structure
"""

from shiny import App, render, ui
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# ============================================================================
# DATA SECTION - This is our boat completion data from the case study
# ============================================================================

# These are the inter-throughput times in hours (time between boat completions)
# From Table 2.2 in the LuxBoat case study
boat_data = [
    32.5, 35.5, 40, 38.5, 29.5,      # First 5 boats
    37, 40, 49, 44, 33.5,            # Next 5 boats
    44, 37.5, 47, 49, 45,            # Next 5 boats
    37.5, 30, 32, 34.5, 34,          # Next 5 boats
    51, 48, 41.5, 39.5, 36,          # Next 5 boats
    31, 36, 41, 34                   # Last 4 boats
]

# ============================================================================
# STUDENT TODO SECTION - Try modifying these calculations!
# ============================================================================

def calculate_average(data):
    """
    Calculate the average (mean) of the data.
    
    TODO for students: What happens if you add more data points?
    """
    average = np.mean(data)
    return average


def calculate_variance(data):
    """
    Calculate the variance (how spread out the data is).
    
    Higher variance = more unpredictable times
    Lower variance = more consistent times
    
    TODO for students: What does ddof=1 do? (Answer: sample variance)
    """
    variance = np.var(data, ddof=1)
    return variance


def calculate_autocorrelation(data):
    """
    Calculate autocorrelation (are consecutive times related?).
    
    Positive autocorrelation: If one boat is slow, next is probably slow too
    Negative autocorrelation: Times alternate (fast, slow, fast, slow)
    Zero autocorrelation: Times are independent
    
    TODO for students: Print series_1 and series_2 to see what's happening
    """
    # Take all data except the last value
    series_1 = data[:-1]
    
    # Take all data except the first value
    series_2 = data[1:]
    
    # Calculate correlation between these two series
    correlation = np.corrcoef(series_1, series_2)[0, 1]
    
    return correlation


def calculate_due_date(data, num_boats, confidence_pct):
    """
    Main calculation: When will the order be ready?
    
    This function combines everything to give us a reliable due date.
    """
    # Convert confidence from percentage (90) to decimal (0.90)
    confidence = confidence_pct / 100.0
    
    # STEP 1: Calculate basic statistics
    mean_time = calculate_average(data)
    variance = calculate_variance(data)
    std_dev = np.sqrt(variance)
    
    # STEP 2: Calculate autocorrelation
    autocorr = calculate_autocorrelation(data)
    
    # STEP 3: Calculate expected time for all boats (in hours)
    # Formula: number of boats × average time per boat
    expected_hours = num_boats * mean_time
    
    # STEP 4: Adjust variance for autocorrelation
    # If autocorr is positive, we need MORE buffer time
    # If autocorr is zero, this multiplier = 1
    variance_adjustment = (1 + autocorr) / (1 - autocorr)
    adjusted_variance = variance_adjustment * num_boats * variance
    adjusted_std_dev = np.sqrt(adjusted_variance)
    
    # STEP 5: Get z-score for our confidence level
    # 90% confidence → z ≈ 1.28
    # 95% confidence → z ≈ 1.96
    z_score = stats.norm.ppf(confidence)
    
    # STEP 6: Calculate due date in hours
    # Formula: Expected time + (z-score × standard deviation)
    due_date_hours = expected_hours + (z_score * adjusted_std_dev)
    
    # STEP 7: Convert to days (plant works 24 hours/day)
    due_date_days = due_date_hours / 24
    expected_days = expected_hours / 24
    safety_days = due_date_days - expected_days
    
    # Return all the results
    return {
        'mean': mean_time,
        'std': std_dev,
        'autocorr': autocorr,
        'expected_days': expected_days,
        'due_date_days': due_date_days,
        'safety_days': safety_days,
        'z_score': z_score
    }

# ============================================================================
# END STUDENT TODO SECTION
# ============================================================================


# ============================================================================
# USER INTERFACE - What students see and interact with
# ============================================================================

app_ui = ui.page_fluid(
    # Title at the top
    ui.panel_title("🚤 LuxBoat Due Date Calculator (Beginner Version)"),
    
    # Instructions
    ui.markdown("""
    ### Welcome! 
    This calculator helps determine when a boat order will be ready.
    
    **Your job:** Adjust the sliders and observe what happens!
    """),
    
    ui.hr(),  # Horizontal line
    
    # Create two columns
    ui.layout_columns(
        # LEFT COLUMN: Input controls
        ui.card(
            ui.card_header("📊 Inputs"),
            
            # Slider for number of boats
            ui.input_slider(
                "num_boats",
                "How many boats are needed?",
                min=5,
                max=50,
                value=25,
                step=1
            ),
            
            # Slider for confidence level
            ui.input_slider(
                "confidence",
                "Confidence level (%):",
                min=50,
                max=99,
                value=90,
                step=1
            ),
            
            ui.markdown("""
            **Tip:** Try changing these sliders and watch the results update!
            """)
        ),
        
        # RIGHT COLUMN: Results
        ui.card(
            ui.card_header("✅ Results"),
            ui.output_text_verbatim("results_text"),
        ),
        
        col_widths=[6, 6]  # Equal width columns
    ),
    
    ui.hr(),
    
    # Visualization
    ui.card(
        ui.card_header("📈 Data Visualization"),
        ui.output_plot("histogram")
    ),
    
    ui.hr(),
    
    # Explanation section
    ui.card(
        ui.card_header("💡 Understanding the Results"),
        ui.output_ui("explanation")
    ),
    
    # Footer with student exercises
    ui.hr(),
    ui.markdown("""
    ### 🎓 Student Exercises
    
    **Exercise 1:** Change confidence from 90% to 95%. What happens to:
    - Due date? (increases)
    - Safety time? (increases)
    - Why? (Higher confidence needs more buffer)
    
    **Exercise 2:** Change boats from 25 to 50. What happens to:
    - Due date? (increases)
    - Is it exactly double? (No! Why not?)
    
    **Exercise 3:** Click "Edit code" and find the `boat_data` list.
    - Change the first value from 32.5 to 50
    - What happens to the average?
    - What happens to the due date?
    
    **Exercise 4:** Can you change the histogram color?
    - Find the line with `color='steelblue'`
    - Try: 'red', 'green', 'purple', or '#FF6347'
    """)
)


# ============================================================================
# SERVER LOGIC - The "brain" that does calculations
# ============================================================================

def server(input, output, session):
    """
    This function runs every time a slider moves.
    It calculates new results and updates the display.
    """
    
    @output
    @render.text
    def results_text():
        """
        Display the main results as text.
        """
        # Get current slider values
        boats = input.num_boats()
        conf = input.confidence()
        
        # Calculate results
        results = calculate_due_date(boat_data, boats, conf)
        
        # Format the output text
        output_text = f"""
╔═══════════════════════════════════════╗
║         CALCULATION RESULTS           ║
╚═══════════════════════════════════════╝

📦 Number of boats needed: {boats}
🎯 Confidence level: {conf}%

📊 STATISTICS:
   • Average time per boat: {results['mean']:.1f} hours
   • Standard deviation: {results['std']:.1f} hours
   • Autocorrelation: {results['autocorr']:.3f}

⏱️  TIMING:
   • Expected time (average): {results['expected_days']:.1f} days
   • Due date ({conf}% confidence): {results['due_date_days']:.1f} days
   • Safety time (buffer): {results['safety_days']:.1f} days

✅ INTERPRETATION:
   With {conf}% confidence, the order will be ready
   in {results['due_date_days']:.0f} days or less.
   
   This includes {results['safety_days']:.1f} extra days of
   safety time to account for variability.
        """
        
        return output_text
    
    @output
    @render.plot
    def histogram():
        """
        Create a histogram showing the distribution of times.
        """
        # TODO for students: Try changing the color!
        # TODO for students: Try changing bins from 10 to 15 or 20
        
        results = calculate_due_date(boat_data, input.num_boats(), input.confidence())
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Draw histogram
        ax.hist(boat_data, bins=10, edgecolor='black', 
                alpha=0.7, color='steelblue')
        
        # Add a line showing the average
        ax.axvline(results['mean'], color='red', linestyle='--', 
                   linewidth=2, label=f"Average: {results['mean']:.1f} hrs")
        
        # Labels and formatting
        ax.set_xlabel('Inter-Throughput Time (hours)', fontsize=12)
        ax.set_ylabel('Frequency (how many boats)', fontsize=12)
        ax.set_title('Distribution of Boat Completion Times', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        return fig
    
    @output
    @render.ui
    def explanation():
        """
        Provide an explanation based on current results.
        """
        results = calculate_due_date(boat_data, input.num_boats(), input.confidence())
        boats = input.num_boats()
        conf = input.confidence()
        
        # Determine autocorrelation strength
        if results['autocorr'] > 0.3:
            autocorr_msg = "**Strong positive correlation!** When one boat takes longer, the next boat tends to take longer too. This is why we need extra safety time."
        elif results['autocorr'] > 0.1:
            autocorr_msg = "**Moderate correlation detected.** There's some relationship between consecutive boat times."
        else:
            autocorr_msg = "**Low correlation.** Boat completion times are fairly independent."
        
        return ui.markdown(f"""
        ### What Do These Numbers Mean?
        
        **The Story:**
        Joseph needs to promise a delivery date for {boats} boats with {conf}% confidence.
        He can't just use the average time because:
        
        1. **Variability**: Some boats take {min(boat_data):.1f} hours, others take {max(boat_data):.1f} hours
        2. **Autocorrelation**: {autocorr_msg}
        3. **Reliability**: The customer wants to be {conf}% sure, not just 50% sure
        
        **The Solution:**
        - **Average time**: {results['expected_days']:.1f} days (50% chance of being done)
        - **Due date**: {results['due_date_days']:.1f} days ({conf}% chance of being done)
        - **Safety buffer**: {results['safety_days']:.1f} extra days for reliability
        
        This means there's only a {100-conf}% chance the order takes longer than {results['due_date_days']:.0f} days!
        """)


# Create and run the app
app = App(app_ui, server)
