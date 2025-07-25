#!/usr/bin/env python3
"""
Digital Nomad Travel Assistant - Chatbot Version
A friendly, conversational AI travel assistant powered by Perplexity's Sonar models.
"""

import os
import sys
import requests
import json
import argparse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
import time

console = Console()

@dataclass
class ConversationTurn:
    user_message: str
    assistant_response: str
    timestamp: float
    search_triggered: bool = False

class PerplexityAPI:
    """Perplexity API client for conversational travel assistance"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def chat(self, messages: List[Dict], search_context_size: str = "medium") -> Dict[str, Any]:
        """
        Send conversation to Perplexity's Sonar model
        
        Args:
            messages: List of conversation messages (system, user, assistant)
            search_context_size: 'low', 'medium', or 'high'
        """
        
        payload = {
            "model": "sonar",  # Fastest model for conversational responses
            "messages": messages,
            "web_search_options": {
                "search_context_size": search_context_size
            },
            "max_tokens": 300,  # Shorter responses
            "temperature": 0.8,  # Higher for more excitement
            "stream": False
        }
            
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API Error: {e}[/red]")
            return None

class TravelChatbot:
    """Conversational travel chatbot"""
    
    def __init__(self, api_key: str):
        self.api = PerplexityAPI(api_key)
        self.conversation_history: List[ConversationTurn] = []
        self.system_prompt = """You are an EXCITED, friendly digital nomad travel assistant! 🌍

RULES - FOLLOW THESE EXACTLY:
✅ Keep responses SHORT and DIRECT (1-2 sentences max)
✅ Use an EXCITING, enthusiastic tone with emojis
✅ Give SPECIFIC, actionable info - no fluff or long explanations  
✅ Be SUPER friendly and encouraging
✅ NO lengthy descriptions or unnecessary details
✅ Focus on what they NEED to know RIGHT NOW

For travel questions, give QUICK answers about:
- Visa requirements (just the essentials)
- Internet speeds (numbers and quick verdict)
- Costs (specific prices, direct comparison)
- Best locations (top 2-3 picks with why)
- Coworking/accommodation (best options only)

Examples of perfect responses:
"Portugal's D7 visa needs €2,760/month income proof - totally doable! 🇵🇹 Apply online, takes 2-3 months."
"Lisbon gets 200+ Mbps, perfect for remote work! 💻 Fiber everywhere, tons of coworking spaces."
"Bali is CHEAP! $500-800/month gets you a nice place. Food $2-5/meal. You'll save tons! 💰"

Be EXCITED to help but keep it SHORT and USEFUL!"""

    def get_conversation_context(self, limit: int = 4) -> List[Dict]:
        """Get recent conversation context for API"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent conversation history
        recent_turns = self.conversation_history[-limit:] if self.conversation_history else []
        
        for turn in recent_turns:
            messages.append({"role": "user", "content": turn.user_message})
            messages.append({"role": "assistant", "content": turn.assistant_response})
            
        return messages

    def chat(self, user_input: str, show_progress: bool = True) -> str:
        """
        Process user input and return conversational response
        
        Args:
            user_input: User's question or message
            show_progress: Whether to show progress indicator
        """
        
        # Build conversation context
        messages = self.get_conversation_context()
        messages.append({"role": "user", "content": user_input})
        
        # Show typing indicator (optional)
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[blue]Getting the latest info..."),
                console=console,
                transient=True
            ) as progress:
                progress.add_task("chat", total=None)
                
                # Auto-adjust search context based on query complexity
                word_count = len(user_input.split())
                if word_count > 15:
                    search_context = "high"
                elif word_count > 8:
                    search_context = "medium"
                else:
                    search_context = "low"
                
                response = self.api.chat(messages, search_context)
        else:
            # No progress indicator for command line mode
            word_count = len(user_input.split())
            if word_count > 15:
                search_context = "high"
            elif word_count > 8:
                search_context = "medium"
            else:
                search_context = "low"
            
            response = self.api.chat(messages, search_context)
        
        if not response or 'choices' not in response:
            return "Oops! Something went wrong. Try again? 🤔"
            
        assistant_response = response['choices'][0]['message']['content']
        
        # Store conversation turn (no citations display for cleaner output)
        turn = ConversationTurn(
            user_message=user_input,
            assistant_response=assistant_response,
            timestamp=time.time(),
            search_triggered=True
        )
        self.conversation_history.append(turn)
        
        return assistant_response
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for display"""
        if not self.conversation_history:
            return "No conversation yet"
            
        turn_count = len(self.conversation_history)
        search_count = sum(1 for turn in self.conversation_history if turn.search_triggered)
        
        return f"{turn_count} messages • {search_count} searches • Started {time.strftime('%H:%M', time.localtime(self.conversation_history[0].timestamp))}"

def single_question_mode(chatbot: TravelChatbot, question: str):
    """Handle single question from command line"""
    console.print(f"[bold yellow]Question:[/bold yellow] {question}\n")
    
    # Get response
    response = chatbot.chat(question, show_progress=True)
    
    # Display response
    console.print(f"[bold cyan]Travel Assistant:[/bold cyan] {response}\n")

def interactive_mode(chatbot: TravelChatbot):
    """Handle interactive chat mode"""
    # Welcome message
    console.print(Panel(
        Text("🌍 Digital Nomad Travel Chatbot\n", style="bold blue") +
        Text("Hey! I'm your excited travel buddy! Ask me anything! 🚀", style="white"),
        title="Let's Chat!",
        border_style="blue"
    ))
    
    # Initial greeting
    console.print("\n[bold cyan]Travel Assistant:[/bold cyan] 🔥 What's up! Where do you want to go or what do you need to know?\n")
    
    # Main chat loop
    while True:
        try:
            # Get user input (more natural prompt)
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
            
            # Handle exit commands
            if user_input.lower().strip() in ['quit', 'exit', 'bye', 'goodbye']:
                console.print("\n[bold cyan]Travel Assistant:[/bold cyan] 🎉 Awesome chatting! Safe travels!")
                break
            
            # Handle empty input
            if not user_input.strip():
                console.print("\n[bold cyan]Travel Assistant:[/bold cyan] 💭 I'm ready when you are!")
                continue
                
            # Get chatbot response
            console.print()
            response = chatbot.chat(user_input)
            
            # Display response in a conversational way
            console.print(f"[bold cyan]Travel Assistant:[/bold cyan] {response}")
            
            console.print()  # Add spacing
            
        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Travel Assistant:[/bold cyan] ✈️ Catch you later!")
            break
        except Exception as e:
            console.print(f"\n[red]Whoops! {e}[/red]")

def main():
    """Main application entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Digital Nomad Travel Assistant - Get quick, exciting travel answers!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python travel_assistant.py "What's the internet speed in Lisbon?"
  python travel_assistant.py "Tell me about digital nomad visas for Portugal"
  python travel_assistant.py                    # Interactive mode
        """
    )
    parser.add_argument(
        'question', 
        nargs='?', 
        help='Your travel question (if not provided, starts interactive mode)'
    )
    
    args = parser.parse_args()
    
    # Load API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        console.print(Panel(
            "Please set your PERPLEXITY_API_KEY environment variable.\n"
            "You can get an API key from: https://www.perplexity.ai/",
            title="[red]API Key Required[/red]",
            border_style="red"
        ))
        sys.exit(1)
    
    # Initialize chatbot
    chatbot = TravelChatbot(api_key)
    
    # Decide mode based on arguments
    if args.question:
        # Single question mode
        single_question_mode(chatbot, args.question)
    else:
        # Interactive mode
        interactive_mode(chatbot)

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional
    
    main() 