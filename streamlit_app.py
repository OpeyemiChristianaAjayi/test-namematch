import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Name Matching API Demo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL= "https://namematchbk-c2ecaaaqcjhccsbz.australiaeast-01.azurewebsites.net
API_BASE_URL = "http://127.0.0.1:8000"  # Adjust this to your API URL
API_ENDPOINT = f"{API_BASE_URL}/api/v1/utility/util"

def call_name_matching_api(name1, name2):
    """Call the name matching API and return the response"""
    try:
        params = {
            "name1": name1,
            "name2": name2
        }
        
        headers = {
            "accept": "application/json"
        }
        
        # Show loading spinner
        with st.spinner(f"Comparing '{name1}' vs '{name2}'..."):
            start_time = time.time()
            response = requests.get(API_ENDPOINT, params=params, headers=headers)
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        if response.status_code == 200:
            result = response.json()
            result['response_time_ms'] = response_time
            return result, None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, f"Connection Error: Could not connect to API at {API_BASE_URL}. Make sure your API server is running."
    except Exception as e:
        return None, f"Error: {str(e)}"

def format_confidence_score(score):
    """Format confidence score with color coding"""
    if score >= 0.8:
        return f"<span style='color: green; font-weight: bold'>{score:.2f}</span>"
    elif score >= 0.5:
        return f"<span style='color: orange; font-weight: bold'>{score:.2f}</span>"
    else:
        return f"<span style='color: red; font-weight: bold'>{score:.2f}</span>"

def format_match_result(is_match):
    """Format match result with color coding"""
    if is_match == "yes":
        return f"<span style='color: green; font-weight: bold; font-size: 18px'>✅ YES</span>"
    else:
        return f"<span style='color: red; font-weight: bold; font-size: 18px'>❌ NO</span>"

