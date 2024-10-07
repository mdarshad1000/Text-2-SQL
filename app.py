import streamlit as st
import pandas as pd
from llm_integration import OpenAIQueryGenerator, OllamaQueryGenerator, GeminiQueryGenerator
from query_executor import DatabaseExecutor

# Page config
st.set_page_config(
    page_title="LLM SQL Query Generator",
    page_icon="🤖",
    layout="wide"
)

# Initialize models and database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseExecutor()
if 'models' not in st.session_state:
    st.session_state.models = {
        '🌟 GPT-4': OpenAIQueryGenerator(model='gpt-4'),
        '🔮 llama3.2': OllamaQueryGenerator(model='llama3.2:latest'),
        '🤖 Gemini': GeminiQueryGenerator()
    }

# Format schema into a more readable structure
def format_schema(schema_df):
    # Group by table name
    tables = {}
    for _, row in schema_df.iterrows():
        table_name = row['Table Name']
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append({
            'column': row['Column Name'],
            'type': row['Data Type']
        })
    
    # Create formatted string
    formatted_schema = []
    for table, columns in tables.items():
        formatted_schema.append(f"\n📊 TABLE: {table.upper()}")
        for col in columns:
            formatted_schema.append(f"  ├─ {col['column']} ({col['type']})")
    
    return "\n".join(formatted_schema)

# Sidebar
with st.sidebar:
    st.title("🤖 SQL Query Generator")
    
    # Model selection at the top
    st.header("Model Selection")
    selected_model = st.selectbox(
        "Choose AI Model",
        options=list(st.session_state.models.keys())
    )
    
    # Schema viewer with better formatting
    st.header("Database Schema")
    schema_df = pd.DataFrame(st.session_state.db.get_schema_info()[0])
    
    # Quick schema overview
    st.caption("Quick Overview:")
    st.info(f"📊 {len(schema_df['Table Name'].unique())} tables, {len(schema_df)} total columns")
    
    # Table selector for detailed view
    selected_table = st.selectbox(
        "Select table to view details",
        options=['All Tables'] + list(schema_df['Table Name'].unique())
    )
    
    # Show schema based on selection
    if selected_table == 'All Tables':
        with st.expander("View Complete Schema", expanded=False):
            st.text(format_schema(schema_df))
    else:
        filtered_df = schema_df[schema_df['Table Name'] == selected_table]
        st.table(filtered_df[['Column Name', 'Data Type']])

# Main content
st.title("Natural Language to SQL Query")

# User input section
user_query = st.text_area(
    "What would you like to know?",
    height=100,
    placeholder="e.g., Give me the full name of all the people hired before May 2022"
)

if st.button("🚀 Generate Results", type="primary"):
    if user_query:
        with st.spinner("Generating query and fetching results..."):
            try:
                # Generate SQL query
                database_schema = st.session_state.db.get_schema_info()[1]
                llm = st.session_state.models[selected_model]
                sql_query = llm.generate_sql_from_nl(database_schema, user_query)
                
                # Execute query
                db_response = st.session_state.db.execute_query(sql_query)
                
                # Store results
                st.session_state.current_query = sql_query
                st.session_state.current_results = db_response
                
                st.success("Query executed successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question first!")

# Display generated SQL
if 'current_query' in st.session_state:
    st.subheader("Generated SQL Query")
    st.code(st.session_state.current_query, language="sql")

# Results section with tabs
if 'current_results' in st.session_state:
    # Convert to DataFrame if needed
    if not isinstance(st.session_state.current_results, pd.DataFrame):
        df = pd.DataFrame(st.session_state.current_results)
    else:
        df = st.session_state.current_results
    
    # Check data types
    # st.write("Data Types of Columns:")
    # st.write(df.dtypes)  # Check data types for debugging

    # Convert 'total_revenue' to numeric if it's in the DataFrame
    if 'total_revenue' in df.columns:
        df['total_revenue'] = pd.to_numeric(df['total_revenue'], errors='coerce')

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Data Table", "📈 Visualizations"])
    
    with tab1:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv,
            file_name="query_results.csv",
            mime="text/csv"
        )
    
    with tab2:
        if not df.empty and df.shape[1] >= 2:
            # Column selection for visualization
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) >= 1:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("Select X-axis", options=df.columns)
                with col2:
                    y_axis = st.selectbox("Select Y-axis", options=numeric_cols)
                
                chart_type = st.radio(
                    "Select chart type:",
                    options=["Bar Chart", "Line Chart", "Area Chart"],
                    horizontal=True
                )
                
                # Create visualization based on selection
                chart_data = df[[x_axis, y_axis]].set_index(x_axis)
                if chart_type == "Bar Chart":
                    st.bar_chart(chart_data)
                elif chart_type == "Line Chart":
                    st.line_chart(chart_data)
                elif chart_type == "Area Chart":
                    st.area_chart(chart_data)
            else:
                st.info("No numeric columns available for visualization")
        else:
            st.info("Insufficient data for visualization. Need at least 2 columns with numeric data.")
