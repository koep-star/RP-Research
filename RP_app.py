import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configure the page
st.set_page_config(
    page_title="Roller Press Mining Project Research",
    page_icon="⛏️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #2c5282;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3182ce;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #38a169;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fffaf0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ed8936;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #fed7d7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #e53e3e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'research_data' not in st.session_state:
        st.session_state.research_data = {}
    if 'completed_steps' not in st.session_state:
        st.session_state.completed_steps = set()
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0

def search_web_serp(query):
    """
    Search using SerpAPI (Google Search API)
    Requires SERP_API_KEY in Streamlit secrets
    """
    try:
        if "serp_api_key" not in st.secrets:
            return {"error": "SERP API key not found in secrets"}
        
        api_key = st.secrets["serp_api_key"]
        url = "https://serpapi.com/search"
        
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
            "num": 10,
            "gl": "au",  # Australia
            "hl": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if "organic_results" in data:
                for result in data["organic_results"][:5]:  # Top 5 results
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", "")
                    })
            
            return {"results": results, "query": query}
        else:
            return {"error": f"API request failed with status {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Search error: {str(e)}"}

def search_web_bing(query):
    """
    Search using Bing Search API
    Requires BING_API_KEY in Streamlit secrets
    """
    try:
        if "bing_api_key" not in st.secrets:
            return {"error": "Bing API key not found in secrets"}
        
        api_key = st.secrets["bing_api_key"]
        url = "https://api.bing.microsoft.com/v7.0/search"
        
        headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Accept": "application/json"
        }
        
        params = {
            "q": query,
            "count": 10,
            "mkt": "en-AU",
            "responseFilter": "Webpages"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if "webPages" in data and "value" in data["webPages"]:
                for result in data["webPages"]["value"][:5]:  # Top 5 results
                    results.append({
                        "title": result.get("name", ""),
                        "link": result.get("url", ""),
                        "snippet": result.get("snippet", "")
                    })
            
            return {"results": results, "query": query}
        else:
            return {"error": f"API request failed with status {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Search error: {str(e)}"}

def search_web_info(query):
    """
    Main search function that tries different APIs
    """
    st.info(f"🔍 Searching for: {query}")
    
    # Try SerpAPI first
    result = search_web_serp(query)
    if "error" not in result:
        return result
    
    # Try Bing API as fallback
    result = search_web_bing(query)
    if "error" not in result:
        return result
    
    # If both fail, return error
    return {
        "error": "No working search API found. Please configure SERP_API_KEY or BING_API_KEY in Streamlit secrets.",
        "query": query
    }

def parse_project_input(project_input):
    """Parse the combined project input to extract company and project names"""
    # Try different separators and formats
    separators = [' - ', ' – ', ' — ', ' | ', ' / ', ' \\ ']
    
    for sep in separators:
        if sep in project_input:
            parts = project_input.split(sep, 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
    
    # If no separator found, try to split on common patterns
    words = project_input.split()
    if len(words) >= 2:
        # Look for keywords that might indicate project name
        project_keywords = ['project', 'mine', 'deposit', 'prospect', 'operation']
        
        for i, word in enumerate(words):
            if word.lower() in project_keywords:
                company = ' '.join(words[:i]).strip()
                project = ' '.join(words[i:]).strip()
                if company and project:
                    return company, project
        
        # Default: split in half
        mid = len(words) // 2
        company = ' '.join(words[:mid]).strip()
        project = ' '.join(words[mid:]).strip()
        return company, project
    
    # If only one word, use it as both
    return project_input.strip(), project_input.strip()

def get_location_info(company_name, project_name):
    """Research step 1: Get project location"""
    query = f"{company_name} {project_name} mining project location Australia state"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'location': 'Location to be extracted from search results'
    }

def get_coordinates(company_name, project_name):
    """Research step 2: Get longitude and latitude"""
    query = f"{company_name} {project_name} mining coordinates latitude longitude GPS"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'coordinates': 'Coordinates to be extracted from search results'
    }

def get_commodity_info(company_name, project_name):
    """Research step 3: Get commodity information"""
    query = f"{company_name} {project_name} commodity gold copper iron ore lithium mineral"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'commodity': 'Commodity to be extracted from search results'
    }

