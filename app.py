import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="BMI & Health Calculator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bmi-result {
        font-size: 2rem;
        font-weight: bold;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .healthy { background-color: #d4edda; color: #155724; }
    .overweight { background-color: #fff3cd; color: #856404; }
    .obese { background-color: #f8d7da; color: #721c24; }
    .underweight { background-color: #e2e3e5; color: #383d41; }
</style>
""", unsafe_allow_html=True)

class HealthCalculator:
    def __init__(self):
        self.bmi_categories = {
            "Underweight": (0, 18.4),
            "Normal weight": (18.5, 24.9),
            "Overweight": (25, 29.9),
            "Obesity Class I": (30, 34.9),
            "Obesity Class II": (35, 39.9),
            "Obesity Class III": (40, float('inf'))
        }

    def calculate_bmi(self, weight, height, unit_system):
        """Calculate BMI based on metric or imperial units"""
        if unit_system == "Metric (kg, cm)":
            # Convert cm to meters
            height_m = height / 100
            bmi = weight / (height_m ** 2)
        else:  # Imperial (lbs, inches)
            bmi = (weight / (height ** 2)) * 703

        return round(bmi, 1)

    def get_bmi_category(self, bmi):
        """Determine BMI category"""
        for category, (min_bmi, max_bmi) in self.bmi_categories.items():
            if min_bmi <= bmi <= max_bmi:
                return category
        return "Unknown"

    def calculate_calories(self, age, weight, height, gender, activity_level, goal):
        """Calculate daily calorie needs using Mifflin-St Jeor Equation"""
        if gender == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Activity multipliers
        activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly active": 1.375,
            "Moderately active": 1.55,
            "Very active": 1.725,
            "Extremely active": 1.9
        }

        maintenance_calories = bmr * activity_multipliers.get(activity_level, 1.2)

        # Adjust for goal
        goal_adjustments = {
            "Lose weight": -500,
            "Maintain weight": 0,
            "Gain weight": 500
        }

        return int(maintenance_calories + goal_adjustments.get(goal, 0))

    def calculate_ideal_weight(self, height, unit_system):
        """Calculate ideal weight range"""
        if unit_system == "Metric (kg, cm)":
            height_m = height / 100
            min_ideal = 18.5 * (height_m ** 2)
            max_ideal = 24.9 * (height_m ** 2)
        else:
            min_ideal = (18.5 * (height ** 2)) / 703
            max_ideal = (24.9 * (height ** 2)) / 703

        return round(min_ideal, 1), round(max_ideal, 1)

def main():
    calculator = HealthCalculator()

    # Header
    st.markdown('<h1 class="main-header">🏥 BMI & Health Calculator</h1>', unsafe_allow_html=True)

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Calculator",
                                   ["BMI Calculator", "Calorie Calculator", "Health Analysis", "About"])

    if app_mode == "BMI Calculator":
        show_bmi_calculator(calculator)
    elif app_mode == "Calorie Calculator":
        show_calorie_calculator(calculator)
    elif app_mode == "Health Analysis":
        show_health_analysis(calculator)
    else:
        show_about()

def show_bmi_calculator(calculator):
    st.header("📊 BMI Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Input Details")
        unit_system = st.radio("Select Unit System",
                              ["Metric (kg, cm)", "Imperial (lbs, inches)"])

        if unit_system == "Metric (kg, cm)":
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
        else:
            weight = st.number_input("Weight (lbs)", min_value=1.0, max_value=600.0, value=154.0, step=0.1)
            height = st.number_input("Height (inches)", min_value=20.0, max_value=100.0, value=67.0, step=0.1)

        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        gender = st.radio("Gender", ["Male", "Female"])

    with col2:
        if st.button("Calculate BMI", use_container_width=True):
            bmi = calculator.calculate_bmi(weight, height, unit_system)
            category = calculator.get_bmi_category(bmi)
            min_ideal, max_ideal = calculator.calculate_ideal_weight(height, unit_system)

            # Display BMI result with color coding
            st.subheader("Results")

            # Color code based on BMI category
            if category == "Normal weight":
                css_class = "healthy"
            elif category in ["Overweight", "Obesity Class I"]:
                css_class = "overweight"
            elif category in ["Obesity Class II", "Obesity Class III"]:
                css_class = "obese"
            else:
                css_class = "underweight"

            st.markdown(f'<div class="bmi-result {css_class}">BMI: {bmi}<br>{category}</div>',
                       unsafe_allow_html=True)

            # Additional information
            st.info(f"**Ideal weight range:** {min_ideal} - {max_ideal} {'kg' if unit_system == 'Metric (kg, cm)' else 'lbs'}")

            # BMI Chart
            st.subheader("BMI Categories")
            categories = list(calculator.bmi_categories.keys())
            ranges = [f"{calculator.bmi_categories[cat][0]}-{calculator.bmi_categories[cat][1]}"
                     for cat in categories]

            chart_data = pd.DataFrame({
                'Category': categories,
                'BMI Range': ranges
            })
            st.dataframe(chart_data, use_container_width=True)

def show_calorie_calculator(calculator):
    st.header("🔥 Calorie Calculator")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        age = st.number_input("Age", min_value=1, max_value=120, value=25, key="calorie_age")
        gender = st.radio("Gender", ["Male", "Female"], key="calorie_gender")

        unit_system = st.radio("Unit System",
                              ["Metric (kg, cm)", "Imperial (lbs, inches)"],
                              key="calorie_units")

        if unit_system == "Metric (kg, cm)":
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1, key="calorie_weight")
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1, key="calorie_height")
        else:
            weight = st.number_input("Weight (lbs)", min_value=1.0, max_value=600.0, value=154.0, step=0.1, key="calorie_weight")
            height = st.number_input("Height (inches)", min_value=20.0, max_value=100.0, value=67.0, step=0.1, key="calorie_height")

    with col2:
        st.subheader("Activity & Goals")
        activity_level = st.selectbox(
            "Activity Level",
            ["Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active"]
        )

        goal = st.radio(
            "Your Goal",
            ["Lose weight", "Maintain weight", "Gain weight"]
        )

        if st.button("Calculate Calories", use_container_width=True):
            # Convert height to cm if imperial
            if unit_system == "Imperial (lbs, inches)":
                height_cm = height * 2.54
                weight_kg = weight * 0.453592
            else:
                height_cm = height
                weight_kg = weight

            calories = calculator.calculate_calories(age, weight_kg, height_cm, gender, activity_level, goal)

            st.success(f"**Daily Calorie Needs:** {calories} calories")

            # Macronutrient breakdown
            st.subheader("Recommended Macronutrients")

            col_protein, col_carbs, col_fat = st.columns(3)

            with col_protein:
                protein_cal = calories * 0.3
                protein_grams = int(protein_cal / 4)
                st.metric("Protein", f"{protein_grams}g", "30%")

            with col_carbs:
                carbs_cal = calories * 0.50
                carbs_grams = int(carbs_cal / 4)
                st.metric("Carbohydrates", f"{carbs_grams}g", "50%")

            with col_fat:
                fat_cal = calories * 0.20
                fat_grams = int(fat_cal / 9)
                st.metric("Fat", f"{fat_grams}g", "20%")

def show_health_analysis(calculator):
    st.header("📈 Health Analysis")

    st.subheader("BMI Trend Analysis")

    # Generate sample data for visualization
    dates = pd.date_range(start='2024-01-01', end='2024-12-01', freq='M')
    sample_bmi = [22.5, 22.8, 23.1, 22.9, 23.5, 23.8, 24.1, 24.3, 24.0, 23.8, 23.6, 23.4]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, sample_bmi, marker='o', linewidth=2, markersize=6)
    ax.axhline(y=18.5, color='red', linestyle='--', alpha=0.7, label='Underweight')
    ax.axhline(y=24.9, color='green', linestyle='--', alpha=0.7, label='Normal')
    ax.axhline(y=29.9, color='orange', linestyle='--', alpha=0.7, label='Overweight')

    ax.fill_between(dates, 18.5, 24.9, alpha=0.2, color='green')
    ax.fill_between(dates, 25, 29.9, alpha=0.2, color='orange')
    ax.fill_between(dates, 0, 18.4, alpha=0.2, color='red')
    ax.fill_between(dates, 30, 40, alpha=0.2, color='darkred')

    ax.set_xlabel('Date')
    ax.set_ylabel('BMI')
    ax.set_title('BMI Trend Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    # Health tips based on BMI
    st.subheader("Health Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **For Underweight (BMI < 18.5):**
        - Increase calorie intake with nutrient-dense foods
        - Include strength training exercises
        - Eat more frequent, smaller meals
        - Consult a healthcare provider
        """)

    with col2:
        st.info("""
        **For Overweight (BMI > 25):**
        - Create a calorie deficit
        - Increase physical activity
        - Focus on whole foods
        - Stay hydrated
        - Get adequate sleep
        """)

def show_about():
    st.header("ℹ️ About This App")

    st.markdown("""
    ## BMI & Health Calculator

    This application helps you track and understand your health metrics through various calculators:

    ### Features:
    - **BMI Calculator**: Calculate your Body Mass Index with detailed categorization
    - **Calorie Calculator**: Determine your daily calorie needs based on your goals
    - **Health Analysis**: Visualize trends and get personalized recommendations

    ### How to Use:
    1. Navigate between different calculators using the sidebar
    2. Input your personal information
    3. Get instant results and recommendations
    4. Track your progress over time

    ### BMI Categories:
    - **Underweight**: BMI less than 18.5
    - **Normal weight**: BMI 18.5–24.9
    - **Overweight**: BMI 25–29.9
    - **Obesity**: BMI 30 or greater

    **Disclaimer**: This app provides general health information and should not be used as a substitute for professional medical advice.
    """)

if __name__ == "__main__":
    main()
