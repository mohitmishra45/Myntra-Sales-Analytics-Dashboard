import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import plotly.figure_factory as ff
from io import BytesIO
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import joblib
from scipy import stats
import calendar
import google.generativeai as genai
from auth import check_auth, logout
from data_watcher import setup_data_watcher, check_data_updates

class SalesAnalyzer:
    def __init__(self):
        self.model = self.setup_gemini()
    
    @staticmethod
    def setup_gemini():
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            return model
        except Exception as e:
            st.error(f"Error configuring Gemini: {str(e)}")
            return None
    
    def analyze_sales_trends(self, df):
        """
        Analyze sales trends and generate insights
        
        Args:
            df (pandas.DataFrame): Sales dataset
        
        Returns:
            str: Analysis report
        """
        try:
            # Calculate key metrics
            total_sales = df['Discounted Price'].sum()
            total_orders = len(df)
            avg_order_value = df['Discounted Price'].mean()
            avg_rating = df['Ratings'].mean()
            
            # Calculate month-over-month growth
            df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
            monthly_sales = df.groupby('Month')['Discounted Price'].sum().reset_index()
            monthly_sales['Month'] = monthly_sales['Month'].astype(str)
            
            # Calculate growth rate
            monthly_sales['Growth'] = monthly_sales['Discounted Price'].pct_change() * 100
            
            # Get top performing categories
            top_categories = df.groupby('Category')['Discounted Price'].sum().nlargest(3)
            
            # Get top performing brands
            top_brands = df.groupby('Brand Name')['Discounted Price'].sum().nlargest(3)
            
            # Generate analysis report
            report = f"""
            ### Sales Performance Analysis
            
            #### Key Metrics
            - Total Sales: ₹{total_sales:,.2f}
            - Total Orders: {total_orders:,}
            - Average Order Value: ₹{avg_order_value:,.2f}
            - Average Rating: {avg_rating:.2f} ⭐
            
            #### Monthly Growth
            - Latest Month: {monthly_sales['Month'].iloc[-1]}
            - Latest Sales: ₹{monthly_sales['Discounted Price'].iloc[-1]:,.2f}
            - Growth Rate: {monthly_sales['Growth'].iloc[-1]:.1f}%
            
            #### Top Performing Categories
            {chr(10).join([f"- {cat}: ₹{sales:,.2f}" for cat, sales in top_categories.items()])}
            
            #### Top Performing Brands
            {chr(10).join([f"- {brand}: ₹{sales:,.2f}" for brand, sales in top_brands.items()])}
            
            #### Insights
            1. Sales Performance:
               - The business is showing {'positive' if monthly_sales['Growth'].iloc[-1] > 0 else 'negative'} growth
               - Average order value indicates {'high' if avg_order_value > 1000 else 'moderate'} customer spending
            
            2. Category Analysis:
               - {top_categories.index[0]} is the leading category
               - Category mix shows {'good' if len(top_categories) > 2 else 'limited'} diversification
            
            3. Brand Performance:
               - {top_brands.index[0]} is the top-performing brand
               - Brand portfolio shows {'strong' if top_brands.values[0] > total_sales * 0.3 else 'balanced'} concentration
            
            4. Customer Satisfaction:
               - Rating of {avg_rating:.2f} indicates {'high' if avg_rating > 4 else 'moderate'} customer satisfaction
               - {'Consider' if avg_rating < 4 else 'Maintain'} focus on product quality and service
            
            #### Recommendations
            1. Growth Strategy:
               - {'Focus on increasing order volume' if total_orders < 1000 else 'Maintain current growth rate'}
               - {'Consider expanding to new categories' if len(top_categories) < 3 else 'Optimize existing categories'}
            
            2. Brand Strategy:
               - {'Strengthen top brand performance' if top_brands.values[0] > total_sales * 0.3 else 'Maintain brand diversity'}
               - {'Consider adding new brands' if len(top_brands) < 3 else 'Focus on brand optimization'}
            
            3. Customer Experience:
               - {'Improve product quality' if avg_rating < 4 else 'Maintain high standards'}
               - {'Focus on customer feedback' if avg_rating < 4 else 'Continue gathering feedback'}
            """
            
            return report
            
        except Exception as e:
            return f"Error analyzing sales trends: {str(e)}"
    
    def analyze_sales_data(self, df, prompt):
        """
        Dynamically analyze sales data based on user prompt
        
        Args:
            df (pandas.DataFrame): Myntra sales dataset
            prompt (str): User's specific analysis request
        
        Returns:
            str: AI-generated analysis response
        """
        try:
            if self.model is None:
                return "Error: Could not initialize Gemini model"
            
            # Handle city-specific brand queries
            if "most selling brand in" in prompt.lower():
                # Extract city name from prompt
                city = prompt.lower().split("most selling brand in")[-1].strip()
                
                # Filter data for the specific city
                city_data = df[df['City'].str.lower() == city.lower()]
                
                if city_data.empty:
                    return f"No data found for the city: {city}"
                
                # Calculate top brands for the city
                city_brands = city_data.groupby('Brand Name')['Discounted Price'].sum().sort_values(ascending=False)
                
                if city_brands.empty:
                    return f"No brand data found for the city: {city}"
                
                # Get top 5 brands with detailed metrics
                top_brands = city_brands.head(5)
                brand_metrics = city_data[city_data['Brand Name'].isin(top_brands.index)].groupby('Brand Name').agg({
                    'Discounted Price': ['sum', 'count', 'mean'],
                    'Ratings': 'mean',
                    'Discount%': 'mean'
                }).round(2)
                
                # Flatten column names
                brand_metrics.columns = ['Total_Sales', 'Order_Count', 'Avg_Order_Value', 'Avg_Rating', 'Avg_Discount']
                brand_metrics = brand_metrics.sort_values('Total_Sales', ascending=False)
                
                # Generate focused response
                response = f"### Top Selling Brands in {city.title()}\n\n"
                
                for i, (brand, sales) in enumerate(top_brands.items(), 1):
                    metrics = brand_metrics.loc[brand]
                    response += f"{i}. **{brand}**\n"
                    response += f"   - Total Sales: ₹{metrics['Total_Sales']:,.2f}\n"
                    response += f"   - Number of Orders: {metrics['Order_Count']:,}\n"
                    response += f"   - Average Order Value: ₹{metrics['Avg_Order_Value']:,.2f}\n"
                    response += f"   - Average Rating: {metrics['Avg_Rating']:.2f} ⭐\n"
                    response += f"   - Average Discount: {metrics['Avg_Discount']:.1f}%\n\n"
                
                return response
            
            # Handle specific queries about categories, sub-categories, and brands
            elif "most selling category" in prompt.lower():
                # Calculate top categories by sales
                top_categories = df.groupby('Category')['Discounted Price'].sum().sort_values(ascending=False).head(5)
                response = "### Top Selling Categories\n\n"
                for i, (category, sales) in enumerate(top_categories.items(), 1):
                    response += f"{i}. **{category}**: ₹{sales:,.2f}\n"
                return response
            
            elif "most selling sub category" in prompt.lower():
                # Calculate top sub-categories by sales
                top_subcategories = df.groupby('Sub-category')['Discounted Price'].sum().sort_values(ascending=False).head(5)
                response = "### Top Selling Sub-categories\n\n"
                for i, (subcategory, sales) in enumerate(top_subcategories.items(), 1):
                    response += f"{i}. **{subcategory}**: ₹{sales:,.2f}\n"
                return response
            
            elif "most selling brand" in prompt.lower():
                # Calculate overall top brands by sales
                top_brands = df.groupby('Brand Name')['Discounted Price'].sum().sort_values(ascending=False).head(10)
                
                # Calculate additional metrics for top brands
                brand_metrics = df[df['Brand Name'].isin(top_brands.index)].groupby('Brand Name').agg({
                    'Discounted Price': ['sum', 'count', 'mean'],
                    'Ratings': 'mean',
                    'Discount%': 'mean'
                }).round(2)
                
                # Flatten column names
                brand_metrics.columns = ['Total_Sales', 'Order_Count', 'Avg_Order_Value', 'Avg_Rating', 'Avg_Discount']
                brand_metrics = brand_metrics.sort_values('Total_Sales', ascending=False)
                
                # Generate comprehensive response
                response = "### Overall Top Selling Brands\n\n"
                
                # Overall top brands
                for i, (brand, sales) in enumerate(top_brands.items(), 1):
                    metrics = brand_metrics.loc[brand]
                    response += f"{i}. **{brand}**\n"
                    response += f"   - Total Sales: ₹{metrics['Total_Sales']:,.2f}\n"
                    response += f"   - Number of Orders: {metrics['Order_Count']:,}\n"
                    response += f"   - Average Order Value: ₹{metrics['Avg_Order_Value']:,.2f}\n"
                    response += f"   - Average Rating: {metrics['Avg_Rating']:.2f} ⭐\n"
                    response += f"   - Average Discount: {metrics['Avg_Discount']:.1f}%\n\n"
                
                # Add state-wise breakdown for top 3 brands
                response += "### State-wise Performance of Top 3 Brands\n\n"
                top_3_brands = top_brands.head(3)
                
                for brand in top_3_brands.index:
                    brand_data = df[df['Brand Name'] == brand]
                    state_sales = brand_data.groupby('State')['Discounted Price'].sum().sort_values(ascending=False)
                    response += f"#### {brand}\n"
                    for state, sales in state_sales.items():
                        response += f"- {state}: ₹{sales:,.2f}\n"
                    response += "\n"
                
                return response
            
            # For other queries, use the existing context-based analysis
            context_data = self._prepare_context_data(df)
            
            # Construct an intelligent prompt that combines user request with data context
            full_prompt = f"""
            Context: This is a Myntra sales dataset with comprehensive information.

            Dataset Overview:
            {context_data}

            User Query: {prompt}

            Please provide a detailed, data-driven analysis that:
            1. Directly addresses the specific question or prompt
            2. Uses quantitative insights from the dataset
            3. Offers actionable recommendations
            4. Explains the reasoning behind the analysis
            """
            
            # Generate AI analysis
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"Error analyzing sales data: {str(e)}"
    
    def _prepare_context_data(self, df):
        """
        Prepare a comprehensive context summary from the dataset
        
        Args:
            df (pandas.DataFrame): Myntra sales dataset
        
        Returns:
            str: Formatted context summary
        """
        # Total sales and key metrics
        total_sales = df['Discounted Price'].sum()
        total_orders = len(df)
        unique_brands = df['Brand Name'].nunique()
        unique_categories = df['Category'].nunique()
        
        # Calculate brand metrics
        brand_metrics = df.groupby('Brand Name').agg({
            'Discounted Price': ['sum', 'count', 'mean'],
            'Ratings': 'mean',
            'Discount%': 'mean'
        }).round(2)
        
        # Flatten column names
        brand_metrics.columns = ['Total_Sales', 'Order_Count', 'Avg_Order_Value', 'Avg_Rating', 'Avg_Discount']
        brand_metrics = brand_metrics.sort_values('Total_Sales', ascending=False)
        
        # Get top 5 brands with detailed metrics
        top_brands = brand_metrics.head(5)
        
        # Calculate state-wise brand performance
        state_brand_sales = df.groupby(['State', 'Brand Name'])['Discounted Price'].sum().reset_index()
        state_brand_sales = state_brand_sales.sort_values(['State', 'Discounted Price'], ascending=[True, False])
        top_brands_by_state = state_brand_sales.groupby('State').first()
        
        # Get top 5 categories
        top_categories = df.groupby('Category')['Discounted Price'].sum().nlargest(5)
        
        context = f"""
        Dataset Metrics:
        - Total Sales: ₹{total_sales:,.2f}
        - Total Orders: {total_orders:,}
        - Unique Brands: {unique_brands}
        - Unique Categories: {unique_categories}

        Top 5 Brands by Sales:
        {top_brands.to_string()}

        Top Brand in Each State:
        {top_brands_by_state.to_string()}

        Top 5 Categories by Sales:
        {top_categories.to_string()}
        """
        
        return context
    
    def analyze_brand_performance(self, df):
        """Analyze brand performance metrics"""
        try:
            # Calculate brand-wise metrics
            brand_metrics = df.groupby('Brand Name').agg({
                'Discounted Price': ['sum', 'count', 'mean'],
                'Ratings': 'mean',
                'Discount%': 'mean'
            }).round(2)
            
            # Flatten column names
            brand_metrics.columns = ['Total_Sales', 'Order_Count', 'Avg_Order_Value', 'Avg_Rating', 'Avg_Discount']
            brand_metrics = brand_metrics.reset_index()
            
            # Sort by total sales
            brand_metrics = brand_metrics.sort_values('Total_Sales', ascending=False)
            
            return brand_metrics
        except Exception as e:
            return f"Error analyzing brand performance: {str(e)}"
    
    def create_visualizations(self, df):
        """Create comprehensive sales visualizations"""
        try:
            # Daily sales trend
            daily_trend = df.groupby('Date')['Discounted Price'].sum().reset_index()
            fig_daily = px.line(
                daily_trend,
                x='Date',
                y='Discounted Price',
                title='Daily Sales Trend',
                labels={'Discounted Price': 'Sales (₹)', 'Date': 'Date'}
            )
            fig_daily.update_traces(line_color='#FF3F6C')
            
            # Category performance
            cat_sales = df.groupby('Category')['Discounted Price'].sum().sort_values(ascending=True)
            fig_cat = px.bar(
                cat_sales,
                orientation='h',
                title='Sales by Category',
                labels={'value': 'Total Sales (₹)', 'Category': 'Category'}
            )
            fig_cat.update_traces(marker_color='#FF3F6C')
            
            # Monthly trend
            df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
            monthly_trend = df.groupby('Month')['Discounted Price'].sum().reset_index()
            monthly_trend['Month'] = monthly_trend['Month'].astype(str)
            fig_monthly = px.line(
                monthly_trend,
                x='Month',
                y='Discounted Price',
                title='Monthly Sales Trend',
                labels={'Discounted Price': 'Sales (₹)', 'Month': 'Month'}
            )
            fig_monthly.update_traces(line_color='#FF3F6C')
            
            return fig_daily, fig_cat, fig_monthly
            
        except Exception as e:
            st.error(f"Error creating visualizations: {str(e)}")
            return None, None, None

