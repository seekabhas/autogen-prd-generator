#!/usr/bin/env python3
"""
Streamlit UI for AutoGen PRD Generator
Run with: streamlit run ui.py
"""

import streamlit as st
from agents import (
    create_orchestrator_agent, 
    create_intent_classifier, 
    create_conversation_agent, 
    create_research_agent,
    create_prd_agent
)
import logging

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="AutoGen PRD Generator",
    page_icon="📋",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_stage' not in st.session_state:
    st.session_state.conversation_stage = 'initial'
if 'current_intent' not in st.session_state:
    st.session_state.current_intent = None
if 'agents' not in st.session_state:
    # Initialize all agents
    st.session_state.agents = {
        'orchestrator': create_orchestrator_agent(),
        'intent_classifier': create_intent_classifier(),
        'conversation_agent': create_conversation_agent(),
        'research_agent': create_research_agent(),
        'prd_agent': create_prd_agent()
    }
    logging.info("All agents initialized successfully")

st.title("🤖 AutoGen PRD Generator")
st.subheader("AI-Powered Product Requirements Document Creation")

# Sidebar with status
with st.sidebar:
    st.markdown("### 📊 Session Status")
    st.write(f"**Stage:** {st.session_state.conversation_stage}")
    if st.session_state.current_intent:
        st.write(f"**Intent:** {st.session_state.current_intent}")
    st.write(f"**Messages:** {len(st.session_state.messages)}")
    
    st.markdown("---")
    st.markdown("### 🔄 Workflow")
    st.markdown("""
    1. **Intent Detection** - AI analyzes your request
    2. **Requirements Gathering** - Interactive Q&A session  
    3. **Market Research** - AI researches relevant data
    4. **PRD Generation** - Creates comprehensive document
    """)
    
    st.markdown("### ⚙️ System")
    st.markdown("- **AutoGen** Multi-Agent Framework")
    st.markdown("- **Ollama** Local LLM")
    st.markdown("- **Qwen2.5VL:3B** Language Model")
    
    if st.button("🔄 Reset Conversation", type="secondary"):
        st.session_state.messages = []
        st.session_state.conversation_stage = 'initial'
        st.session_state.current_intent = None
        st.rerun()