def get_drilling_status(company_name, project_name):
    """Research step 4: Check diamond drilling completion"""
    query = f"{company_name} {project_name} diamond drilling completed reverse circulation drilling program"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'drilling_status': 'Drilling status to be extracted from search results'
    }

def get_project_stage(company_name, project_name):
    """Research step 5: Get project development stage"""
    query = f"{company_name} {project_name} exploration scoping study PFS DFS feasibility development stage"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'project_stage': 'Project stage to be extracted from search results'
    }

def get_resource_data(company_name, project_name):
    """Research step 6: Get resource size and grade"""
    query = f"{company_name} {project_name} resource estimate tonnage grade ounces Mt Moz JORC"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'resource_data': 'Resource data to be extracted from search results (e.g., 118.7Mt @ 0.53g/t Au for 2 Moz)'
    }

def get_ore_competency(company_name, project_name):
    """Research step 7: Get ore competency data"""
    query = f"{company_name} {project_name} ore competency UCS BWI AxB hardness strength bond work index"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'ore_competency': 'Ore competency data to be extracted from search results'
    }

def get_process_flowsheet(company_name, project_name):
    """Research step 8: Get process flowsheet and HPGR information"""
    query = f"{company_name} {project_name} process flowsheet HPGR high pressure grinding rolls comminution"
    results = search_web_info(query)
    
    return {
        'query': query,
        'results': results,
        'process_info': 'Process information to be extracted from search results'
    }

def display_search_results(results):
    """Display search results in a formatted way"""
    if "error" in results:
        st.markdown(f'<div class="error-box">❌ {results["error"]}</div>', unsafe_allow_html=True)
        return
    
    if "results" in results and results["results"]:
        st.markdown("**Search Results:**")
        for i, result in enumerate(results["results"], 1):
            with st.expander(f"{i}. {result['title']}", expanded=False):
                st.write(f"**Link:** {result['link']}")
                st.write(f"**Summary:** {result['snippet']}")
    else:
        st.warning("No search results found.")

