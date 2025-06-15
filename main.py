#!/usr/bin/env python3
"""
AutoGen PRD Generator - Simple Entry Point
"""

from workflow import generate_prd
import logging
logging.basicConfig(level=logging.INFO)

def main():
    logging.info("🤖 AutoGen PRD Generator")
    logging.info("Using Ollama + Qwen3:8b locally")
    logging.info("=" * 50)
    
    while True:
        user_input = input("\n📝 Describe your product idea (or 'quit' to exit): ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            logging.info("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
            
        logging.info("\n🔄 Generating PRD...")
        try:
            prd = generate_prd(user_input)
            logging.info("\n📋 Generated PRD:")
            logging.info("=" * 50)
            logging.info(prd)
            logging.info("=" * 50)
            
        except Exception as e:
            logging.info(f"❌ Error: {e}")
            logging.info("Make sure Ollama is running: ollama serve")

if __name__ == "__main__":
    main()