# Main chat interface
st.markdown("## 💬 Interactive Chat")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def process_conversation_turn(user_input: str) -> str:
    """Process a single conversation turn through the agent workflow"""
    
    agents = st.session_state.agents
    stage = st.session_state.conversation_stage
    
    logging.info(f"Processing input at stage: {stage}")
    
    try:
        # Stage 1: Initial intent detection
        if stage == 'initial':
            logging.info("Stage: Intent Detection")
            
            # Use intent classifier
            intent_response = agents['intent_classifier'].generate_reply([
                {"role": "user", "content": user_input}
            ])
            
            # Extract intent from response
            intent = str(intent_response).strip().lower()
            st.session_state.current_intent = intent
            logging.info(f"Detected intent: {intent}")
            
            if 'prd' in intent:
                # Move to conversation stage
                st.session_state.conversation_stage = 'requirements_gathering'
                
                # Start requirements gathering
                conversation_prompt = f"""The user wants to create a PRD for: "{user_input}"

Start gathering requirements by asking your first question. Remember to ask only ONE specific question to begin understanding their product needs."""
                
                conv_response = agents['conversation_agent'].generate_reply([
                    {"role": "user", "content": conversation_prompt}
                ])
                
                return f"🎯 **Great! I'll help you create a Product Requirements Document.**\n\n{conv_response}"
            
            else:
                return "👋 Hi! I specialize in creating Product Requirements Documents (PRDs). Please describe a product, feature, or system you'd like to document, and I'll help you create a comprehensive PRD through an interactive conversation."
        
        # Stage 2: Requirements gathering conversation
        elif stage == 'requirements_gathering':
            logging.info("Stage: Requirements Gathering")
            
            # Build conversation context
            conversation_context = "Previous conversation:\n"
            for msg in st.session_state.messages[-10:]:  # Last 10 messages for context
                conversation_context += f"{msg['role']}: {msg['content']}\n"
            
            conversation_context += f"\nLatest user response: {user_input}"
            
            # Get next question or determine if complete
            conv_response = agents['conversation_agent'].generate_reply([
                {"role": "user", "content": conversation_context}
            ])
            
            # Check if requirements are complete
            if "REQUIREMENTS_COMPLETE" in str(conv_response):
                logging.info("Requirements gathering complete, moving to research phase")
                st.session_state.conversation_stage = 'research_and_generation'
                
                # Extract the main topic for research
                first_user_message = st.session_state.messages[0]['content']
                
                # Perform research
                research_prompt = f"""Research the market and technical landscape for: {first_user_message}

Based on our conversation, gather relevant information about:
- Market opportunities and trends
- Competitive analysis
- Technical best practices
- User behavior insights

Use web search to find current information."""
                
                with st.spinner("🔍 Researching market data and best practices..."):
                    research_response = agents['research_agent'].generate_reply([
                        {"role": "user", "content": research_prompt}
                    ])
                
                # Generate PRD
                prd_prompt = f"""Create a comprehensive Product Requirements Document based on:

CONVERSATION HISTORY:
{conversation_context}

RESEARCH FINDINGS:
{research_response}

Generate a detailed, professional PRD following the structured format."""

                with st.spinner("📝 Generating your comprehensive PRD..."):
                    prd_response = agents['prd_agent'].generate_reply([
                        {"role": "user", "content": prd_prompt}
                    ])
                
                st.session_state.conversation_stage = 'complete'
                
                return f"""✅ **Requirements gathering complete!**

📊 **Research Summary:**
{research_response}

---

## 📋 **Your Product Requirements Document**

{prd_response}

---

🎉 **PRD Generation Complete!** 

You can now:
- Copy the PRD for your use
- Ask me to refine specific sections
- Start a new PRD conversation"""
            
            else:
                return conv_response
        
        # Stage 3: PRD complete - handle follow-up
        elif stage == 'complete':
            logging.info("Stage: Post-PRD Interaction")
            
            if any(word in user_input.lower() for word in ['new', 'another', 'different', 'start over']):
                # Reset for new conversation
                st.session_state.conversation_stage = 'initial'
                st.session_state.current_intent = None
                return "🔄 **Starting fresh!** What new product would you like to create a PRD for?"
            
            elif any(word in user_input.lower() for word in ['refine', 'improve', 'modify', 'change']):
                return "🔧 **I can help refine the PRD!** Which specific section would you like me to improve or what changes would you like to make?"
            
            else:
                return """🤔 **I can help you with:**

- **Refine the PRD** - Improve specific sections or add details
- **Start a new PRD** - Create documentation for a different product  
- **Answer questions** - About the PRD or product requirements process

What would you like to do?"""
        
        else:
            # Fallback
            st.session_state.conversation_stage = 'initial'
            return "🔄 Let's start fresh. What product would you like to create a PRD for?"
    
    except Exception as e:
        logging.error(f"Error in conversation processing: {e}")
        return f"⚠️ I encountered an issue: {str(e)}. Please try rephrasing your request or check that Ollama is running properly."

# Handle user input
if user_input := st.chat_input("Describe your product idea or ask a question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display AI response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Processing your request..."):
            try:
                response = process_conversation_turn(user_input)
                st.markdown(response)
                # Add AI response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"❌ **Error occurred:** {str(e)}\n\n**Troubleshooting:**\n- Ensure Ollama is running (`ollama serve`)\n- Check if the model is available (`ollama list`)\n- Verify the model name in config.py"
                st.error(error_message)
                logging.error(f"Error in conversation: {e}")

# Footer
st.markdown("---")
st.markdown("**🚀 Built with AutoGen + Ollama + Streamlit | Local & Private AI Processing**")