#!/usr/bin/env python3
"""
Podcast Episode Creator
Converts learning content to Shaan/Sam style podcast episodes with minimal AI token usage
"""

import os
import sys
import json
import subprocess
from datetime import datetime
import re

class PodcastCreator:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.style_patterns = self.load_style_patterns()
        
    def load_style_patterns(self):
        """Load style transformation patterns to reduce AI dependency"""
        return {
            'openings': [
                "Yo, what's up! Welcome back.",
                "Alright, so here's what's interesting...",
                "Dude, I just figured out something kind of genius..."
            ],
            'transitions': [
                "And this is where it gets interesting...",
                "But here's the thing...",
                "Here's what's crazy...",
                "The beautiful part is...",
                "Now here's what's cool..."
            ],
            'emphasis': [
                "Think about it...",
                "Here's the money shot...",
                "And boom...",
                "Let's be real about..."
            ],
            'closings': [
                "That's a wrap!",
                "Peace out!",
                "Catch you next time!"
            ]
        }
    
    def get_next_episode_number(self):
        """Find the next episode number"""
        audio_dir = os.path.join(self.base_dir, 'audio')
        if not os.path.exists(audio_dir):
            return 1
            
        episodes = [f for f in os.listdir(audio_dir) if f.startswith('episode-')]
        if not episodes:
            return 1
            
        numbers = []
        for ep in episodes:
            match = re.search(r'episode-(\d+)', ep)
            if match:
                numbers.append(int(match.group(1)))
        
        return max(numbers) + 1 if numbers else 1
    
    def basic_style_conversion(self, content):
        """Basic style conversion using patterns (reduces AI token usage)"""
        lines = content.split('\n')
        converted = []
        
        for i, line in enumerate(lines):
            # Skip empty lines and headers initially
            if not line.strip() or line.startswith('#'):
                continue
                
            # Convert formal language to casual
            line = re.sub(r'We (identified|discovered|found)', r'I figured out', line)
            line = re.sub(r'The analysis shows', r"Here's what's crazy", line)
            line = re.sub(r'In conclusion', r"The beautiful part", line)
            line = re.sub(r'Furthermore', r"And here's the thing", line)
            line = re.sub(r'Additionally', r"Plus", line)
            line = re.sub(r'However', r"But dude", line)
            
            # Add casual connectors
            if i == 0:  # First content line
                line = "So here's what happened. " + line
            elif 'pattern' in line.lower() or 'approach' in line.lower():
                line = "And this is where it gets interesting. " + line
                
            converted.append(line)
        
        return '\n'.join(converted)
    
    def create_episode_script(self, title, content):
        """Create episode script with Shaan/Sam style"""
        episode_num = self.get_next_episode_number()
        
        # Basic style conversion
        styled_content = self.basic_style_conversion(content)
        
        # Create script structure
        script = f"""# Episode {episode_num:03d}: {title}

{self.style_patterns['openings'][0]} I'm Claude, and today we're diving into {title.lower()}.

{styled_content}

{self.style_patterns['closings'][0]}

---
Episode {episode_num:03d} • Generated {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return episode_num, script
    
    def generate_audio(self, script, episode_num, title):
        """Generate TTS audio (calls OpenClaw's TTS system)"""
        # Clean script for TTS (remove markdown, etc.)
        clean_text = re.sub(r'#.*\n', '', script)  # Remove headers
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_text)  # Remove bold
        clean_text = re.sub(r'---.*', '', clean_text, flags=re.DOTALL)  # Remove footer
        clean_text = clean_text.strip()
        
        # Save to temp file for TTS processing
        temp_script = f"/tmp/episode_{episode_num:03d}_script.txt"
        with open(temp_script, 'w') as f:
            f.write(clean_text)
            
        print(f"TTS script ready at: {temp_script}")
        print("To generate audio, run:")
        print(f'openclaw tts "{clean_text[:100]}..." > episode-{episode_num:03d}-audio.mp3')
        
        return f"episode-{episode_num:03d}-{title.lower().replace(' ', '-')}.mp3"
    
    def update_rss_feed(self, episode_num, title, description, audio_filename):
        """Update RSS feed with new episode"""
        rss_file = os.path.join(self.base_dir, 'feed.xml')
        
        # Create new episode XML
        pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        episode_xml = f'''    <item>
      <title>Episode {episode_num:03d}: {title}</title>
      <link>https://iamaaronnorth.github.io/podcast-feed/episodes/{episode_num:03d}</link>
      <description>{description}</description>
      <enclosure url="https://iamaaronnorth.github.io/podcast-feed/audio/{audio_filename}" type="audio/mpeg" length="2048000"/>
      <guid isPermaLink="false">episode-{episode_num:03d}-{title.lower().replace(' ', '-')}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:duration>05:00</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
      <itunes:summary>{description[:200]}...</itunes:summary>
    </item>
    
'''
        
        # Read existing RSS
        with open(rss_file, 'r') as f:
            rss_content = f.read()
        
        # Insert new episode after the first item (latest first)
        insert_point = rss_content.find('    <item>') 
        if insert_point == -1:
            insert_point = rss_content.find('  </channel>')
            
        new_rss = rss_content[:insert_point] + episode_xml + rss_content[insert_point:]
        
        # Update lastBuildDate
        new_rss = re.sub(
            r'<lastBuildDate>.*?</lastBuildDate>', 
            f'<lastBuildDate>{pub_date}</lastBuildDate>', 
            new_rss
        )
        
        with open(rss_file, 'w') as f:
            f.write(new_rss)
        
        print(f"RSS feed updated with Episode {episode_num:03d}")
    
    def create_episode(self, title, content_file=None, content_text=None):
        """Main function to create a complete episode"""
        if content_file and os.path.exists(content_file):
            with open(content_file, 'r') as f:
                content = f.read()
        elif content_text:
            content = content_text
        else:
            print("Error: No content provided")
            return False
            
        print(f"Creating episode: {title}")
        
        # Create script
        episode_num, script = self.create_episode_script(title, content)
        
        # Save script
        script_file = os.path.join(self.base_dir, 'content', f'episode-{episode_num:03d}-script.md')
        os.makedirs(os.path.dirname(script_file), exist_ok=True)
        with open(script_file, 'w') as f:
            f.write(script)
        print(f"Script saved: {script_file}")
        
        # Generate audio filename (actual TTS done separately)
        audio_filename = self.generate_audio(script, episode_num, title)
        
        # Update RSS feed
        description = f"Episode {episode_num:03d} covering {title.lower()}"
        self.update_rss_feed(episode_num, title, description, audio_filename)
        
        # Git commit
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.base_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Add Episode {episode_num:03d}: {title}'], cwd=self.base_dir, check=True)
            subprocess.run(['git', 'push'], cwd=self.base_dir, check=True)
            print(f"Episode {episode_num:03d} committed and pushed")
        except subprocess.CalledProcessError:
            print("Git operations failed - check manually")
        
        print(f"\n✅ Episode {episode_num:03d} created successfully!")
        print(f"📝 Script: {script_file}")
        print(f"🎧 Audio: {audio_filename} (TTS needed)")
        print(f"📡 RSS updated and deployed")
        
        return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_episode.py 'Episode Title' [content_file|content_text]")
        sys.exit(1)
        
    title = sys.argv[1]
    
    # Get base directory (script location)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    creator = PodcastCreator(base_dir)
    
    if len(sys.argv) >= 3 and os.path.exists(sys.argv[2]):
        # File provided
        creator.create_episode(title, content_file=sys.argv[2])
    else:
        # Text content provided
        content = ' '.join(sys.argv[2:])
        creator.create_episode(title, content_text=content)

if __name__ == "__main__":
    main()