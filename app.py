import streamlit as st
import json
import openai

# Set page configuration
st.set_page_config(
    page_title="Structured System Prompt Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .output-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .json-output {
        position: relative;
    }
    .copy-btn {
        float: right;
        margin-top: -10px;
        margin-right: 10px;
    }
    .copy-icon {
        cursor: pointer;
        margin-left: 5px;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}
</style>
""", unsafe_allow_html=True)

# Add JavaScript for copy to clipboard functionality
def get_clipboard_js():
    return """
    <script>
    function copyToClipboard(text) {
        const el = document.createElement('textarea');
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
    }
    </script>
    """

# Create a button with clipboard functionality
def copy_button(text, button_text="Copy", key=None):
    if st.button(f"📋 {button_text}", key=key):
        st.markdown(f"""
        <script>
        const text = `{text.replace('`', '\\`')}`;
        navigator.clipboard.writeText(text)
            .then(() => console.log('Copied to clipboard'))
            .catch(err => console.error('Error copying: ', err));
        </script>
        """, unsafe_allow_html=True)
        st.success(f"{button_text} copied to clipboard!")

# Function to process the system prompt using OpenAI
def process_system_prompt(api_key, system_prompt):
    if not api_key or not system_prompt:
        return None, None, None
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Create the message for OpenAI
        messages = [
            {"role": "system", "content": """You are a helpful assistant specialized in refining system prompts and generating structured schemas for AI tools. When a user provides a system prompt, your task is to analyze it and produce three key outputs: an optimized system prompt, data requirements, and a JSON schema.

1.  **Optimized System Prompt:** Re-write the provided system prompt for clarity, intelligibility, and flow, and present the rewritten system prompt within a markdown code fence. Ensure all instructions are clear and actionable. Do not change the purpose of the assistant.
2.  **Data Requirements:** List every piece of data that the optimized system prompt requires, along with its most likely structure described in SQL terms. Present this information in a markdown table with the columns "Field Name" and "Data Type". For example:

    | Field Name      | Data Type |
    | --------------- | --------- |
    | Company Name    | VARCHAR   |
    | Estimated Revenue | INTEGER   |
3.  **Structured Output JSON:** Generate a JSON schema that reflects the data collection process detailed in the optimized system prompt. Present the entire JSON schema within a code fence. This schema should align with the data requirements table."""},
            {"role": "user", "content": f"Please analyze this system prompt: {system_prompt}"}
        ]
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Parse the response to extract the three components
        # This is a simple parsing approach and might need refinement
        sections = content.split("**")
        
        optimized_prompt = ""
        data_requirements = ""
        json_schema = ""
        
        for i, section in enumerate(sections):
            if "Optimized System Prompt" in section and i+1 < len(sections):
                optimized_prompt = sections[i+1].strip()
                # Extract content from markdown code fence if present
                if "```" in optimized_prompt:
                    parts = optimized_prompt.split("```")
                    if len(parts) >= 3:
                        fence_content = parts[1]
                        if fence_content.startswith("markdown") or fence_content.startswith("md"):
                            optimized_prompt = parts[2].strip()
                        else:
                            optimized_prompt = fence_content.strip()
            
            if "Data Requirements" in section and i+1 < len(sections):
                data_requirements = sections[i+1].strip()
                # Keep the markdown table format
            
            if "Structured Output JSON" in section and i+1 < len(sections):
                json_schema = sections[i+1].strip()
                # Extract content from code fence if present
                if "```" in json_schema:
                    parts = json_schema.split("```")
                    if len(parts) >= 3:
                        fence_content = parts[1]
                        if fence_content.startswith("json"):
                            json_schema = parts[2].strip()
                        else:
                            json_schema = fence_content.strip()
        
        return optimized_prompt, data_requirements, json_schema
    
    except Exception as e:
        st.error(f"Error processing prompt: {str(e)}")
        return None, None, None

# Sidebar for API key input
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Enter your OpenAI API Key", type="password", help="Your API key will not be stored")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app helps you generate structured system prompts for AI applications.
    
    It analyzes your input prompt and produces:
    1. An optimized system prompt
    2. Data requirements table
    3. Structured output JSON schema
    
    Created with ❤️ using Streamlit
    """)

# Main content
st.title("🤖 Structured System Prompt Generator")
st.markdown("Input your system prompt, and get an optimized version with structured data requirements and JSON schema.")

# Input text area
system_prompt = st.text_area("Enter your system prompt:", height=200)

# Process button
col1, col2 = st.columns([3, 1])
with col1:
    process_button = st.button("🚀 Generate Structured Prompt", use_container_width=True)
with col2:
    reset_button = st.button("🔄 Reset", use_container_width=True)

if reset_button:
    st.experimental_rerun()

if process_button:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not system_prompt:
        st.error("Please enter a system prompt.")
    else:
        with st.spinner("Processing your system prompt..."):
            optimized_prompt, data_requirements, json_schema = process_system_prompt(api_key, system_prompt)
            
            if optimized_prompt and data_requirements and json_schema:
                # Display results in tabs
                tabs = st.tabs(["Optimized System Prompt", "Data Requirements", "JSON Schema"])
                
                with tabs[0]:
                    st.markdown("### Optimized System Prompt")
                    
                    # Create a container for the prompt with copy button
                    prompt_container = st.container()
                    with prompt_container:
                        col1, col2 = st.columns([10, 1])
                        with col1:
                            st.markdown("#### Result")
                        with col2:
                            # Add copy button using HTML/JS
                            st.markdown(f"""
                            <div class="copy-btn">
                                <span onclick="copyToClipboard(`{optimized_prompt.replace('`', '\\`')}`)">
                                    <span title="Copy to clipboard">📋</span>
                                </span>
                            </div>
                            {get_clipboard_js()}
                            """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown(optimized_prompt)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a regular Streamlit copy button as fallback
                    copy_button(optimized_prompt, "Copy Optimized Prompt", key="copy_prompt")
                
                with tabs[1]:
                    st.markdown("### Data Requirements")
                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown(data_requirements)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tabs[2]:
                    st.markdown("### Structured Output JSON")
                    
                    # Format JSON if it's valid
                    try:
                        parsed_json = json.loads(json_schema)
                        formatted_json = json.dumps(parsed_json, indent=2)
                    except json.JSONDecodeError:
                        formatted_json = json_schema
                    
                    # Create a container for the JSON with copy button
                    json_container = st.container()
                    with json_container:
                        col1, col2 = st.columns([10, 1])
                        with col1:
                            st.markdown("#### JSON Schema")
                        with col2:
                            # Add copy button using HTML/JS
                            st.markdown(f"""
                            <div class="copy-btn">
                                <span onclick="copyToClipboard(`{formatted_json.replace('`', '\\`')}`)">
                                    <span title="Copy to clipboard">📋</span>
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-container json-output">', unsafe_allow_html=True)
                    st.code(formatted_json, language="json")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a regular Streamlit copy button as fallback
                    copy_button(formatted_json, "Copy JSON Schema", key="copy_json")
