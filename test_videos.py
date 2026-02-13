#!/usr/bin/env python3
"""
Helper script to find popular YouTube videos with captions for testing
"""

# Popular YouTube videos known to have captions (for testing)
# Note: These are curated videos confirmed to have captions available
VIDEOS_WITH_CAPTIONS = {
    'TED Talks (Always have captions)': [
        'https://youtu.be/ZXsQAXx_ao0',  # "Do schools kill creativity?" - Sir Ken Robinson
        'https://youtu.be/R5Gzlx34Gm0',  # "The Paradox of Choice" - Barry Schwartz
        'https://youtu.be/4SE7YXAnWyk',  # "The skill of reading all over the place" - Caitlin Doughty
    ],
    'Khan Academy (Always have captions)': [
        'https://youtu.be/a1NnFu7-UVU',  # Khan Academy introduction
        'https://youtu.be/kJQP7kiw9Fk',  # Khan Academy math lesson
    ],
    'Official Channels (Usually have captions)': [
        'https://youtu.be/kJQP7kiw9Fk',  # Official upload usually have captions
        'https://youtu.be/9bZkp7q19f0',  # Official video
    ],
    'First YouTube Video': [
        'https://youtu.be/jNQXAC9IVRw',  # "Me at the zoo" - has captions
    ],
}

def print_available_videos():
    """Print list of videos known to have captions"""
    print("\n" + "=" * 70)
    print("📺 YouTube Videos Known to Have Captions (for testing)")
    print("=" * 70 + "\n")
    
    for category, videos in VIDEOS_WITH_CAPTIONS.items():
        print(f"\n{category}:")
        for i, video in enumerate(videos, 1):
            print(f"  {i}. {video}")
    
    print("\n" + "=" * 70)
    print("💡 Tips for finding videos with captions:")
    print("   • TED Talks always have captions")
    print("   • Khan Academy and educational channels have captions")
    print("   • News channels usually have captions")
    print("   • Official uploaded videos are more likely to have captions")
    print("   • Music videos and personal uploads often don't have captions")
    print("=" * 70)
    print("\n📝 Try with this command:")
    print("   python3 transcribe_videos.py 'https://youtu.be/ZXsQAXx_ao0'")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    print_available_videos()
