from core.models import User, Pinboard
from django.utils import timezone
import sys

# Get all existing users
users = User.objects.all()
boards_created = 0

# Create liked pins board for each user
for user in users:
    # Check if user already has a liked pins board
    liked_board_exists = Pinboard.objects.filter(
        user=user,
        is_liked_collection=True
    ).exists()
    
    if not liked_board_exists:
        # Create a new liked pins board
        try:
            Pinboard.objects.create(
                user=user,
                name="Liked Pins",
                category="Likes",
                friends_only_comments=False,
                is_liked_collection=True,
                created_at=timezone.now()
            )
            boards_created += 1
            print(f"Created Liked Pins board for {user.name}")
        except Exception as e:
            print(f"Error creating board for {user.name}: {e}")

print(f"Created {boards_created} new 'Liked Pins' boards")
sys.stdout.flush()  # Force output to be displayed
