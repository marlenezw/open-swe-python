#!/usr/bin/env python3
import sys
import os

# Rich imports for enhanced terminal display
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ANSI color codes (fallback when rich is not available)
PURPLE = '\033[95m'
PURPLE_BG = '\033[105m'
BOLD = '\033[1m'
RESET = '\033[0m'
WHITE = '\033[97m'

# Initialize rich console
console = Console() if RICH_AVAILABLE else None

def print_welcome_message():
    """Print a purple block-style welcome message for open-swe"""
    
    # Block-style banner using Unicode block characters
    banner = f"""{PURPLE}
 ██████╗ ██████╗ ███████╗███╗   ██╗      ███████╗██╗    ██╗███████╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║      ██╔════╝██║    ██║██╔════╝
██║   ██║██████╔╝█████╗  ██╔██╗ ██║█████╗███████╗██║ █╗ ██║█████╗  
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║╚════╝╚════██║██║███╗██║██╔══╝  
╚██████╔╝██║     ███████╗██║ ╚████║      ███████║╚███╔███╔╝███████╗
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝      ╚══════╝ ╚══╝╚══╝ ╚══════╝
{RESET}"""
    
    # Box drawing for frame
    frame_top = f"{PURPLE}┌{'─' * 50}┐{RESET}"
    frame_bottom = f"{PURPLE}└{'─' * 50}┘{RESET}"
    
    # Welcome text with box
    print()
    print(banner)
    print()
    print(frame_top)
    print(f"{PURPLE}│{RESET} {BOLD}Welcome to Open-SWE!{RESET}                            {PURPLE}│{RESET}")
    print(f"{PURPLE}│{RESET}                                                  {PURPLE}│{RESET}")
    print(f"{PURPLE}│{RESET} Your software engineering workspace is ready.    {PURPLE}│{RESET}")
    print(f"{PURPLE}│{RESET} Type 'help' for available commands.              {PURPLE}│{RESET}")
    print(frame_bottom)
    
    # System info bar
    sys_info = f"Python {sys.version.split()[0]} | {os.name.upper()} System"
    print(f"\n{PURPLE}{'═' * 50}{RESET}")
    print(f"{PURPLE}  {sys_info}{RESET}")
    print(f"{PURPLE}{'═' * 50}{RESET}\n")


def display_agent_status(agent_name: str, status: str = "working"):
    """Display agent status with rich formatting or fallback to ANSI colors."""
    
    # Agent configurations: emoji, color, box style
    agent_configs = {
        "manager": {
            "emoji": "👔",
            "color": "blue",
            "title": "Manager Agent",
            "box_style": box.ROUNDED if RICH_AVAILABLE else None
        },
        "planner": {
            "emoji": "📋", 
            "color": "green",
            "title": "Planner Agent",
            "box_style": box.DOUBLE if RICH_AVAILABLE else None
        },
        "programmer": {
            "emoji": "💻",
            "color": "yellow", 
            "title": "Programmer Agent",
            "box_style": box.HEAVY if RICH_AVAILABLE else None
        }
    }
    
    config = agent_configs.get(agent_name.lower(), {
        "emoji": "🤖",
        "color": "white",
        "title": f"{agent_name.title()} Agent",
        "box_style": box.ROUNDED if RICH_AVAILABLE else None
    })
    
    if RICH_AVAILABLE and console:
        # Rich formatted output
        title_text = Text(f"{config['emoji']} {config['title']} {status.title()}", 
                         style=f"bold {config['color']}")
        panel = Panel(
            "",  # Empty content, just the title
            title=title_text,
            border_style=config['color'],
            box=config['box_style'],
            width=60
        )
        console.print(panel)
    else:
        # Fallback ANSI formatting
        color_codes = {
            "blue": "\033[34m",
            "green": "\033[32m", 
            "yellow": "\033[33m",
            "white": "\033[37m"
        }
        color = color_codes.get(config['color'], "\033[37m")
        print(f"\n{color}{BOLD}┌{'─' * 58}┐{RESET}")
        print(f"{color}│ {config['emoji']} {config['title']} {status.title()}{' ' * (50 - len(config['title']) - len(status))}│{RESET}")
        print(f"{color}└{'─' * 58}┘{RESET}")


def display_agent_thoughts(agent_name: str, thoughts: str):
    """Display agent thoughts with rich formatting."""
    
    if not thoughts or thoughts.strip() == "":
        return
    
    # Agent color mapping
    agent_colors = {
        "manager": "blue",
        "planner": "green", 
        "programmer": "yellow"
    }
    
    color = agent_colors.get(agent_name.lower(), "white")
    
    if RICH_AVAILABLE and console:
        # Rich formatted thoughts
        thoughts_text = Text(thoughts, style=f"{color}")
        panel = Panel(
            thoughts_text,
            title=f"💭 {agent_name.title()} Thinking",
            title_align="left",
            border_style=f"dim {color}",
            box=box.SIMPLE,
            width=80
        )
        console.print(panel)
    else:
        # Fallback ANSI formatting
        color_codes = {
            "blue": "\033[34m",
            "green": "\033[32m",
            "yellow": "\033[33m", 
            "white": "\033[37m"
        }
        ansi_color = color_codes.get(color, "\033[37m")
        print(f"\n{ansi_color}💭 {agent_name.title()} Thinking:{RESET}")
        print(f"{ansi_color}{'─' * 60}{RESET}")
        # Indent thoughts
        for line in thoughts.split('\n'):
            print(f"{ansi_color}  {line}{RESET}")
        print(f"{ansi_color}{'─' * 60}{RESET}")


def display_agent_result(agent_name: str, message: str):
    """Display agent result/decision with rich formatting."""
    
    if not message or message.strip() == "":
        return
    
    agent_colors = {
        "manager": "blue",
        "planner": "green",
        "programmer": "yellow"
    }
    
    color = agent_colors.get(agent_name.lower(), "white")
    
    if RICH_AVAILABLE and console:
        # Rich formatted result
        result_text = Text(message, style=f"bold {color}")
        panel = Panel(
            result_text,
            title=f"✅ {agent_name.title()} Result",
            title_align="left", 
            border_style=color,
            box=box.ROUNDED,
            width=70
        )
        console.print(panel)
    else:
        # Fallback ANSI formatting  
        color_codes = {
            "blue": "\033[34m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "white": "\033[37m"
        }
        ansi_color = color_codes.get(color, "\033[37m")
        print(f"\n{ansi_color}{BOLD}✅ {agent_name.title()} Result:{RESET}")
        print(f"{ansi_color}{message}{RESET}\n")


if __name__ == "__main__":
    # You can choose which version to use
    print_welcome_message()  # Detailed version
    # print_compact_version()  # Compact version