def display_result(result):
    """Display the API result in a formatted way"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("### 📊 Match Result")
        match_html = format_match_result(result.get('is_match', 'no'))
        st.markdown(match_html, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 🎯 Confidence Score")
        confidence_html = format_confidence_score(result.get('confidence_score', 0.0))
        st.markdown(confidence_html, unsafe_allow_html=True)
        
    with col3:
        st.markdown("### ⏱️ Response Time")
        st.markdown(f"**{result.get('response_time_ms', 0)} ms**")
    
    # Reason section
    st.markdown("### 💭 Reasoning")
    reason = result.get('reason', 'No reason provided')
    st.info(reason)
    
    # Routing information
    st.markdown("### 📋 Sheet Routing Info")
    is_match = result.get('is_match') == 'yes'
    confidence = result.get('confidence_score', 0.0)
    
    if is_match and confidence >= 0.8:
        sheet_name = "Name Match API True Data"
        sheet_color = "green"
        sheet_icon = "✅"
    elif not is_match and confidence < 0.8:
        sheet_name = "Name Match API False Data"
        sheet_color = "red"
        sheet_icon = "❌"
    else:
        sheet_name = "Name Match API Data"
        sheet_color = "orange"
        sheet_icon = "📊"
    
    st.markdown(f"""
    <div style='padding: 10px; border-left: 4px solid {sheet_color}; background-color: #f0f0f0;'>
        {sheet_icon} <strong>Target Sheet:</strong> {sheet_name}
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.title("🔍 Name Matching API Demo")
    st.markdown("Test the intelligent name matching system with caching and conditional routing")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API URL configuration
        st.subheader("API Settings")
        api_url = st.text_input("API Base URL", value=API_BASE_URL)
        
        # Update global API endpoint if changed
        global API_ENDPOINT
        API_ENDPOINT = f"{api_url}/api/v1/utility/util"
        
        st.markdown("---")
        
        # Information about the system
        st.subheader("📊 Sheet Routing Logic")
        st.markdown("""
        **True Data Sheet:**
        - is_match = YES
        - confidence ≥ 0.8
        
        **False Data Sheet:**
        - is_match = NO  
        - confidence < 0.8
        
        **Default Data Sheet:**
        - All other combinations
        """)
        
        st.markdown("---")
        
        # Test scenarios
        st.subheader("🧪 Quick Test Scenarios")
        if st.button("Load Similar Names"):
            st.session_state.name1 = "John Smith"
            st.session_state.name2 = "JOHNSMITH123"
            
        if st.button("Load Different Names"):
            st.session_state.name1 = "Alice Johnson"
            st.session_state.name2 = "Bob Wilson"
            
        if st.button("Load Nickname Test"):
            st.session_state.name1 = "Michael Johnson"
            st.session_state.name2 = "Mike Johnson"
    
    # Main input section
    st.header("🎯 Name Comparison Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name1 = st.text_input(
            "👤 Name 1", 
            value=st.session_state.get('name1', ''),
            placeholder="Enter first name...",
            key="input_name1"
        )
    
    with col2:
        name2 = st.text_input(
            "👤 Name 2", 
            value=st.session_state.get('name2', ''),
            placeholder="Enter second name...",
            key="input_name2"
        )
    
    # Update session state
    st.session_state.name1 = name1
    st.session_state.name2 = name2
    
    # Compare button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Compare Names", type="primary", use_container_width=True):
            if name1.strip() and name2.strip():
                result, error = call_name_matching_api(name1.strip(), name2.strip())
                
                if result:
                    st.markdown("---")
                    st.header("📋 Results")
                    display_result(result)
                    
                    # Store result in session state for history
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    
                    result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result['input_name1'] = name1.strip()
                    result['input_name2'] = name2.strip()
                    st.session_state.history.insert(0, result)
                    
                    # Keep only last 10 results
                    st.session_state.history = st.session_state.history[:10]
                    
                elif error:
                    st.error(error)
            else:
                st.warning("⚠️ Please enter both names to compare")
    
    # History section
    if 'history' in st.session_state and st.session_state.history:
        st.markdown("---")
        st.header("📚 Recent Comparisons")
        
        # Create DataFrame from history
        history_data = []
        for item in st.session_state.history:
            history_data.append({
                'Timestamp': item.get('timestamp', ''),
                'Name 1': item.get('input_name1', ''),
                'Name 2': item.get('input_name2', ''),
                'Match': '✅ YES' if item.get('is_match') == 'yes' else '❌ NO',
                'Confidence': f"{item.get('confidence_score', 0):.2f}",
                'Response Time (ms)': item.get('response_time_ms', 0)
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    
    # API Health Check
    st.markdown("---")
    st.header("🏥 API Health Check")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Check API Status"):
            try:
                health_response = requests.get(f"{api_url}/health", timeout=5)
                if health_response.status_code == 200:
                    st.success("✅ API is healthy and accessible")
                else:
                    st.error(f"❌ API returned status code: {health_response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Cannot connect to API at {api_url}")
            except Exception as e:
                st.error(f"❌ Health check failed: {str(e)}")
    
    with col2:
        st.info(f"📡 **Current API Endpoint:** {API_ENDPOINT}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🔍 <strong>Name Matching API Demo</strong> | Built with Streamlit</p>
            <p>Features: Intelligent Caching • Conditional Routing • Duplicate Prevention</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
#past edpoint tests
# import streamlit as st
# import requests
# import json
# import time

# # Configuration
# FASTAPI_URL = "http://localhost:8000/api/v1/chatbot"
# HEADERS = {"Content-Type": "application/json"}  # Initialize without token, will be updated with JWT

# # Title and layout
# st.title("Name Match AI Service Demo")
# st.write("Interact with the chatbot using the /chat and /chat/stream endpoints.")

# # Input for JWT token
# st.subheader("Authentication")
# jwt_token = st.text_area("Enter your JWT Token:", "your_token_here", height=100)
# if jwt_token and jwt_token != "your_token_here":
#     HEADERS["Authorization"] = f"Bearer {jwt_token}"

# # Input for user message
# user_message = st.text_input("Enter your message:", "How long does the onboarding process take?")

# # Buttons for chat and stream
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("Send Chat"):
#         if user_message:
#             payload = {"messages": [{"role": "user", "content": user_message}]}
#             try:
#                 response = requests.post(f"{FASTAPI_URL}/chat", headers=HEADERS, json=payload)
#                 if response.status_code == 200:
#                     result = response.json()
#                     st.session_state.messages = result.get("messages", [])
#                     st.write("**Chat Response:**")
#                     for msg in st.session_state.messages:
#                         st.write(f"{msg['role'].capitalize()}: {msg['content']}")
#                 else:
#                     st.error(f"Error: {response.status_code} - {response.text}")
#             except Exception as e:
#                 st.error(f"Request failed: {str(e)}")


# with col2:
#     if st.button("Stream Chat"):
#         if user_message:
#             payload = {"messages": [{"role": "user", "content": user_message}]}
#             try:
#                 with st.spinner("Streaming response..."):
#                     response = requests.post(
#                         f"{FASTAPI_URL}/chat/stream", 
#                         headers=HEADERS, 
#                         json=payload, 
#                         stream=True, 
#                         timeout=180
#                     )
                    
#                     print(f"Response status: {response.status_code}")
#                     print(f"Response headers: {response.headers}")
                    
#                     if response.status_code == 200:
#                         # Initialize session state messages if not exists
#                         if "messages" not in st.session_state:
#                             st.session_state.messages = []
                        
#                         # Add user message to session state
#                         st.session_state.messages.append({
#                             "role": "user", 
#                             "content": user_message
#                         })
                        
#                         st.write("**Streaming Response:**")
                        
#                         # Create a container for the streaming response
#                         response_container = st.container()
                        
#                         message_content = ""
                        
#                         try:
#                             # Process streaming response
#                             for line in response.iter_lines(decode_unicode=True):
#                                 if line:
#                                     print(f"Raw line: {repr(line)}")  # Debug with repr to see exact content
                                    
#                                     # Handle different SSE line formats
#                                     if line.startswith("data: "):
#                                         data_str = line[6:]  # Remove "data: " prefix
                                        
#                                         # Skip empty data or [DONE] signals
#                                         if not data_str.strip() or data_str.strip() == "[DONE]":
#                                             continue
                                            
#                                         try:
#                                             data = json.loads(data_str)
#                                             print(f"Parsed data: {data}")
                                            
#                                             # Handle different response formats
#                                             content_delta = ""
                                            
#                                             # Check various possible response formats
#                                             if "delta" in data:
#                                                 if "content" in data["delta"]:
#                                                     content_delta = data["delta"]["content"]
#                                                 elif "message" in data["delta"] and "content" in data["delta"]["message"]:
#                                                     content_delta = data["delta"]["message"]["content"]
#                                             elif "content" in data:
#                                                 content_delta = data["content"]
#                                             elif "message" in data and "content" in data["message"]:
#                                                 content_delta = data["message"]["content"]
                                            
#                                             # Update content if we got a delta
#                                             if content_delta:
#                                                 message_content += content_delta
                                                
#                                                 # Update the display in real-time
#                                                 with response_container:
#                                                     st.markdown(f"**Assistant:** {message_content}")
                                                
#                                                 # Small delay to make streaming visible
#                                                 time.sleep(0.01)
                                            
#                                             # Check for completion signals
#                                             is_done = (
#                                                 data.get("done", False) or 
#                                                 data.get("finished", False) or
#                                                 (data.get("delta", {}).get("finish_reason") is not None)
#                                             )
                                            
#                                             if is_done:
#                                                 print("Stream completed")
#                                                 break
                                                
#                                         except json.JSONDecodeError as json_err:
#                                             print(f"JSON decode error: {json_err} for line: {data_str}")
#                                             # If it's not JSON, might be plain text
#                                             if data_str.strip() and not data_str.strip().startswith("{"):
#                                                 message_content += data_str
#                                                 with response_container:
#                                                     st.markdown(f"**Assistant:** {message_content}")
#                                             continue
                                            
#                                     elif line.strip() == "":
#                                         # Handle empty lines (SSE delimiter)
#                                         continue
#                                     elif not line.startswith("data:") and line.strip():
#                                         # Handle lines that might be plain text without SSE format
#                                         print(f"Non-SSE line: {line}")
#                                         # You might want to handle this case depending on your server
                                        
#                         except Exception as stream_err:
#                             print(f"Streaming error: {stream_err}")
#                             st.error(f"Streaming error: {str(stream_err)}")
                        
#                         # Add the complete message to session state
#                         if message_content:
#                             st.session_state.messages.append({
#                                 "role": "assistant", 
#                                 "content": message_content
#                             })
#                             print(f"Final message added: {message_content}")
                        
#                         # Success message
#                         st.success("Streaming completed!")
                        
#                         # Force a rerun to update the chat history display
#                         st.rerun()
                        
#                     else:
#                         st.error(f"Error: {response.status_code} - {response.text}")
                        
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Request failed: {str(e)}")
#                 print(f"Request Exception: {e}")
#             except Exception as e:
#                 st.error(f"Unexpected error: {str(e)}")
#                 print(f"Unexpected Exception: {e}")

# # Additional buttons for get_all_chat and clear_all_chat
# col3, col4 = st.columns(2)
# with col3:
#     if st.button("Get All Chat"):
#         try:
#             response = requests.get(f"{FASTAPI_URL}/messages", headers=HEADERS)
#             if response.status_code == 200:
#                 result = response.json()
#                 st.session_state.messages = result.get("messages", [])
#                 st.write("**All Chat History:**")
#                 for msg in st.session_state.messages:
#                     st.write(f"{msg['role'].capitalize()}: {msg['content']}")
#             else:
#                 st.error(f"Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             st.error(f"Request failed: {str(e)}")

# with col4:
#     if st.button("Clear All Chat"):
#         try:
#             response = requests.delete(f"{FASTAPI_URL}/messages", headers=HEADERS)
#             if response.status_code == 200:
#                 st.session_state.messages = []
#                 st.success("Chat history cleared successfully")
#             else:
#                 st.error(f"Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             st.error(f"Request failed: {str(e)}")

# # Display chat history
# if "messages" in st.session_state and st.session_state.messages:
#     st.write("**Chat History:**")
#     for msg in st.session_state.messages:
#         st.write(f"{msg['role'].capitalize()}: {msg['content']}")
