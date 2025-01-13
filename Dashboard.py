import streamlit as st 
import pandas as pd
import boto3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from boto3.dynamodb.conditions import Key, Attr
import pytz

# AWS Configuration
AWS_ACCESS_KEY = 'AKIAZAI4HB6HIQOTKD5L'
AWS_SECRET_KEY = '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'
AWS_REGION = 'ap-southeast-1'
TABLE_NAME = 'Attendance'

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)
table = dynamodb.Table(TABLE_NAME)

# Tetapkan zona waktu Indonesia (WIB)
WIB = pytz.timezone('Asia/Jakarta')

def load_attendance_data(start_date=None, end_date=None):
    try:
        if start_date and end_date:
            response = table.scan(
                FilterExpression=Attr('AttendanceDate').between(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
            )
        else:
            today = datetime.now(WIB).strftime('%Y-%m-%d')
            response = table.scan(
                FilterExpression=Attr('AttendanceDate').eq(today)
            )
        
        items = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=Attr('AttendanceDate').between(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                ),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
            
        if not items:
            return pd.DataFrame({
                'PersonName': [],
                'Timestamp': [],
                'AttendanceDate': []
            })
            
        df = pd.DataFrame(items)
        # Konversi timestamp ke zona waktu WIB
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.tz_localize('UTC').dt.tz_convert('Asia/Jakarta')
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame({
            'PersonName': [],
            'Timestamp': [],
            'AttendanceDate': []
        })

def show_metrics(df, today):
    try:
        # Pastikan tanggal menggunakan zona waktu yang benar
        df['AttendanceDate'] = pd.to_datetime(df['AttendanceDate']).dt.tz_localize(None)
        today_df = df[df['AttendanceDate'].dt.date == today]
        
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            total_present = len(today_df['PersonName'].unique()) if not today_df.empty else 0
            st.metric("Total Kehadiran", total_present)
        
        with metric_cols[1]:
            early_birds = len(today_df[today_df['Timestamp'].dt.hour < 9]) if not today_df.empty else 0
            st.metric("Data Diterima", early_birds)
        
        with metric_cols[2]:
            if not today_df.empty:
                latest = today_df['Timestamp'].max()
                latest_str = latest.strftime('%H:%M') if pd.notnull(latest) else "N/A"
            else:
                latest_str = "N/A"
            st.metric("Terakhir Datang", latest_str)
        
        with metric_cols[3]:
            if not today_df.empty:
                avg_time = today_df['Timestamp'].mean()
                avg_time_str = avg_time.strftime('%H:%M') if pd.notnull(avg_time) else "N/A"
            else:
                avg_time_str = "N/A"
            st.metric("Rata-Rata Waktu Tiba", avg_time_str)
            
        return today_df
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return pd.DataFrame()

def plot_attendance_timeline(df):
    if df.empty:
        st.warning("No attendance data available for the selected date range.")
        return
    
    # Create a copy of the dataframe for timeline
    timeline_df = df.copy()
    
    # Add end time (15 minutes after check-in for visualization purposes)
    timeline_df['End'] = timeline_df['Timestamp'] + pd.Timedelta(minutes=15)
    
    # Create a Gantt chart using plotly
    fig = go.Figure()
    
    for person in timeline_df['PersonName'].unique():
        person_df = timeline_df[timeline_df['PersonName'] == person]
        
        fig.add_trace(go.Scatter(
            x=person_df['Timestamp'],
            y=[person] * len(person_df),
            mode='markers',
            name=person,
            marker=dict(size=10),
            hovertemplate="<b>%{y}</b><br>" +
                         "Time: %{x|%H:%M:%S}<extra></extra>"
        ))
    
    fig.update_layout(
        title='Attendance Timeline',
        xaxis_title='Time',
        yaxis_title='Person',
        height=400,
        showlegend=True,
        yaxis={'categoryorder': 'category ascending'},
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_attendance_histogram(df):
    if df.empty:
        return
        
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['Timestamp'].dt.hour + df['Timestamp'].dt.minute/60,
        nbinsx=24,
        name='Attendance Distribution'
    ))
    
    fig.update_layout(
        title='Attendance Distribution by Hour',
        xaxis_title='Hour of Day',
        yaxis_title='Number of People',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_attendance_dashboard():
    st.set_page_config(page_title="Face Recognition Attendance System", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .stMetric:hover {
            background-color: #262730;
        }
        .stDataFrame {
            border: 1px solid #262730;
            border-radius: 0.5rem;
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("📊 Face Recognition Attendance Dashboard")
    
    # Date selection dengan waktu WIB
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now(WIB).date()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now(WIB).date()
        )
    
    # Load and process data
    df = load_attendance_data(start_date, end_date)
    
    # Show metrics for today using WIB time
    st.subheader("Today's Overview")
    today_df = show_metrics(df, datetime.now(WIB).date())
    
    # Attendance Timeline
    st.subheader("Attendance Timeline")
    plot_attendance_timeline(df)
    
    # Attendance Distribution
    st.subheader("Attendance Distribution")
    plot_attendance_histogram(df)
    
# Detailed Attendance Table
    st.subheader("Detailed Attendance Records")
    if not df.empty:
        # Sort the original dataframe first by timestamp
        df_sorted = df.sort_values('Timestamp', ascending=False)
        
        # Create display version with formatted columns in WIB time
        df_display = pd.DataFrame({
            'No': range(len(df_sorted), 0, -1),  # Mengubah urutan nomor dari besar ke kecil
            'PersonName': df_sorted['PersonName'],
            'Date': df_sorted['Timestamp'].dt.strftime('%Y-%m-%d'),
            'Time': df_sorted['Timestamp'].dt.strftime('%H:%M:%S')
        }).set_index('No')
        
        # Display the sorted dataframe
        st.dataframe(
            df_display,
            use_container_width=True
        )
    else:
        st.info("No attendance records found for the selected date range.")

if __name__ == "__main__":
    show_attendance_dashboard()