# Set page configuration with optimized settings
st.set_page_config(
    page_title="Myntra Sales Analytics Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="👕",
    menu_items={
        'Get Help': 'https://www.myntra.com/contact',
        'Report a bug': "https://www.myntra.com/contact",
        'About': "# Myntra Sales Analytics Pro\nA comprehensive analytics dashboard for Myntra sales data."
    }
)

# Add optimized CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@100;300;400;500;700&display=swap');
    
    .main {
        padding: 20px;
        font-family: 'Assistant', sans-serif;
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #282C3F;
        padding: 20px 0;
        text-align: center;
        margin-bottom: 30px;
        background: linear-gradient(120deg, #FF3F6C, #282C3F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-title {
        color: #282C3F;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    
    .metric-value {
        background: linear-gradient(120deg, #FF3F6C, #282C3F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px;
        font-weight: 600;
        margin: 0;
    }
    
    .star-icon {
        color: #FFD700;
        font-size: 24px;
        vertical-align: middle;
        -webkit-text-fill-color: #FFD700;
    }
    
    .analysis-box {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #eee;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .analysis-box:hover {
        transform: translateY(-5px);
    }
    
    .stButton button {
        background-color: #FF3F6C;
        color: white;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #FF1F4C;
    }
    
    .chart-container {
        background: transparent;
        padding: 10px 0;
        margin: 10px 0;
    }
    
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #FF3F6C;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* New styles for section headers */
    .section-header {
        color: #282C3F;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 20px 0 10px 0;
        padding: 0;
        border-bottom: 2px solid #FF3F6C;
        display: inline-block;
    }

    /* Style for plotly charts */
    .js-plotly-plot {
        background: white !important;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Remove box from headings */
    h2, h3, h4 {
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding: 0;
        border: none;
        background: none;
    }
    </style>
""", unsafe_allow_html=True)

# Add loading state
if 'loading' not in st.session_state:
    st.session_state.loading = True

# Check authentication before showing dashboard
if not check_auth():
    st.stop()

# Add logout button in sidebar
with st.sidebar:
    if st.button("Logout"):
        logout()

# Set up data watcher for real-time updates
EXCEL_PATH = "Myntra_dataset_large.csv"
data_watcher = setup_data_watcher(EXCEL_PATH)

# Check for data updates
check_data_updates()

# Optimize data loading with better caching and error handling
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_data():
    try:
        # Use data watcher to get latest data
        data = data_watcher.get_latest_data()
        
        if data is None:
            st.error("Failed to load data from the file. Please check if the file exists and is accessible.")
            return None
            
        # Check if Date column exists
        if 'Date' not in data.columns:
            st.error("The dataset must contain a 'Date' column.")
            return None
            
        # Data preprocessing with optimized operations
        # First, try to identify the date format
        sample_date = data['Date'].iloc[0]
        try:
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y/%m/%d',
                '%d.%m.%Y',
                '%Y.%m.%d'
            ]
            
            parsed_date = None
            used_format = None
            
            for date_format in date_formats:
                try:
                    parsed_date = pd.to_datetime(sample_date, format=date_format)
                    used_format = date_format
                    break
                except:
                    continue
            
            if parsed_date is None:
                # If no specific format works, try pandas default parser
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            else:
                # Use the identified format for all dates
                data['Date'] = pd.to_datetime(data['Date'], format=used_format, errors='coerce')
            
            # Check for invalid dates
            invalid_dates = data['Date'].isna()
            if invalid_dates.any():
                invalid_rows = data[invalid_dates]
                st.error(f"""
                    Found {invalid_dates.sum()} rows with invalid dates. 
                    First few problematic rows:
                    {invalid_rows[['Date']].head().to_string()}
                    
                    Please ensure all dates are in a valid format (e.g., YYYY-MM-DD, DD-MM-YYYY).
                """)
                return None
            
            # Calculate discounted price only if not already present
            if 'Discounted Price' not in data.columns:
                if 'Original Price' in data.columns and 'Discount%' in data.columns:
                    data['Discounted Price'] = data['Original Price'] * (1 - data['Discount%']/100)
                else:
                    st.error("Missing required columns for price calculation: 'Original Price' and 'Discount%'")
                    return None
            
            # Add commonly used aggregations as new columns
            data['Month'] = data['Date'].dt.to_period('M')
            data['Year'] = data['Date'].dt.year
            data['DayOfWeek'] = data['Date'].dt.dayofweek
            
            return data
            
        except Exception as e:
            st.error(f"Error processing dates: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Add data validation function
def validate_data(df):
    """Validate data structure and content"""
    try:
        # Check required columns
        required_columns = ['Date', 'Category', 'Brand Name', 'Discounted Price', 'Ratings', 'State', 'City']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        
        # Check for empty dataset
        if df.empty:
            st.error("Dataset is empty")
            return False
        
        # Validate date column
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            st.error("Date column is not in datetime format")
            return False
        
        if df['Date'].isna().any():
            st.error("Dataset contains invalid dates")
            return False
        
        # Validate numeric columns
        numeric_columns = ['Discounted Price', 'Ratings', 'Discount%']
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    st.error(f"Column '{col}' must contain numeric values")
                    return False
                if df[col].isna().any():
                    st.error(f"Column '{col}' contains missing values")
                    return False
        
        # Validate categorical columns
        categorical_columns = ['Category', 'Brand Name', 'State', 'City']
        for col in categorical_columns:
            if col in df.columns:
                if df[col].isna().any():
                    st.error(f"Column '{col}' contains missing values")
                    return False
        
        return True
        
    except Exception as e:
        st.error(f"Error during data validation: {str(e)}")
        return False

# Add performance optimization for data filtering
@st.cache_data(ttl=3600)
def filter_data(df, selected_states, selected_categories, start_date, end_date):
    """Optimized data filtering"""
    mask = (
        (df['Date'].dt.date >= start_date) &
        (df['Date'].dt.date <= end_date) &
        (df['Category'].isin(selected_categories)) &
        (df['State'].isin(selected_states))
    )
    return df[mask]

# Add optimized metric calculations
@st.cache_data(ttl=3600)
def calculate_metrics(df):
    """Calculate key metrics with optimized operations"""
    metrics = {
        'total_sales': df['Discounted Price'].sum(),
        'average_rating': df['Ratings'].mean(),
        'total_orders': len(df),
        'average_discount': df['Discount%'].mean(),
        'unique_customers': df['Customer ID'].nunique(),
        'unique_brands': df['Brand Name'].nunique(),
        'unique_categories': df['Category'].nunique()
    }
    return metrics

# Add optimized visualization functions
@st.cache_data(ttl=3600)
def create_sales_trend(df):
    """Create optimized sales trend visualization"""
    monthly_sales = df.groupby('Month')['Discounted Price'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Month'].astype(str)
    
    fig = px.line(
        monthly_sales,
        x='Month',
        y='Discounted Price',
        title="Monthly Sales Trend",
        template="plotly_white"
    )
    
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=3, color='#ff3f6c'),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        title_font=dict(size=20),
        xaxis_title="Month",
        yaxis_title="Total Sales (₹)",
        plot_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="white", font_size=14)
    )
    
    return fig

@st.cache_data(ttl=3600)
def create_category_distribution(df):
    """Create optimized category distribution visualization"""
    category_sales = df.groupby('Category')['Discounted Price'].sum()
    
    fig = px.pie(
        values=category_sales.values,
        names=category_sales.index,
        title="Sales by Category",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    
    fig.update_layout(
        title_font=dict(size=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

# Load and validate data
try:
    data = load_data()
    if data is None:
        st.error("Failed to load dataset. Please check if the file exists and is accessible.")
        st.stop()
    
    if not validate_data(data):
        st.error("Data validation failed. Please check the data format.")
        st.stop()
    
    st.session_state.loading = False
except Exception as e:
    st.error(f"Error initializing data: {str(e)}")
    st.stop()

# Show loading spinner
if st.session_state.loading:
    st.markdown("""
        <div class="loading">
            <div class="loading-spinner"></div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# Title with Myntra logo
st.markdown("""
    <div class="dashboard-title">
        <div class="logo-container">
            <img src="https://logolook.net/wp-content/uploads/2023/01/Myntra-Emblem-2048x1152.png" width="60px">
        </div>
        Myntra Sales Analytics Dashboard
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Advanced Filters")
    
    # Create tabs in sidebar for better organization
    filter_tab, analysis_tab, assistant_tab = st.tabs(["🎯 Filters", "📈 Analysis Options", "🤖 AI Assistant"])

    with filter_tab:
        # State filter with search
        all_states = sorted(data['State'].unique())
        selected_states = st.multiselect(
            "Select States",
            options=all_states,
            default=all_states[:5],
            help="Select at least one state to view the dashboard"
        )

        # Separate date filters
        st.markdown("### Date Range")
        
        # Start date selector
        start_date = st.date_input(
            "Start Date",
            value=data['Date'].min(),
            min_value=data['Date'].min(),
            max_value=data['Date'].max()
        )
        
        # End date selector
        end_date = st.date_input(
            "End Date",
            value=data['Date'].max(),
            min_value=data['Date'].min(),
            max_value=data['Date'].max()
        )

        # Add date validation
        if start_date > end_date:
            st.error("Error: End date must be after start date")
            st.stop()

        # Category filter with search and default selection
        all_categories = sorted(data['Category'].unique())
        selected_categories = st.multiselect(
            "Select Categories",
            options=all_categories,
            default=[all_categories[0]] if len(all_categories) > 0 else [],  # Default to first category if available
            help="Select at least one category"
        )

    with analysis_tab:
        # Analysis options
        show_trends = st.checkbox("Show Trend Analysis", True)
        show_predictions = st.checkbox("Show Sales Predictions", True)
        show_correlations = st.checkbox("Show Correlation Analysis", False)

# Validation checks
if not selected_states:
    st.warning("⚠️ Please select at least one state to view the dashboard.")
    st.stop()

if not selected_categories:
    st.warning("⚠️ Please select at least one category to view the dashboard.")
    st.stop()

# Direct filtering of the dataframe
filtered_df = data[
    (data['Date'].dt.date >= start_date) &
    (data['Date'].dt.date <= end_date) &
    (data['Category'].isin(selected_categories)) &
    (data['State'].isin(selected_states))
]

# Check if filtered data is empty
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Calculate KPI metrics based on filtered data
def calculate_kpis(df):
    return {
        'total_sales': df['Discounted Price'].sum(),
        'average_rating': df['Ratings'].mean(),
        'total_orders': len(df),
        'average_discount': df['Discount%'].mean()
    }

# Calculate KPIs from filtered data
kpi_metrics = calculate_kpis(filtered_df)

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)

# Display metrics in columns
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Sales</div>
            <div class="metric-value">₹{kpi_metrics['total_sales']:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Rating</div>
            <div class="metric-value">{kpi_metrics['average_rating']:.2f} <span class="star-icon">⭐</span></div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Orders</div>
            <div class="metric-value">{kpi_metrics['total_orders']:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Discount</div>
            <div class="metric-value">{kpi_metrics['average_discount']:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

# After displaying metrics, implement AI Assistant
def analyze_city_performance(df, target_city):
    """Analyze performance metrics for a specific city"""
    try:
        # Get city-specific data
        city_data = df[df['City'] == target_city]
        
        # Calculate key metrics
        metrics = {
            'total_sales': city_data['Discounted Price'].sum(),
            'order_count': len(city_data),
            'avg_order_value': city_data['Discounted Price'].mean(),
            'avg_rating': city_data['Ratings'].mean(),
            'avg_discount': city_data['Discount%'].mean(),
            'top_brands': city_data.groupby('Brand Name')['Discounted Price'].sum().nlargest(3).to_dict(),
            'top_categories': city_data.groupby('Category')['Discounted Price'].sum().nlargest(3).to_dict(),
            'customer_age_dist': city_data['Customer Age'].value_counts().to_dict()
        }
        
        # Get state average for comparison
        state = city_data['State'].iloc[0]
        state_data = df[df['State'] == state]
        state_avg_sales = state_data.groupby('City')['Discounted Price'].sum().mean()
        
        # Calculate performance gap
        sales_gap = ((state_avg_sales - metrics['total_sales']) / state_avg_sales) * 100
        
        return metrics, sales_gap, state_avg_sales
        
    except Exception as e:
        st.error(f"Error analyzing city performance: {str(e)}")
        return None, None, None

def generate_city_recommendations(metrics, sales_gap, state_avg_sales):
    """Generate targeted recommendations for improving city performance"""
    recommendations = []
    
    # Sales Performance Analysis
    recommendations.append({
        'category': 'Sales Performance',
        'analysis': f"""
        Current Performance:
        - Total Sales: ₹{metrics['total_sales']:,.2f}
        - Sales Gap: {sales_gap:.1f}% below state average
        - Average Order Value: ₹{metrics['avg_order_value']:,.2f}
        - Number of Orders: {metrics['order_count']}
        """,
        'recommendations': [
            f"Focus on increasing order volume to reach state average of ₹{state_avg_sales:,.2f}",
            "Implement targeted promotions to boost average order value",
            "Develop local marketing campaigns to increase brand awareness"
        ]
    })
    
    # Brand Strategy
    top_brands = metrics['top_brands']
    recommendations.append({
        'category': 'Brand Strategy',
        'analysis': f"""
        Top Performing Brands:
        {', '.join([f"{brand} (₹{sales:,.2f})" for brand, sales in top_brands.items()])}
        """,
        'recommendations': [
            "Expand inventory of top-performing brands",
            "Create brand-specific promotions",
            "Partner with local retailers to increase brand visibility"
        ]
    })
    
    # Category Focus
    top_categories = metrics['top_categories']
    recommendations.append({
        'category': 'Category Focus',
        'analysis': f"""
        Top Performing Categories:
        {', '.join([f"{category} (₹{sales:,.2f})" for category, sales in top_categories.items()])}
        """,
        'recommendations': [
            "Increase stock of top-performing categories",
            "Develop category-specific marketing campaigns",
            "Create bundle offers for popular categories"
        ]
    })
    
    # Customer Engagement
    recommendations.append({
        'category': 'Customer Engagement',
        'analysis': f"""
        Customer Metrics:
        - Average Rating: {metrics['avg_rating']:.2f} ⭐
        - Average Discount: {metrics['avg_discount']:.1f}%
        """,
        'recommendations': [
            "Implement customer loyalty program",
            "Increase social media presence",
            "Organize local events and pop-ups"
        ]
    })
    
    # Operational Improvements
    recommendations.append({
        'category': 'Operational Improvements',
        'analysis': "Based on current performance metrics",
        'recommendations': [
            "Optimize inventory management",
            "Improve delivery service",
            "Enhance customer support"
        ]
    })
    
    return recommendations

def prepare_ai_context(df):
    """Prepare comprehensive context for AI analysis"""
    try:
        # Calculate state-wise metrics including ratings
        state_performance = df.groupby('State').agg({
            'Discounted Price': ['sum', 'mean', 'count'],
            'Ratings': ['mean', 'count']  # Calculate mean rating and count of ratings per state
        }).round(2)
        
        summary = {
            'basic_metrics': {
                'total_sales': df['Discounted Price'].sum(),
                'total_orders': len(df),
                'avg_order_value': df['Discounted Price'].mean(),
                'avg_rating': df['Ratings'].mean(),
                'avg_discount': df['Discount%'].mean(),
                'date_range': f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
            },
            'top_performers': {
                'brands': df.groupby('Brand Name')['Discounted Price'].sum().nlargest(5).to_dict(),
                'categories': df.groupby('Category')['Discounted Price'].sum().nlargest(5).to_dict(),
                'cities': df.groupby('City')['Discounted Price'].sum().to_dict(),
                'states': df.groupby('State')['Discounted Price'].sum().to_dict()
            },
            'performance_metrics': {
                'category_performance': df.groupby('Category').agg({
                    'Discounted Price': ['sum', 'mean'],
                    'Ratings': 'mean'
                }).round(2).to_dict(),
                'monthly_sales': df.groupby(df['Date'].dt.strftime('%Y-%m'))['Discounted Price'].sum().to_dict(),
                'state_performance': state_performance.to_dict(),  # Now includes proper rating metrics
                'city_performance': df.groupby('City').agg({
                    'Discounted Price': ['sum', 'mean', 'count'],
                    'Ratings': ['mean', 'count']
                }).round(2).to_dict(),
                'brand_by_state': df.groupby(['State', 'Brand Name'])['Discounted Price'].sum().to_dict()
            }
        }
        return summary
    except Exception as e:
        st.error(f"Error preparing AI context: {str(e)}")
        return None

def generate_ai_prompt(user_question, context):
    """Generate a more structured and focused prompt"""
    # Sort cities by sales for better analysis
    city_sales = sorted(context['top_performers']['cities'].items(), key=lambda x: x[1])
    bottom_cities = city_sales[:5]  # Get bottom 5 cities
    top_cities = city_sales[-5:]    # Get top 5 cities
    
    # Get brand-wise sales for each state
    brand_by_state = {}
    for (state, brand), sales in context['performance_metrics']['brand_by_state'].items():
        if state not in brand_by_state:
            brand_by_state[state] = {}
        brand_by_state[state][brand] = sales
    
    # Format brand-wise sales for each state
    state_brand_sales = []
    for state, brands in brand_by_state.items():
        top_brand = max(brands.items(), key=lambda x: x[1])
        state_brand_sales.append(f"{state}: {top_brand[0]} (₹{top_brand[1]:,.2f})")
    
    # Format state-wise ratings with proper error handling
    state_ratings = []
    for state in context['top_performers']['states'].keys():
        try:
            state_metrics = context['performance_metrics']['state_performance']
            rating = state_metrics[('Ratings', 'mean')][state]
            count = state_metrics[('Ratings', 'count')][state]
            if pd.notna(rating) and pd.notna(count):
                state_ratings.append(f"{state}: {rating:.2f} ({count:,.0f} orders)")
            else:
                state_ratings.append(f"{state}: No ratings available")
        except:
            state_ratings.append(f"{state}: No ratings available")
    
    # Format city-wise ratings
    city_ratings = []
    for city, metrics in context['performance_metrics']['city_performance'].items():
        try:
            rating = metrics[('Ratings', 'mean')]
            count = metrics[('Ratings', 'count')]
            city_ratings.append(f"{city}: {rating:.2f} ({count} orders)")
        except:
            city_ratings.append(f"{city}: N/A")
    
    # Sort city ratings by rating value
    city_ratings.sort(key=lambda x: float(x.split(': ')[1].split(' ')[0]) if x.split(': ')[1] != 'N/A' else 0, reverse=True)
    top_city_ratings = city_ratings[:5]  # Top 5 cities by rating
    bottom_city_ratings = city_ratings[-5:]  # Bottom 5 cities by rating
    
    prompt = f"""
    You are a retail analytics expert analyzing Myntra sales data. Answer the following question using only the provided data:

    Question: {user_question}

    Available Data Summary:
    1. Time Period: {context['basic_metrics']['date_range']}
    2. Overall Performance:
       - Total Sales: ₹{context['basic_metrics']['total_sales']:,.2f}
       - Total Orders: {context['basic_metrics']['total_orders']:,}
       - Average Order Value: ₹{context['basic_metrics']['avg_order_value']:,.2f}
       - Average Rating: {context['basic_metrics']['avg_rating']:.2f}
    
    3. City Performance:
       - Top 5 Cities by Sales: {', '.join([f"{city}: ₹{sales:,.2f}" for city, sales in top_cities])}
       - Bottom 5 Cities by Sales: {', '.join([f"{city}: ₹{sales:,.2f}" for city, sales in bottom_cities])}
       - Top 5 Cities by Rating: {', '.join(top_city_ratings)}
       - Bottom 5 Cities by Rating: {', '.join(bottom_city_ratings)}
    
    4. State Performance:
       - State-wise Sales: {', '.join([f"{state}: ₹{sales:,.2f}" for state, sales in context['top_performers']['states'].items()])}
       - State-wise Ratings: {', '.join(state_ratings)}
       - Top Brand by State: {', '.join(state_brand_sales)}

    Provide a clear, data-driven answer with specific numbers and insights. If the question cannot be answered with the available data, explicitly state that.
    """
    return prompt

with st.sidebar:
    with assistant_tab:
        st.markdown("""
            <style>
            .chat-message {
                padding: 1.5rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                display: flex;
                flex-direction: column;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .assistant {
                background-color: #f0f2f6;
                border-left: 5px solid #FF3F6C;
            }
            .human {
                background-color: white;
                border-left: 5px solid #282C3F;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.subheader("💬 AI Sales Assistant")
        
        # Initialize session state variables
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Initialize sales_analyzer in session state
        if "sales_analyzer" not in st.session_state:
            st.session_state.sales_analyzer = SalesAnalyzer()
        
        # Display chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            if isinstance(content, str):
                content = content.replace("</div>", "").replace("<div>", "").strip()
            
                st.markdown(f"""
                    <div class="chat-message {role}">
                        {content}
                    </div>
                """, unsafe_allow_html=True)

        # Create a form for chat input
        with st.form(key="chat_form"):
            user_question = st.text_input("Ask me anything about the sales data:", key="user_question")
            submit_button = st.form_submit_button("Get Analysis")
            
            if submit_button and user_question:
                try:
                    with st.spinner("Analyzing data..."):
                        if "gaya" in user_question.lower():
                            # Analyze Gaya's performance
                            metrics, sales_gap, state_avg_sales = analyze_city_performance(filtered_df, "Gaya")
                            if metrics:
                                recommendations = generate_city_recommendations(metrics, sales_gap, state_avg_sales)
                                
                                # Format response
                                response = "### Gaya Sales Analysis & Recommendations\n\n"
                                
                                for rec in recommendations:
                                    response += f"""
                                    #### {rec['category']}
                                    {rec['analysis']}
                                    
                                    **Recommendations:**
                                    {chr(10).join(['- ' + r for r in rec['recommendations']])}
                                    
                                    """
                                
                                # Display response
                                st.markdown(response)
                                
                                # Add to chat history
                                st.session_state.chat_history.append({"role": "human", "content": user_question})
                                st.session_state.chat_history.append({"role": "assistant", "content": response})
                            else:
                                st.error("Unable to analyze Gaya's performance. Please check if Gaya is included in the selected filters.")
                        else:
                            # Handle other questions using existing context and prompt
                            context = prepare_ai_context(filtered_df)
                            if context:
                                prompt = generate_ai_prompt(user_question, context)
                                response = st.session_state.sales_analyzer.model.generate_content(prompt)
                                st.markdown("### Analysis Results")
                                st.markdown(response.text)
                                st.session_state.chat_history.append({"role": "human", "content": user_question})
                                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                            else:
                                st.error("Failed to prepare data context for analysis")
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")
        
        # Clear chat button outside the form
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# Sales Trend
st.markdown('<h2 class="section-header">📈 Sales Trend Over Time</h2>', unsafe_allow_html=True)
@st.cache_data
def get_monthly_sales(data):
    monthly_sales = data.groupby(data['Date'].dt.to_period("M"))['Discounted Price'].sum().reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].astype(str)
    return monthly_sales

monthly_sales = get_monthly_sales(filtered_df)
fig_trend = px.line(monthly_sales, x='Date', y='Discounted Price',
                    title="Monthly Sales Trend",
                    template="plotly_white")
fig_trend.update_traces(mode="lines+markers", line=dict(width=3, color='#ff3f6c'), marker=dict(size=8))
fig_trend.update_layout(
    title_font=dict(size=20),
    xaxis_title="Month",
    yaxis_title="Total Sales (₹)",
    plot_bgcolor='rgba(0,0,0,0)',
    hoverlabel=dict(bgcolor="white", font_size=14)
)
st.plotly_chart(fig_trend, use_container_width=True)

# Category and Sub-category Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h2 class="section-header">🏷️ Category Distribution</h2>', unsafe_allow_html=True)
    category_sales = filtered_df.groupby('Category')['Discounted Price'].sum()
    fig_category_pie = px.pie(values=category_sales.values, 
                            names=category_sales.index,
                            title="Sales by Category",
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Reds_r)
    fig_category_pie.update_layout(
        title_font=dict(size=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_category_pie, use_container_width=True)

with col2:
    st.markdown('<h2 class="section-header">📊 Sub-category Distribution</h2>', unsafe_allow_html=True)
    subcategory_sales = filtered_df.groupby('Sub-category')['Discounted Price'].sum().sort_values(ascending=False).head(10)
    top_10_subcategories = subcategory_sales.head(10)
    top_10_subcategories_pct = (top_10_subcategories / top_10_subcategories.sum() * 100).round(2)

    # Custom color palette (red shades)
    colors = [
        '#67000D',  # Dark red
        '#A50F15',
        '#CB181D',
        '#EF3B2C',
        '#FB6A4A',
        '#FC9272',
        '#FCBBA1',
        '#FEE0D2',
        '#FFF5F0',
        '#FFF5F0'
    ]

    # Create pie chart with customizations
    fig = go.Figure(data=[go.Pie(
        labels=top_10_subcategories_pct.index,
        values=top_10_subcategories_pct.values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='outside',
        texttemplate='%{label}<br>%{percent:.1f}%',
        showlegend=True,
        direction='clockwise',
        sort=True
    )])

    # Update layout with corrected legend orientation
    fig.update_layout(
        title="Top 10 Sub-categories by Sales",
        height=500,
        font=dict(size=12),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(size=10)
        ),
        margin=dict(l=20, r=120, t=70, b=20)
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

# Brand Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h2 class="section-header">🏢 Top Brands by Sales</h2>', unsafe_allow_html=True)
    @st.cache_data
    def get_top_brands(data):
        return data.groupby('Brand Name')['Discounted Price'].sum().sort_values(ascending=False).head(10)
    
    top_brands = get_top_brands(filtered_df)
    top_brands_df = pd.DataFrame({
        'Brand': top_brands.index,
        'Sales': top_brands.values
    })

    fig_brands = px.bar(
        data_frame=top_brands_df,
        x='Brand',
        y='Sales',
        title="Top 10 Brands by Sales",
        template="plotly_white",
        color='Sales',
        color_continuous_scale='Reds'
    )

    fig_brands.update_layout(
        xaxis_title="Brand",
        yaxis_title="Total Sales (₹)",
        height=400,
        xaxis_tickangle=45,
        plot_bgcolor='white',
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
        showlegend=False
    )

    fig_brands.update_traces(
        texttemplate='₹%{y:,.0f}',
        textposition='outside'
    )

    st.plotly_chart(fig_brands, use_container_width=True)

with col2:
    st.markdown('<h2 class="section-header">⭐ Brand Performance</h2>', unsafe_allow_html=True)
    @st.cache_data
    def get_brand_ratings(data):
        return data.groupby('Brand Name')['Ratings'].mean().sort_values(ascending=False).head(10)
    
    brand_ratings = get_brand_ratings(filtered_df)
    fig_ratings = px.bar(x=brand_ratings.index, y=brand_ratings.values,
                        title="Top 10 Brands by Rating",
                        template="plotly_white",
                        color=brand_ratings.values,
                        color_continuous_scale='Reds')
    fig_ratings.update_layout(
        title_font=dict(size=20),
        xaxis_title="Brand",
        yaxis_title="Average Rating",
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_ratings, use_container_width=True)

# Customer Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h2 class="section-header">👥 Customer Age Distribution</h2>', unsafe_allow_html=True)
    fig_age = px.histogram(filtered_df, x='Customer Age', nbins=20,
                          title="Customer Age Distribution",
                          template="plotly_white",
                          color_discrete_sequence=['#ff3f6c'])
    fig_age.update_layout(
        title_font=dict(size=20),
        xaxis_title="Age Group",
        yaxis_title="Number of Customers",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_age, use_container_width=True)

with col2:
    st.markdown('<h2 class="section-header">⭐ Rating Distribution</h2>', unsafe_allow_html=True)
    fig_rating = px.histogram(filtered_df, x='Ratings', nbins=10,
                            title="Product Ratings Distribution",
                            template="plotly_white",
                            color_discrete_sequence=['#ff3f6c'])
    fig_rating.update_layout(
        title_font=dict(size=20),
        xaxis_title="Rating",
        yaxis_title="Number of Products",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_rating, use_container_width=True)

# Geographical Analysis
st.markdown('<h2 class="section-header">📍 Geographical Analysis</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    @st.cache_data
    def get_state_sales(data):
        return data.groupby('State')['Discounted Price'].sum().sort_values(ascending=False)
    
    state_sales = get_state_sales(filtered_df)
    fig_state = px.bar(x=state_sales.index, y=state_sales.values,
                      title="State-wise Sales",
                      template="plotly_white",
                      color=state_sales.values,
                      color_continuous_scale='Reds')
    fig_state.update_layout(
        title_font=dict(size=20),
        xaxis_title="State",
        yaxis_title="Total Sales (₹)",
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_state, use_container_width=True)

with col2:
    @st.cache_data
    def get_city_sales(data):
        return data.groupby('City')['Discounted Price'].sum().sort_values(ascending=False).head(20)
    
    city_sales = get_city_sales(filtered_df)
    fig_city = px.bar(x=city_sales.index, y=city_sales.values,
                     title="Top 20 Cities by Sales",
                     template="plotly_white",
                     color=city_sales.values,
                     color_continuous_scale='Reds')
    fig_city.update_layout(
        title_font=dict(size=20),
        xaxis_title="City",
        yaxis_title="Total Sales (₹)",
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_city, use_container_width=True)

# Interactive Sales Trend Analysis
if show_trends:
    st.subheader("📈 Sales Trend Analysis")
    
    # Daily sales trend with moving average
    daily_sales = filtered_df.groupby('Date')['Discounted Price'].sum().reset_index()
    daily_sales['MA7'] = daily_sales['Discounted Price'].rolling(window=7).mean()
    daily_sales['MA30'] = daily_sales['Discounted Price'].rolling(window=30).mean()

    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['Discounted Price'],
        name='Daily Sales',
        line=dict(color='#FF3F6C', width=1)
    ))

    fig_trend.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['MA7'],
        name='7-Day MA',
        line=dict(color='#282C3F', width=2)
    ))

    fig_trend.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['MA30'],
        name='30-Day MA',
        line=dict(color='#00C853', width=2)
    ))

    fig_trend.update_layout(
        title="Sales Trend with Moving Averages",
        height=400,
        hovermode='x unified',
        showlegend=True
    )

    st.plotly_chart(fig_trend, use_container_width=True)


# Add Evolutionary Data Analysis section before AI Sales Analysis
st.markdown('<h2 class="section-header">📊 Evolutionary Data Analysis</h2>', unsafe_allow_html=True)

# Create tabs for different evolutionary analyses
evo_tab1, evo_tab2, evo_tab3 = st.tabs(["📈 Growth Trends", "🔄 Seasonal Patterns", "📊 Performance Evolution"])

with evo_tab1:
    st.subheader("Growth Trends Analysis")
    
    # Calculate monthly growth rates
    monthly_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M')).agg({
        'Discounted Price': 'sum',
        'Ratings': 'mean',
        'Discount%': 'mean'
    }).reset_index()
    
    monthly_data['Date'] = monthly_data['Date'].astype(str)
    monthly_data['Growth_Rate'] = monthly_data['Discounted Price'].pct_change() * 100
    
    # Create growth trend visualization
    fig_growth = go.Figure()
    
    fig_growth.add_trace(go.Scatter(
        x=monthly_data['Date'],
        y=monthly_data['Growth_Rate'],
        mode='lines+markers',
        name='Growth Rate',
        line=dict(color='#FF3F6C', width=2),
        marker=dict(size=8)
    ))
    
    fig_growth.update_layout(
        title="Monthly Sales Growth Rate",
        xaxis_title="Month",
        yaxis_title="Growth Rate (%)",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Display key growth metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_growth = monthly_data['Growth_Rate'].mean()
        st.metric("Average Monthly Growth", f"{avg_growth:.1f}%")
    
    with col2:
        max_growth = monthly_data['Growth_Rate'].max()
        st.metric("Highest Growth Month", f"{max_growth:.1f}%")
    
    with col3:
        min_growth = monthly_data['Growth_Rate'].min()
        st.metric("Lowest Growth Month", f"{min_growth:.1f}%")

with evo_tab2:
    st.subheader("Seasonal Pattern Analysis")
    
    # Calculate seasonal metrics
    filtered_df['Month'] = filtered_df['Date'].dt.month
    seasonal_data = filtered_df.groupby('Month').agg({
        'Discounted Price': ['sum', 'mean', 'count'],
        'Ratings': 'mean',
        'Discount%': 'mean'
    }).round(2)
    
    # Flatten column names
    seasonal_data.columns = ['Total_Sales', 'Avg_Sale', 'Order_Count', 'Avg_Rating', 'Avg_Discount']
    
    # Create seasonal pattern visualization
    fig_seasonal = go.Figure()
    
    fig_seasonal.add_trace(go.Bar(
        x=seasonal_data.index,
        y=seasonal_data['Total_Sales'],
        name='Total Sales',
        marker_color='#FF3F6C'
    ))
    
    fig_seasonal.update_layout(
        title="Monthly Sales Distribution",
        xaxis_title="Month",
        yaxis_title="Total Sales (₹)",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Display seasonal insights
    st.markdown("""
        ### Seasonal Insights
        1. Peak Sales Months: {}
        2. Off-Peak Months: {}
        3. Best Discount Months: {}
    """.format(
        ', '.join([calendar.month_name[m] for m in seasonal_data.nlargest(3, 'Total_Sales').index]),
        ', '.join([calendar.month_name[m] for m in seasonal_data.nsmallest(3, 'Total_Sales').index]),
        ', '.join([calendar.month_name[m] for m in seasonal_data.nlargest(3, 'Avg_Discount').index])
    ))

with evo_tab3:
    st.subheader("Performance Evolution")
    
    # Calculate performance metrics over time
    performance_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M')).agg({
        'Discounted Price': ['sum', 'mean'],
        'Ratings': 'mean',
        'Discount%': 'mean'
    }).round(2)
    
    # Flatten column names
    performance_data.columns = ['Total_Sales', 'Avg_Sale', 'Avg_Rating', 'Avg_Discount']
    performance_data = performance_data.reset_index()
    performance_data['Date'] = performance_data['Date'].astype(str)
    
    # Create performance evolution visualization
    fig_performance = go.Figure()
    
    fig_performance.add_trace(go.Scatter(
        x=performance_data['Date'],
        y=performance_data['Avg_Rating'],
        mode='lines+markers',
        name='Average Rating',
        line=dict(color='#FF3F6C', width=2),
        marker=dict(size=8)
    ))
    
    fig_performance.update_layout(
        title="Customer Rating Evolution",
        xaxis_title="Month",
        yaxis_title="Average Rating",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_performance, use_container_width=True)
    
    # Display performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            ### Sales Evolution
            - Starting Sales: ₹{:,.2f}
            - Current Sales: ₹{:,.2f}
            - Growth: {:.1f}%
        """.format(
            performance_data['Total_Sales'].iloc[0],
            performance_data['Total_Sales'].iloc[-1],
            ((performance_data['Total_Sales'].iloc[-1] - performance_data['Total_Sales'].iloc[0]) / 
             performance_data['Total_Sales'].iloc[0] * 100)
        ))
    
    with col2:
        st.markdown("""
            ### Rating Evolution
            - Starting Rating: {:.2f}
            - Current Rating: {:.2f}
            - Change: {:.2f}
        """.format(
            performance_data['Avg_Rating'].iloc[0],
            performance_data['Avg_Rating'].iloc[-1],
            performance_data['Avg_Rating'].iloc[-1] - performance_data['Avg_Rating'].iloc[0]
        ))
# Sales Prediction Section
if show_predictions:
    st.subheader("🔮 Sales Prediction")
    
    def prepare_sales_data(df):
        """
        Prepare daily sales data for forecasting
        """
        # Create a copy of the dataframe
        df = df.copy()
        
        # Ensure Date column is datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Group by date and calculate daily metrics
        daily_sales = df.groupby('Date').agg({
            'Discounted Price': ['sum', 'count']
        }).reset_index()
        
        # Flatten column names
        daily_sales.columns = ['Date', 'Total_Sales', 'Number_of_Orders']
        
        # Add time-based features
        daily_sales['Year'] = daily_sales['Date'].dt.year
        daily_sales['Month'] = daily_sales['Date'].dt.month
        daily_sales['DayOfWeek'] = daily_sales['Date'].dt.dayofweek
        daily_sales['DayOfMonth'] = daily_sales['Date'].dt.day
        
        # Sort by date
        daily_sales = daily_sales.sort_values('Date')
        
        return daily_sales

# Define the AI Analysis tabs first
st.header("🤖 AI Sales Analysis & Optimization")
ai_tab1, ai_tab2, ai_tab3 = st.tabs(["📉 Low Performance Analysis", "📈 AI-Powered Sales Forecast", "💡 Optimization Suggestions"])

# Now use the tabs
with ai_tab1:
    st.subheader("📉 Low Performance Analysis")
    # Analyze low performing areas
    def analyze_low_performance(df):
        try:
            # Calculate key metrics by city without nested renamers
            city_metrics = df.groupby(['State', 'City']).agg({
                'Discounted Price': ['sum', 'count', 'mean'],
                'Ratings': 'mean',
                'Discount%': 'mean'
            }).round(2)
            
            # Flatten and rename columns explicitly
            city_metrics.columns = ['Total_Sales', 'Order_Count', 'Avg_Order_Value', 'Avg_Rating', 'Avg_Discount']
            
            # Reset index to make State and City accessible
            city_metrics = city_metrics.reset_index()
            
            # Find the lowest performing city in each state
            low_performing = []
            for state in city_metrics['State'].unique():
                state_cities = city_metrics[city_metrics['State'] == state]
                lowest_city = state_cities.loc[state_cities['Total_Sales'].idxmin()]
                low_performing.append(lowest_city)
            
            low_performing = pd.DataFrame(low_performing)
            low_performing = low_performing.sort_values('Total_Sales')
            
            return low_performing, city_metrics
            
        except Exception as e:
            st.error(f"Error in low performance analysis: {str(e)}")
            return pd.DataFrame(), pd.DataFrame()

    low_performing_cities, all_city_metrics = analyze_low_performance(filtered_df)
    
    if not low_performing_cities.empty:
        for _, city in low_performing_cities.iterrows():
            with st.expander(f"🔍 {city['City']}, {city['State']} (Lowest Sales in {city['State']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Sales", f"₹{city['Total_Sales']:,.2f}")
                    st.metric("Order Count", f"{city['Order_Count']:,}")
                
                with col2:
                    st.metric("Average Order Value", f"₹{city['Avg_Order_Value']:,.2f}")
                    st.metric("Average Rating", f"{city['Avg_Rating']:.2f} ⭐")
                
                # Calculate state average for comparison
                state_data = filtered_df[filtered_df['State'] == city['State']]
                state_avg = state_data['Discounted Price'].mean()
                sales_gap = ((state_avg - city['Total_Sales']) / state_avg) * 100
                
                st.markdown(f"""
                    ### Performance Analysis
                    - This is the lowest performing city in {city['State']}
                    - Sales are **{sales_gap:.1f}%** below state average
                    - Average discount rate: **{city['Avg_Discount']:.1f}%**
                    - Customer rating: **{city['Avg_Rating']:.1f}** out of 5
                    
                    ### Verification
                    - Total cities in {city['State']}: {len(state_data['City'].unique())}
                    - State average sales: ₹{state_avg:,.2f}
                    {
                        '- Next lowest city sales: ' + state_data.groupby('City')['Discounted Price'].sum().nsmallest(2).index[1] 
                        if len(state_data['City'].unique()) > 1 
                        else '- No other cities in this state for comparison'
                    }
                """)

with ai_tab2:
    st.subheader("🔮 AI-Powered Sales Analysis")
    
    try:
        # Initialize analyzer
        analyzer = SalesAnalyzer()
        
        if st.button("Generate AI Sales Analysis", key="generate_analysis"):
            with st.spinner("Analyzing sales data with AI..."):
                # Get AI analysis
                analysis = analyzer.analyze_sales_trends(filtered_df)
                
                # Create tabs
                analysis_tab, viz_tab = st.tabs(["AI Analysis", "Visualizations"])
                
                with analysis_tab:
                    # Style for analysis card
                    st.markdown("""
                        <style>
                        .analysis-card {
                            background-color: #ffffff;
                            border-radius: 10px;
                            padding: 20px;
                            margin: 10px 0;
                            border-left: 5px solid #FF3F6C;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Display analysis
                    st.markdown(f'<div class="analysis-card">{analysis}</div>', 
                              unsafe_allow_html=True)
                
                with viz_tab:
                    # Get visualizations
                    fig_daily, fig_cat, fig_monthly = analyzer.create_visualizations(filtered_df)
                    
                    # Display visualizations
                    if fig_daily is not None:
                        st.plotly_chart(fig_daily, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.plotly_chart(fig_cat, use_container_width=True)
                        with col2:
                            st.plotly_chart(fig_monthly, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error in AI analysis: {str(e)}")
        st.info("Please check your Gemini API configuration and data format.")

with ai_tab3:
    st.subheader("💡 Optimization Suggestions")
    
    def generate_optimization_suggestions(city_data, df):
        suggestions = []
        
        # Analyze successful patterns
        successful_cities = df.groupby('City')['Discounted Price'].sum().nlargest(5)
        top_categories = df[df['City'].isin(successful_cities.index)]['Category'].value_counts()
        peak_months = df[df['City'].isin(successful_cities.index)]['Date'].dt.month.value_counts()
        
        # Generate Product Mix suggestion with safety checks
        category_suggestion = "Focus on top-performing categories:\n"
        for i in range(min(3, len(top_categories))):
            category_suggestion += f"{i+1}. {top_categories.index[i]} ({top_categories.values[i]} sales)\n"
        
        suggestions.append({
            'category': 'Product Mix Optimization',
            'suggestion': category_suggestion
        })
        
        # Seasonal strategy with safety checks
        peak_months_names = [datetime(2024, m, 1).strftime('%B') for m in peak_months.index[:min(3, len(peak_months))]]
        seasonal_suggestion = "Increase marketing efforts during peak months:\n"
        for i, month in enumerate(peak_months_names):
            seasonal_suggestion += f"{i+1}. {month}\n"
        
        suggestions.append({
            'category': 'Seasonal Strategy',
            'suggestion': seasonal_suggestion
        })
        
        # Pricing strategy
        avg_discount = df[df['City'].isin(successful_cities.index)]['Discount%'].mean()
        suggestions.append({
            'category': 'Pricing Strategy',
            'suggestion': f"""
            - Optimize discount rate (successful cities average: {avg_discount:.1f}%)
            - Implement dynamic pricing during peak seasons
            - Consider location-based pricing strategies
            """
        })
        
        # Add market analysis
        suggestions.append({
            'category': 'Market Analysis',
            'suggestion': f"""
            For {city_data['City']}, {city_data['State']}:
            - Current Performance:
              * Total Sales: ₹{city_data['Total_Sales']:,.2f}
              * Order Count: {city_data['Order_Count']}
              * Average Order Value: ₹{city_data['Avg_Order_Value']:,.2f}
            
            Recommended Actions:
            1. Focus on customer acquisition through targeted marketing
            2. Improve product visibility and availability
            3. Enhance local marketing initiatives
            """
        })
        
        # Add operational suggestions
        suggestions.append({
            'category': 'Operational Improvements',
            'suggestion': """
            1. Inventory Management:
               - Optimize stock levels based on local demand
               - Improve supply chain efficiency
               - Reduce delivery times
            
            2. Customer Experience:
               - Implement local customer support
               - Enhance return and exchange processes
               - Develop location-specific promotions
            
            3. Marketing Strategy:
               - Partner with local influencers
               - Organize local events and pop-ups
               - Increase social media presence
            """
        })
        
        return suggestions

    # Update the display section
    if not low_performing_cities.empty:
        for _, city in low_performing_cities.iterrows():
            with st.expander(f"📌 Optimization Plan for {city['City']}, {city['State']}"):
                try:
                    suggestions = generate_optimization_suggestions(city, filtered_df)
                    
                    for suggestion in suggestions:
                        st.markdown(f"""
                            #### {suggestion['category']}
                            {suggestion['suggestion']}
                        """)
                    
                    # Add performance metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sales Gap", 
                                f"₹{abs(city['Total_Sales'] - filtered_df.groupby('City')['Discounted Price'].mean().mean()):,.2f}")
                    with col2:
                        st.metric("Current Rating", f"{city['Avg_Rating']:.1f} ⭐")
                    with col3:
                        st.metric("Current Discount", f"{city['Avg_Discount']:.1f}%")
                
                except Exception as e:
                    st.warning(f"Unable to generate complete suggestions for {city['City']} due to insufficient data. Basic recommendations provided.")
                    st.markdown("""
                        ### Basic Recommendations:
                        1. **Market Research:**
                           - Conduct local market analysis
                           - Understand customer preferences
                           - Identify competition
                        
                        2. **Marketing:**
                           - Increase local advertising
                           - Build brand awareness
                           - Engage with local community
                        
                        3. **Operations:**
                           - Optimize inventory
                           - Improve delivery service
                           - Enhance customer support
                    """)
        # Update the display section
        if not low_performing_cities.empty:
            for _, city in low_performing_cities.iterrows():
                with st.expander(f"📌 Optimization Plan for {city['City']}, {city['State']}"):
                    try:
                        suggestions = generate_optimization_suggestions(city, filtered_df)
                        
                        for suggestion in suggestions:
                            st.markdown(f"""
                                #### {suggestion['category']}
                                {suggestion['suggestion']}
                            """)
                        
                        # Add performance metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Sales Gap", 
                                    f"₹{abs(city['Total_Sales'] - filtered_df.groupby('City')['Discounted Price'].mean().mean()):,.2f}")
                        with col2:
                            st.metric("Current Rating", f"{city['Avg_Rating']:.1f} ⭐")
                        with col3:
                            st.metric("Current Discount", f"{city['Avg_Discount']:.1f}%")
                    
                    except Exception as e:
                        st.warning(f"Unable to generate complete suggestions for {city['City']} due to insufficient data. Basic recommendations provided.")
                        st.markdown("""
                            ### Basic Recommendations:
                            1. **Market Research:**
                               - Conduct local market analysis
                               - Understand customer preferences
                               - Identify competition
                            
                            2. **Marketing:**
                               - Increase local advertising
                               - Build brand awareness
                               - Engage with local community
                            
                            3. **Operations:**
                               - Optimize inventory
                               - Improve delivery service
                               - Enhance customer support
                        """)
        else:
            st.info("No low-performing cities detected in the current selection.")

# Correlation Analysis
if show_correlations:
    st.subheader("🔍 Correlation Analysis")
    
    # Calculate correlations
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    corr_matrix = filtered_df[numeric_cols].corr()
    
    # Create heatmap
    fig_corr = px.imshow(
        corr_matrix,
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    
    fig_corr.update_layout(
        title="Feature Correlation Heatmap",
        height=500
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)

# Download filtered data option
def download_csv():
    csv = filtered_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="myntra_filtered_data.csv">Download Filtered Data</a>'
    return href

st.sidebar.markdown("---")
st.sidebar.markdown(download_csv(), unsafe_allow_html=True)

    # Footer with dashboard info
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        Dashboard last updated: {}
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
