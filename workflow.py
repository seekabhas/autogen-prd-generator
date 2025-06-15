from agents import (
    create_orchestrator_agent,
    create_intent_classifier, 
    create_conversation_agent,
    create_research_agent,
    create_prd_agent
)
from tools import save_conversation
import logging
import uuid

logging.basicConfig(level=logging.INFO)

class PRDWorkflow:
    """Backend workflow orchestrator for PRD generation"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.agents = {
            'orchestrator': create_orchestrator_agent(),
            'intent_classifier': create_intent_classifier(),
            'conversation_agent': create_conversation_agent(),
            'research_agent': create_research_agent(),
            'prd_agent': create_prd_agent()
        }
        self.conversation_history = []
        self.stage = 'initial'
        
        logging.info(f"PRDWorkflow initialized with session ID: {self.session_id}")
    
    def process_input(self, user_input: str) -> dict:
        """Process user input through the agent workflow"""
        
        self.conversation_history.append({"role": "user", "content": user_input})
        logging.info(f"Processing input at stage '{self.stage}': {user_input[:100]}...")
        
        try:
            if self.stage == 'initial':
                return self._handle_intent_detection(user_input)
            
            elif self.stage == 'requirements_gathering':
                return self._handle_requirements_gathering(user_input)
            
            elif self.stage == 'complete':
                return self._handle_post_completion(user_input)
            
            else:
                return {"response": "Workflow error. Restarting...", "stage": "initial"}
                
        except Exception as e:
            logging.error(f"Workflow error: {e}")
            return {"response": f"Error: {str(e)}", "stage": "error"}
    
    def _handle_intent_detection(self, user_input: str) -> dict:
        """Handle intent detection phase"""
        
        # Classify intent
        intent_response = self.agents['intent_classifier'].generate_reply([
            {"role": "user", "content": user_input}
        ])
        
        intent = str(intent_response).strip().lower()
        logging.info(f"Detected intent: {intent}")
        
        if 'prd' in intent:
            self.stage = 'requirements_gathering'
            
            # Start requirements conversation
            conv_prompt = f"""User wants PRD for: "{user_input}"
            
Begin requirements gathering with your first focused question."""
            
            conv_response = self.agents['conversation_agent'].generate_reply([
                {"role": "user", "content": conv_prompt}
            ])
            
            response = f"Great! I'll help create a PRD.\n\n{conv_response}"
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "stage": "requirements_gathering",
                "intent": "prd"
            }
        
        else:
            response = "I create Product Requirements Documents. Please describe a product you want to document."
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "stage": "initial",
                "intent": "other"
            }
    
    def _handle_requirements_gathering(self, user_input: str) -> dict:
        """Handle requirements gathering conversation"""
        
        # Build context from conversation
        context = self._build_conversation_context()
        context += f"\nLatest user response: {user_input}"
        
        # Get agent response
        conv_response = self.agents['conversation_agent'].generate_reply([
            {"role": "user", "content": context}
        ])
        
        # Check if requirements are complete
        if "REQUIREMENTS_COMPLETE" in str(conv_response):
            logging.info("Requirements complete, generating PRD")
            return self._generate_final_prd()
        
        else:
            # Continue conversation
            self.conversation_history.append({"role": "assistant", "content": conv_response})
            
            return {
                "response": conv_response,
                "stage": "requirements_gathering",
                "action": "continue_conversation"
            }
    
    def _generate_final_prd(self) -> dict:
        """Generate final PRD with research"""
        
        try:
            # Extract main topic for research
            first_input = self.conversation_history[0]['content']
            
            # Do research
            logging.info("Performing market research")
            research_prompt = f"""Research market and technical aspects for: {first_input}
            
Find current information about market trends, competitors, and technical best practices."""
            
            research_response = self.agents['research_agent'].generate_reply([
                {"role": "user", "content": research_prompt}
            ])
            
            # Generate PRD
            logging.info("Generating comprehensive PRD")
            conversation_summary = self._build_conversation_context()
            
            prd_prompt = f"""Create comprehensive PRD based on:

CONVERSATION HISTORY:
{conversation_summary}

RESEARCH FINDINGS:
{research_response}

Generate detailed, professional PRD with all required sections."""
            
            prd_response = self.agents['prd_agent'].generate_reply([
                {"role": "user", "content": prd_prompt}
            ])
            
            # Update stage and save
            self.stage = 'complete'
            final_response = f"""Research Summary:
{research_response}

---

# Product Requirements Document

{prd_response}"""
            
            self.conversation_history.append({"role": "assistant", "content": final_response})
            
            # Save conversation
            save_conversation(self.session_id, {
                "conversation_history": self.conversation_history,
                "research": research_response,
                "prd": prd_response
            })
            
            return {
                "response": final_response,
                "stage": "complete",
                "action": "prd_generated",
                "prd": prd_response,
                "research": research_response
            }
            
        except Exception as e:
            logging.error(f"PRD generation failed: {e}")
            return {
                "response": f"PRD generation failed: {str(e)}",
                "stage": "error",
                "action": "generation_failed"
            }
    
    def _handle_post_completion(self, user_input: str) -> dict:
        """Handle interactions after PRD completion"""
        
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['new', 'another', 'different']):
            # Reset for new PRD
            self.__init__()
            return {
                "response": "Starting new PRD session. What product would you like to document?",
                "stage": "initial",
                "action": "new_session"
            }
        
        elif any(word in user_lower for word in ['refine', 'improve', 'modify']):
            response = "What specific section of the PRD would you like me to refine?"
            return {
                "response": response,
                "stage": "complete",
                "action": "refine_request"
            }
        
        else:
            response = """I can help you:
- Start a new PRD
- Refine sections of the current PRD
- Answer questions about the document

What would you like to do?"""
            
            return {
                "response": response,
                "stage": "complete", 
                "action": "show_options"
            }
    
    def _build_conversation_context(self) -> str:
        """Build conversation context for agent prompts"""
        context = "Conversation history:\n"
        for msg in self.conversation_history:
            context += f"{msg['role']}: {msg['content']}\n"
        return context

# Simple function interface for CLI usage
def generate_prd(user_input: str) -> str:
    """Generate PRD from single input (for CLI/testing)"""
    
    workflow = PRDWorkflow()
    
    # Process initial input
    result1 = workflow.process_input(user_input)
    
    if result1.get('stage') == 'requirements_gathering':
        # Simulate additional requirements gathering
        additional_context = f"Please extract all possible requirements from the initial request: {user_input}"
        result2 = workflow.process_input(additional_context)
        
        if 'prd' in result2.get('response', '').lower():
            return result2['response']
        else:
            return "Could not generate PRD from provided information."
    
    return result1['response']