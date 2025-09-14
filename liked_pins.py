from core.models import User, Pinboard, Pin, Likes
from django.utils import timezone
from django.db import transaction

# First create the boards for all users
users = User.objects.all()
boards_created = 0

for user in users:
    # Check if user already has a liked pins board
    liked_board_exists = Pinboard.objects.filter(
        user=user,
        is_liked_collection=True
    ).exists()
    
    if not liked_board_exists:
        # Create a new liked pins board
        liked_board = Pinboard.objects.create(
            user=user,
            name="Liked Pins",
            category="Likes",
            friends_only_comments=False,
            is_liked_collection=True,
            created_at=timezone.now()
        )
        boards_created += 1
        print(f"Created Liked Pins board for {user.name}")
        
        # Find all pins this user has liked
        user_likes = Likes.objects.filter(user=user)
        pins_added = 0
        
        # Add each liked pin to the new board
        for like in user_likes:
            original_pin = like.pin
            
            # Check if this pin is already in the board
            if not Pin.objects.filter(
                user=user,
                board=liked_board,
                root_pin=original_pin.root_pin or original_pin
            ).exists():
                try:
                    with transaction.atomic():
                        # Create a repin in the liked pins board
                        Pin.objects.create(
                            user=user,
                            image=original_pin.image,
                            board=liked_board,
                            timestamp=timezone.now(),
                            repin_from=original_pin,
                            is_original=False,
                            root_pin=original_pin.root_pin or original_pin
                        )
                        pins_added += 1
                except Exception as e:
                    print(f"Error adding pin {original_pin.pin_id}: {e}")
        
        print(f"Added {pins_added} previously liked pins to the board")

print(f"Created {boards_created} new 'Liked Pins' boards")