def main():
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">⛏️ Roller Press Mining Project Research</h1>', unsafe_allow_html=True)
    
    # Project input section
    st.markdown('<div class="step-header">Project Information</div>', unsafe_allow_html=True)
    
    # Single input box for project information
    project_input = st.text_input(
        "Enter Project Information", 
        placeholder="e.g., Saturn Metals - Apollo Hill Project  or  BHP - Olympic Dam Mine",
        help="Enter the company name and project name. Use formats like 'Company - Project' or 'Company | Project'"
    )
    
    if not project_input:
        st.markdown('<div class="info-box">💡 Please enter project information in the format: "Company Name - Project Name" to proceed with research.</div>', unsafe_allow_html=True)
        return
    
    # Parse the input
    company_name, project_name = parse_project_input(project_input)
    
    # Display parsed information
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Company:** {company_name}")
    with col2:
        st.write(f"**Project:** {project_name}")
    
    # Option to manually adjust if parsing is incorrect
    with st.expander("✏️ Adjust company/project names if needed"):
        company_name = st.text_input("Company Name", value=company_name, key="company_manual")
        project_name = st.text_input("Project Name", value=project_name, key="project_manual")
    
    # Store project info in session state
    st.session_state.research_data['company_name'] = company_name
    st.session_state.research_data['project_name'] = project_name
    
    # Check API configuration
    st.markdown('<div class="step-header">API Configuration Status</div>', unsafe_allow_html=True)
    
    api_status = []
    if "serp_api_key" in st.secrets:
        api_status.append("✅ SerpAPI configured")
    if "bing_api_key" in st.secrets:
        api_status.append("✅ Bing Search API configured")
    
    if not api_status:
        st.markdown('<div class="warning-box">⚠️ No search APIs configured. Please add SERP_API_KEY or BING_API_KEY to your Streamlit secrets.</div>', unsafe_allow_html=True)
        st.markdown("""
        **To configure APIs:**
        1. Go to your Streamlit app settings
        2. Navigate to the "Secrets" section
        3. Add one of the following:
        ```
        serp_api_key = "your_serpapi_key_here"
        ```
        or
        ```
        bing_api_key = "your_bing_api_key_here"
        ```
        """)
    else:
        for status in api_status:
            st.markdown(f'<div class="success-box">{status}</div>', unsafe_allow_html=True)
    
    # Research steps
    research_steps = [
        {
            'title': '1. Project Location',
            'description': 'Determine the location of the project (state in Australia or overseas)',
            'function': get_location_info,
            'key': 'location'
        },
        {
            'title': '2. Geographic Coordinates',
            'description': 'Find longitude and latitude of the project',
            'function': get_coordinates,
            'key': 'coordinates'
        },
        {
            'title': '3. Commodity Information',
            'description': 'Identify the commodity being explored or mined',
            'function': get_commodity_info,
            'key': 'commodity'
        },
        {
            'title': '4. Diamond Drilling Status',
            'description': 'Check if the project has completed diamond drilling',
            'function': get_drilling_status,
            'key': 'drilling'
        },
        {
            'title': '5. Project Development Stage',
            'description': 'Determine current stage: Exploration, Scoping Study, PFS, DFS',
            'function': get_project_stage,
            'key': 'stage'
        },
        {
            'title': '6. Resource Size and Grade',
            'description': 'Find resource estimates in format: tonnage @ grade for ounces',
            'function': get_resource_data,
            'key': 'resources'
        },
        {
            'title': '7. Ore Competency',
            'description': 'Research UCS, BWI, AxB values or typical competency for the commodity',
            'function': get_ore_competency,
            'key': 'competency'
        },
        {
            'title': '8. Process Flowsheet & HPGR',
            'description': 'Analyze process flowsheet and HPGR applicability',
            'function': get_process_flowsheet,
            'key': 'process'
        }
    ]
    
    # Display research steps
    for i, step in enumerate(research_steps):
        st.markdown(f'<div class="step-header">{step["title"]}</div>', unsafe_allow_html=True)
        st.write(step['description'])
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button(f"Research Step {i+1}", key=f"btn_{i}"):
                with st.spinner(f"Researching {step['title'].lower()}..."):
                    result = step['function'](company_name, project_name)
                    st.session_state.research_data[step['key']] = result
                    st.session_state.completed_steps.add(i)
                    st.rerun()  # Refresh to show results
        
        with col1:
            if step['key'] in st.session_state.research_data:
                result = st.session_state.research_data[step['key']]
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.write("**Query Used:**", result['query'])
                display_search_results(result['results'])
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
    
    # Summary section
    if st.session_state.completed_steps:
        st.markdown('<div class="step-header">Research Summary</div>', unsafe_allow_html=True)
        
        # Progress bar
        progress = len(st.session_state.completed_steps) / len(research_steps)
        st.progress(progress, text=f"Progress: {len(st.session_state.completed_steps)}/{len(research_steps)} steps completed")
        
        # Export functionality
        if len(st.session_state.completed_steps) == len(research_steps):
            st.markdown('<div class="success-box">✅ All research steps completed!</div>', unsafe_allow_html=True)
            
            if st.button("📊 Generate Research Report"):
                # Create a comprehensive report
                report_data = {
                    'Company': company_name,
                    'Project': project_name,
                    'Research Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                # Add research data
                for key, data in st.session_state.research_data.items():
                    if isinstance(data, dict) and 'query' in data:
                        report_data[f'{key}_query'] = data['query']
                        if 'results' in data and isinstance(data['results'], dict) and 'results' in data['results']:
                            # Summarize search results
                            results_summary = []
                            for result in data['results']['results'][:3]:  # Top 3 results
                                results_summary.append(f"{result['title']}: {result['snippet'][:100]}...")
                            report_data[f'{key}_results'] = " | ".join(results_summary)
                
                # Convert to DataFrame for export
                df = pd.DataFrame([report_data])
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download Research Report (CSV)",
                    data=csv,
                    file_name=f"{company_name}_{project_name}_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        # Clear all data button
        if st.button("🗑️ Clear All Research Data", type="secondary"):
            st.session_state.research_data = {}
            st.session_state.completed_steps = set()
            st.rerun()

if __name__ == "__main__":
    main()
