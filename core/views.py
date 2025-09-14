
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm, UserRegistrationForm
from .models import User
from .models import Pinboard
from .forms import PinboardForm
import requests
from django.db import transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from .models import Image, Pin, Imagetag, Tag
from .forms import UploadImageForm, RepinForm
from django.core.files.base import ContentFile
from django.utils import timezone
from django.http import HttpResponse
from .models import Image as DBImage
from .models import Likes, Comment
from .forms import LikeForm, CommentForm
from django.db import IntegrityError, DatabaseError
from .models import Friendship
from django.db.models import Q
from django.shortcuts import redirect
from .models import Friendshiprequest
from .forms import FriendRequestForm
from .models import Friendship
from .models import Followstream, Includes
from .forms import FollowStreamForm
from django.shortcuts import get_object_or_404
from collections import defaultdict
from .models import Pin, Image
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pin, Comment, Likes, Imagetag, Tag
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from collections import defaultdict

from .forms import EditProfileForm
from .models import ProfilePicture
from .models import Pin, Followstream  

from .models import Image, ProfilePicture
from .forms import ProfilePictureForm  

def render_with_base(request, template_name, context):
    # Always include profile picture if user is logged in
    if 'user_id' in request.session and 'profile_picture' not in context:
        try:
            user = User.objects.get(user_id=request.session['user_id'])
            pfp_obj = getattr(user, 'pfp', None)
            context['profile_picture'] = pfp_obj.image if pfp_obj else None
        except User.DoesNotExist:
            pass
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, template_name, context)
    else:
        return render(request, template_name, context)
    

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()            
                
                Pinboard.objects.create(
                    user_id=user.user_id,
                    name="Liked Pins",
                    category="Likes",
                    friends_only_comments=False,
                    is_liked_collection=True  
                )
                
                # auto-log them in:
                request.session['user_id'] = user.user_id
                request.session['name'] = user.name
                return redirect('dashboard')  
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                if user.password == form.cleaned_data['password']:  # (✅ in production, use hashing!)
                    request.session['user_id'] = user.user_id
                    request.session['user_name'] = user.name
                    return redirect('dashboard')  # go to a simple welcome page
                else:
                    messages.error(request, "Invalid password.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = LoginForm()
    return render_with_base(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    list(messages.get_messages(request))  # This clears any queued messages
    return redirect('login')

def dashboard(request, stream_id=None):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = get_object_or_404(User, user_id=user_id)

    profile_picture = getattr(user, 'pfp', None)
    profile_picture = profile_picture.image if profile_picture else None

    follow_streams = Followstream.objects.filter(user_id=user_id)

    if stream_id:
        board_ids = Includes.objects.filter(stream_id=stream_id).values_list('board_id', flat=True)
        pins = Pin.objects.filter(board_id__in=board_ids, is_original=True)\
                         .select_related('image', 'user', 'board')\
                         .order_by('-timestamp')[:50]
    else:
        pins = Pin.objects.filter(is_original=True)\
                         .select_related('image', 'user', 'board')\
                         .order_by('-timestamp')[:50]

    liked_root_pins = Likes.objects.filter(user_id=user_id).values_list('pin__root_pin_id', flat=True)

    return render_with_base(request, 'dashboard.html', {
        'pins': pins,
        'profile_picture': profile_picture,
        'user_id': user.user_id,
        'follow_streams': follow_streams,
        'active_stream_id': stream_id,
        'liked_pins': set(liked_root_pins),
    })

def pinboard_list(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    user_id = request.session['user_id']
    user = get_object_or_404(User, user_id=user_id)
    profile_picture = getattr(user, 'pfp', None)
    profile_picture = profile_picture.image if profile_picture else None
    
    boards = Pinboard.objects.filter(user_id=user_id)
    
    preview_images = {}
    for board in boards:
        pins = Pin.objects.filter(board_id=board.board_id)[:4]
        preview_images[board.board_id] = [pin.image for pin in pins]
    
    return render_with_base(request, 'pinboard_list.html', {
        'boards': boards,
        'user_id': user_id,
        'profile_picture': profile_picture,
        'preview_images': preview_images,
    })


@require_http_methods(["GET", "POST"])
def pinboard_create(request):
    if 'user_id' not in request.session:
        return redirect('login')

    current_user = get_object_or_404(User, user_id=request.session['user_id'])
    profile_picture = current_user.pfp.image if hasattr(current_user, 'pfp') and current_user.pfp else None

    if request.method == 'POST':
        form = PinboardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.user_id = request.session['user_id']
            board.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'result': 'created', 'board_id': board.board_id})
            return redirect('pinboard_list')
    else:
        form = PinboardForm()

    return render_with_base(request, 'pinboard_create.html', {
        'form': form,
        'profile_picture': profile_picture,
    })


def pin_image(request, board_id=None):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']

    user = get_object_or_404(User, user_id=user_id)
    pfp_obj = getattr(user, 'pfp', None)
    profile_picture = pfp_obj.image if pfp_obj else None

    error = None
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES, user_id=user_id)
        if form.is_valid():
            board = form.cleaned_data['board']
            selected_tags = form.cleaned_data['tags']  # This is now a queryset of Tag objects
            method = form.cleaned_data['upload_method']

            if method == 'file':
                f = request.FILES['image_file']
                blob = f.read()
                url = f"/media/{f.name}"
            else:
                url = form.cleaned_data['image_url']
                try:
                    resp = requests.get(url)
                    blob = resp.content
                except:
                    error = "Failed to fetch image from URL."

            if not error:
              
                img = Image.objects.create(
                    url=url,
                    source_url=form.cleaned_data['source_url'],
                    uploaded_by_id=user_id,
                    stored_blob=blob,
                    created_at=timezone.now()
                )

                tag_names = request.POST.get('tag_names', '').split(',')

                for tag_name in tag_names:
                    tag = None 
                    try:
                        tag_id = int(tag_name)
                        tag = Tag.objects.get(tag_id=tag_id)
                    except (ValueError, Tag.DoesNotExist):
                        if tag_name.strip():
                            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())

                    if tag:  
                        Imagetag.objects.create(image=img, tag=tag)
                        
                pin = Pin.objects.create(
                    user_id=user_id,
                    image=img,
                    board=board,
                    timestamp=timezone.now(),
                    is_original=True,
                    root_pin_id=-1
                )
                pin.root_pin_id = pin.pin_id
                pin.save()

                return redirect('dashboard')
    else:
        initial_data = {'board': board_id} if board_id else None
        form = UploadImageForm(user_id=user_id, initial=initial_data)

    
    return render_with_base(request, 'pin_image.html', {
        'form': form,
        'error': error,
        'profile_picture': profile_picture,
    })



from django.db.models import Q
from .models import Pin, Likes, Friendship

def pin_feed(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    pins = Pin.objects.filter(is_original=True)\
        .select_related('image', 'board', 'user')\
        .order_by('-timestamp')[:40]

    for pin in pins:
        board = pin.board
        if board.friends_only_comments:
            board_owner_id = board.user.user_id
            is_friend = Friendship.objects.filter(
                Q(user_id1=board_owner_id, user_id2=user_id) |
                Q(user_id1=user_id, user_id2=board_owner_id)
            ).exists()
            pin.can_comment = is_friend
        else:
            pin.can_comment = True

    liked_root_pins = Likes.objects.filter(user_id=user_id).values_list('pin__root_pin_id', flat=True)

    return render_with_base(request, 'pin_feed.html', {
        'pins': pins,
        'liked_pins': set(liked_root_pins),
        'user_id': user_id,
    })


def repin_select_board(request, pin_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    original_pin = get_object_or_404(Pin, pin_id=pin_id)
    boards = Pinboard.objects.filter(user_id=user_id)

    if request.method == 'POST':
        board_id = request.POST.get('board_id')
        if board_id:
            try:
                Pin.objects.create(
                    user_id=user_id,
                    image=original_pin.image,
                    board_id=board_id,
                    timestamp=timezone.now(),
                    repin_from=original_pin,
                    is_original=False,
                    root_pin_id=original_pin.root_pin_id
                )
                return redirect('board_detail', board_id=board_id)
            except IntegrityError as e:
                if "pin_user_id_image_id_board_id_key" in str(e):
                    messages.error(request, "This pin already exists on this board.")
                else:
                    messages.error(request, "Failed to repin: An unexpected error occurred.")
            except Exception as e:
                messages.error(request, f"Failed to repin: {e}")
        else:
            messages.error(request, "Please select a board.")

    return render_with_base(request, 'repin_select_board.html', {
        'pin': original_pin,
        'boards': boards,
        'user_id': user_id,
    })




def board_detail(request, board_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    board = get_object_or_404(Pinboard, board_id=board_id)

    pins = Pin.objects.filter(board=board).select_related('image', 'board', 'user').order_by('-timestamp')[:20]

    for pin in pins:
        if board.friends_only_comments:
            board_owner_id = board.user.user_id
            is_friend = Friendship.objects.filter(
                (Q(user_id1=board_owner_id) & Q(user_id2=user_id)) |
                (Q(user_id1=user_id) & Q(user_id2=board_owner_id))
            ).exists()
            pin.can_comment = is_friend
        else:
            pin.can_comment = True

    liked_pins = Likes.objects.filter(user_id=user_id).values_list('pin_id', flat=True)

    return render_with_base(request, 'board_detail.html', {
        'board': board,
        'pins': pins,
        'liked_pins': set(liked_pins),
        'user_id': user_id,
    })



def image_blob_view(request, image_id):
    image = DBImage.objects.get(pk=image_id)
    return HttpResponse(image.stored_blob, content_type='image/jpeg')

def like_pin(request):
    if request.method == 'POST' and 'user_id' in request.session:
        form = LikeForm(request.POST)
        if form.is_valid():
            pin_id = form.cleaned_data['pin_id']
            user_id = request.session['user_id']

            try:
                pin = Pin.objects.get(pin_id=pin_id)
                root_pin_id = pin.root_pin_id or pin.pin_id
            except Pin.DoesNotExist:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Pin not found'}, status=404)
                return redirect('dashboard')

            like_exists = Likes.objects.filter(user_id=user_id, pin_id=root_pin_id).exists()

            with transaction.atomic():
                if like_exists:
                    Likes.objects.filter(user_id=user_id, pin_id=root_pin_id).delete()
                    
                    try:
                        liked_board = Pinboard.objects.get(user_id=user_id, is_liked_collection=True)
                        Pin.objects.filter(
                            board=liked_board,
                            user_id=user_id,
                            root_pin_id=root_pin_id

                        ).delete()
                    except Pinboard.DoesNotExist:
                        pass  
                        
                    liked = False
                else:
                    Likes.objects.create(user_id=user_id, pin_id=root_pin_id)
                    
                    try:
                        liked_board = Pinboard.objects.get(user_id=user_id, is_liked_collection=True)
                        
                        if not Pin.objects.filter(
                            board=liked_board,
                            user_id=user_id,
                            root_pin_id=root_pin_id
                        ).exists():
                            Pin.objects.create(
                                user_id=user_id,
                                image=pin.image,
                                board=liked_board,
                                timestamp=timezone.now(),
                                repin_from=pin,
                                is_original=False,
                                root_pin_id=root_pin_id
                            )
                    except Pinboard.DoesNotExist:
                        liked_board = Pinboard.objects.create(
                            user_id=user_id,
                            name="Liked Pins",
                            category="Likes",
                            friends_only_comments=False,
                            is_liked_collection=True,
                            created_at=timezone.now()  
                        )
                        
                        Pin.objects.create(
                            user_id=user_id,
                            image=pin.image,
                            board=liked_board,
                            timestamp=timezone.now(),
                            repin_from=pin,
                            is_original=False,
                            root_pin_id=root_pin_id
                        )
                        
                    liked = True
                
            # Get updated count
            like_count = Likes.objects.filter(pin_id=root_pin_id).count()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'liked': liked,
                    'count': like_count
                })
                
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))




def comment_pin(request):
    if request.method == 'POST' and 'user_id' in request.session:
        form = CommentForm(request.POST)
        if form.is_valid():
            pin_id = form.cleaned_data['pin_id']
            user_id = request.session['user_id']
            text = form.cleaned_data['text']

            try:
                Comment.objects.create(user_id=user_id, pin_id=pin_id, text=text)
            except DatabaseError as e:
                messages.error(request, "You must be friends with the board owner to comment on this pin.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def home_redirect(request):
    if 'user_id' in request.session:
        return redirect('dashboard')
    else:
        return redirect('login')
    
from collections import defaultdict
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import User, Pinboard, Friendship, Friendshiprequest, Pin, ProfilePicture

from .models import ProfilePicture

from core.models import User, Pinboard, Friendship, Friendshiprequest, ProfilePicture

from collections import defaultdict
from django.shortcuts import get_object_or_404, redirect, render
from .models import User, Pinboard, Pin, Friendship, Friendshiprequest, ProfilePicture
from django.db.models import Q

def profile_view(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    viewer = get_object_or_404(User, user_id=request.session['user_id'])
    header_pfp = getattr(viewer, 'pfp', None)
    header_pfp = header_pfp.image if header_pfp else None

    target_user = get_object_or_404(User, user_id=user_id)
    target_pfp = getattr(target_user, 'pfp', None)
    target_pfp = target_pfp.image if target_pfp else None

    boards = Pinboard.objects.filter(user_id=target_user.user_id)
    friend_count = Friendship.objects.filter(
        Q(user_id1=target_user.user_id) | Q(user_id2=target_user.user_id)
    ).count()
    is_owner = (viewer.user_id == target_user.user_id)
    is_friend = Friendship.objects.filter(
        (Q(user_id1=viewer.user_id) & Q(user_id2=target_user.user_id)) |
        (Q(user_id1=target_user.user_id) & Q(user_id2=viewer.user_id))
    ).exists()
    request_pending = Friendshiprequest.objects.filter(
        requester_id=viewer.user_id,
        target_id=target_user.user_id,
        status='PENDING'
    ).exists()
    show_friend_button = not is_owner and not is_friend and not request_pending

    preview_images = defaultdict(list)
    for board in boards:
        pins = (Pin.objects
                  .filter(board=board)
                  .select_related('image')
                  .order_by('-timestamp')[:4])
        for pin in pins:
            preview_images[board.board_id].append(pin.image)

    return render_with_base(request, 'profile.html', {
        'profile_picture': header_pfp,            
        'target_profile_picture': target_pfp,     
        'target_user': target_user,
        'boards': boards,
        'friend_count': friend_count,
        'is_friend': is_friend,
        'show_friend_button': show_friend_button,
        'request_pending': request_pending,
        'preview_images': preview_images,
    })



@require_POST
def send_friend_request(request):
    if 'user_id' not in request.session:
        return JsonResponse({'result':'error','message':'Not authenticated.'}, status=403)

    form = FriendRequestForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'result':'error','message':'Please enter a valid email.'}, status=400)

    requester_id = request.session['user_id']
    target_email = form.cleaned_data['target_email']

    try:
        target_user = User.objects.get(email=target_email)
    except User.DoesNotExist:
        return JsonResponse({'result':'error','message':'No user with that email.'}, status=400)

    if target_user.user_id == requester_id:
        return JsonResponse({'result':'error','message':"Cannot friend yourself."}, status=400)

    existing = Friendshiprequest.objects.filter(
        requester_id=requester_id,
        target_id   =target_user.user_id,
    ).first()

    if existing:
        if existing.status != 'PENDING':
            existing.status = 'PENDING'
            existing.save(update_fields=['status'])
        return JsonResponse({'result':'pending','email': target_email})

    try:
        Friendshiprequest.objects.create(
            requester_id=requester_id,
            target_id   =target_user.user_id,
            status      ='PENDING'
        )
    except IntegrityError:
        return JsonResponse({'result':'pending','email': target_email})

    return JsonResponse({'result':'pending','email': target_email})
def friend_requests_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    incoming = Friendshiprequest.objects.filter(target_id=user_id, status='PENDING').select_related('requester')

    return render_with_base(request, 'friend_requests.html', {
        'requests': incoming,
        'user_id': user_id,
    })

@require_POST
def handle_friend_request(request, requester_id, action):
    if 'user_id' not in request.session:
        return redirect('login')
    target_id = request.session['user_id']

    try:
        fr = Friendshiprequest.objects.get(
            requester_id=requester_id,
            target_id=target_id,
            status='PENDING'
        )
        if action == 'accept':
            requester = User.objects.get(user_id=requester_id)
            target    = User.objects.get(user_id=target_id)
            user1, user2 = sorted([requester, target], key=lambda u: u.user_id)
            Friendship.objects.create(user_id1=user1, user_id2=user2)
            fr.status = 'ACCEPTED'
        else:
            fr.status = 'REJECTED'
        fr.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if action == 'accept':
                return JsonResponse({
                    'result':'accepted',
                    'user': {
                        'user_id': requester.user_id,
                        'name':     requester.name,
                        'email':    requester.email,
                    }
                })
            else:
                return JsonResponse({'result':'rejected'})
    except Friendshiprequest.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error':'Friend request not found.'}, status=404)
        messages.error(request, "Friend request not found or already handled.")
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f"Something went wrong: {e}")

    return redirect('friend_list')

def friend_list(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']
    current_user = get_object_or_404(User, user_id=user_id)
    profile_picture = (
        current_user.pfp.image
        if hasattr(current_user, 'pfp') and current_user.pfp
        else None
    )
    form = FriendRequestForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            target_email = form.cleaned_data['target_email']
            try:
                target_user = User.objects.get(email=target_email)
                if target_user.user_id == user_id:
                    raise ValueError("You cannot friend yourself.")
                if Friendshiprequest.objects.filter(requester_id=user_id, target_id=target_user.user_id).exists():
                    raise ValueError("Already sent.")
                Friendshiprequest.objects.create(
                    requester_id=user_id,
                    target_id=target_user.user_id,
                    status='PENDING'
                )
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'result': 'pending',
                        'email': target_email
                    })
                messages.success(request, "Friend request sent.")
            except User.DoesNotExist:
                error = "No user with that email."
            except ValueError as e:
                error = str(e)
        else:
            error = "Please enter a valid email."
        # AJAX error
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'result':'error','error':error}, status=400)
        messages.error(request, error)

    friendships = Friendship.objects.filter(
        Q(user_id1=user_id) | Q(user_id2=user_id)
    ).select_related('user_id1','user_id2')
    friends = [
        f.user_id2 if f.user_id1.user_id==user_id else f.user_id1
        for f in friendships
    ]

    incoming = Friendshiprequest.objects.filter(
        target_id=user_id, status='PENDING'
    ).select_related('requester')

    return render_with_base(request, 'friend_list.html', {
        'friends': friends,
        'incoming': incoming,
        'form': form,
        'profile_picture': profile_picture,
    })

from .models import Followstream, Includes

def follow_streams_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    streams = Followstream.objects.filter(user_id=user_id)
    return render_with_base(request, 'follow_streams.html', {
        'streams': streams,
        'user_id': user_id,
    })


def create_follow_stream(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        form = FollowStreamForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            Followstream.objects.create(
                user_id=request.session['user_id'],
                name=name
            )
            return redirect('dashboard')
    else:
        form = FollowStreamForm()

    return render_with_base(request, 'create_follow_stream.html', {
        'form': form,
        'user_id': request.session['user_id'],
    })


from .models import Pinboard

def browse_boards(request):
    if 'user_id' not in request.session:
        return redirect('login')
    storage = messages.get_messages(request)
    storage.used = True

    user_id = request.session['user_id']
    boards = Pinboard.objects.exclude(user_id=user_id).exclude(is_liked_collection=True)
    preview_images = defaultdict(list)
    for board in boards:
        pins = Pin.objects.filter(board=board).select_related('image').order_by('-timestamp')[:4]
        preview_images[board.board_id] = [pin.image for pin in pins]

    return render_with_base(request, 'browse_boards.html', {
        'boards': boards,
        'user_id': user_id,
        'preview_images': preview_images,
        'hide_messages': True
    })

def add_board_to_stream(request, board_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    streams = Followstream.objects.filter(user_id=user_id)

    if request.method == 'POST':
        stream_id = request.POST.get('stream_id')
        try:
            Includes.objects.create(stream_id=stream_id, board_id=board_id)
            messages.success(request, "Board added to stream.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('browse_boards')

    return render_with_base(request, 'add_board_to_stream.html', {
        'streams': streams,
        'board_id': board_id,
        'user_id': user_id,
    })




def follow_stream_detail(request, stream_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    try:
        stream = Followstream.objects.get(stream_id=stream_id, user_id=user_id)
    except Followstream.DoesNotExist:
        messages.error(request, "Stream not found.")
        return redirect('follow_streams')

    board_ids = Includes.objects.filter(stream_id=stream_id).values_list('board_id', flat=True)

    pins = Pin.objects.filter(board_id__in=board_ids).select_related('image', 'user', 'board').order_by('-timestamp')

    for pin in pins:
        if pin.board.friends_only_comments:
            board_owner_id = pin.board.user.user_id
            is_friend = Friendship.objects.filter(
                (Q(user_id1=board_owner_id) & Q(user_id2=user_id)) |
                (Q(user_id1=user_id) & Q(user_id2=board_owner_id))
            ).exists()
            pin.can_comment = is_friend
        else:
            pin.can_comment = True

    liked_pins = Likes.objects.filter(user_id=user_id).values_list('pin_id', flat=True)

    return render_with_base(request, 'follow_stream_detail.html', {
        'stream': stream,
        'pins': pins,
        'liked_pins': set(liked_pins),
        'user_id': user_id,
    })


def search_pins(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    query = request.GET.get('q', '').strip()
    words = query.lower().split()
    
    pins = []
    pinboards = []
    preview_images = {}

    if words:
        pin_q = Q(is_original=True) & ~Q(user_id=user_id)
        tag_q = Q()
        for word in words:
            tag_q |= (
                Q(image__url__icontains=word) |
                Q(image__source_url__icontains=word) |
                Q(image__imagetag__tag__name__icontains=word)
            )
        pins = (
            Pin.objects
            .filter(pin_q & tag_q)
            .select_related('image', 'user', 'board')
            .distinct()
            .order_by('-timestamp')
        )

        board_q = Q()
        for word in words:
            board_q |= Q(name__icontains=word) | Q(category__icontains=word)

        pinboards = (
            Pinboard.objects
            .filter(board_q)
            .exclude(user_id=user_id)
            .select_related('user')
        )

        for board in pinboards:
            preview_images[board.board_id] = list(
                Pin.objects
                .filter(board=board)
                .select_related('image')[:4]
                .values_list('image_id', flat=True)
            )

    return render_with_base(request, 'search_results.html', {
        'query': query,
        'pins': pins,
        'pinboards': pinboards,
        'preview_images': preview_images,
        'streams': Followstream.objects.filter(user_id=user_id),
        'user_id': user_id,
    })

def add_to_follow_stream(request, board_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    board = get_object_or_404(Pinboard, board_id=board_id)

    if board.user_id == user_id:
        messages.error(request, "You can't follow your own board.")
        return redirect('profile', user_id=board.user_id)

    if request.method == 'POST':
        stream_id = request.POST['stream_id']
        try:
            Includes.objects.create(stream_id=stream_id, board_id=board_id)
            messages.success(request, "Board added to stream!")
        except:
            messages.error(request, "Already included or failed to add.")
        return redirect('profile', user_id=board.user_id)

    streams = Followstream.objects.filter(user_id=user_id)
    return render_with_base(request, 'add_to_stream.html', {
        'streams': streams,
        'board': board
    })


def profile_friends_view(request, user_id):
    if 'user_id' not in request.session:
        return redirect('login')

    viewer = get_object_or_404(User, user_id=request.session['user_id'])
    header_pfp = getattr(viewer, 'pfp', None)
    header_pfp = header_pfp.image if header_pfp else None

    owner = get_object_or_404(User, user_id=user_id)

    friendships = Friendship.objects.filter(
        Q(user_id1=user_id) | Q(user_id2=user_id)
    ).select_related('user_id1', 'user_id2')

    friends = []
    for f in friendships:
        friends.append(f.user_id2 if f.user_id1.user_id == user_id else f.user_id1)

    return render_with_base(request, 'friend_list.html', {
        'profile_picture': header_pfp,  
        'friends': friends,
        'is_own_list': (owner.user_id == viewer.user_id),
        'owner': owner,
    })

def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, user_id=request.session['user_id'])

    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        picture_form = ProfilePictureForm(request.POST, request.FILES)
        
        if form.is_valid():
            user.name = form.cleaned_data['name']

            user.save()
            messages.success(request, "Profile information updated.")
            
        if picture_form.is_valid():
            upload_method = picture_form.cleaned_data['upload_method']
            if upload_method == 'file' and picture_form.cleaned_data['image_file']:

                user.profile_picture = picture_form.cleaned_data['image_file']
                user.save()
                messages.success(request, "Profile picture updated.")
            elif upload_method == 'url' and picture_form.cleaned_data['image_url']:

                user.profile_picture_url = picture_form.cleaned_data['image_url']
                user.save()
                messages.success(request, "Profile picture updated.")
                
        return redirect('profile', user_id=user.user_id)
    else:
        form = EditProfileForm(initial={
            'name': user.name,
            'email': user.email,
        })
        picture_form = ProfilePictureForm()

    return render_with_base(request, 'edit_profile.html', {
        'form': form,
        'picture_form': picture_form,
        'user_id': user.user_id,  
    })



def delete_pin_and_descendants(pin_id):
    children = Pin.objects.filter(repin_from_id=pin_id)
    for child in children:
        delete_pin_and_descendants(child.pin_id)
    Pin.objects.filter(pin_id=pin_id).delete()

@require_POST
def delete_pin(request, pin_id):
    if 'user_id' not in request.session:
        return redirect('login')

    pin = get_object_or_404(Pin, pin_id=pin_id)

    if pin.user_id != request.session['user_id']:
        messages.error(request, "You can't delete someone else's pin.")
        return redirect('dashboard')

    delete_pin_and_descendants(pin_id)
    messages.success(request, "Pin and all repins deleted.")

    return redirect('board_detail', board_id=pin.board.board_id)


def pin_detail(request, pin_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    pin = get_object_or_404(Pin.objects.select_related('image', 'user', 'board'), pin_id=pin_id)

    comments = Comment.objects.filter(pin=pin).select_related('user').order_by('-timestamp')
    liked = Likes.objects.filter(user_id=user_id, pin_id=pin.root_pin_id).exists()


    tag_ids = Imagetag.objects.filter(image=pin.image).values_list('tag_id', flat=True)
    tags = Tag.objects.filter(tag_id__in=tag_ids)

    related_pins = (
        Pin.objects
        .filter(
            is_original=True,
            image__imagetag__tag_id__in=tag_ids
        )
        .exclude(image=pin.image)  
        .select_related('image', 'user', 'board')
        .distinct()
        .order_by('-timestamp')[:10]
    )

    is_owner = pin.user_id == user_id

    return render_with_base(request, 'pin_detail.html', {
        'pin': pin,
        'comments': comments,
        'liked': liked,
        'related_pins': related_pins,
        'is_owner': is_owner,
        'tags': tags,
    })


# views.py
def edit_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = get_object_or_404(User, user_id=request.session['user_id'])

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES)

        if form.is_valid():
            method = form.cleaned_data['upload_method']
            img = None

            if method == 'file':
                image_file = request.FILES.get('image_file')
                if image_file:
                    img = Image.objects.create(
                        url='',
                        stored_blob=image_file.read(),
                        uploaded_by=user,
                        created_at=timezone.now()
                    )

            elif method == 'url':
                url = form.cleaned_data['image_url']
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    img = Image.objects.create(
                        url=url,
                        stored_blob=response.content,
                        uploaded_by=user,
                        created_at=timezone.now()
                    )
                except Exception:
                    messages.error(request, "Failed to fetch image from URL.")
                    return redirect('edit_profile')

            if img:
                ProfilePicture.objects.update_or_create(user=user, defaults={'image': img})
                messages.success(request, "Profile picture updated.")
            return redirect('profile', user_id=user.user_id)

    else:
        form = ProfilePictureForm()

    return render_with_base(request, 'edit_profile.html', {'form': form})


from django.views.decorators.http import require_POST



@require_POST
def unfriend(request):
    if 'user_id' not in request.session:
        return redirect('login')

    me = request.session['user_id']
    them = request.POST.get('target_user_id')
    if not them:
        messages.error(request, "Invalid user.")
        return redirect('dashboard')

    u1, u2 = sorted([int(me), int(them)])
    Friendship.objects.filter(user_id1=u1, user_id2=u2).delete()
    Friendshiprequest.objects.filter(
        Q(requester_id=u1, target_id=u2) |
        Q(requester_id=u2, target_id=u1)
    ).delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'result':'unfriended','user_id': int(them)})

    messages.success(request, "Unfriended successfully.")
    return redirect('profile', user_id=them)

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET","POST"])
def select_board_to_pin(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    boards = Pinboard.objects.filter(user_id=user_id)

    if request.method == 'POST':
        board_id = request.POST.get('board_id')
        if board_id:
            return redirect('pin_image', board_id=board_id)

        error = "Please select a board."
        return render_with_base(request, 'select_board_to_pin.html', {
            'boards': boards,
            'error': error,
        })

    return render_with_base(request, 'select_board_to_pin.html', {
        'boards': boards
    })




@require_POST
def delete_user(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = get_object_or_404(User, user_id=user_id)

    Pinboard.objects.filter(user_id=user_id).delete()

    user.delete()

    request.session.flush()

    messages.success(request, "Your account has been permanently deleted.")
    return redirect('register')

@require_POST
def delete_pinboard(request, board_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    board = get_object_or_404(Pinboard, board_id=board_id, user_id=user_id)

    Includes.objects.filter(board_id=board_id).delete()

    board.delete()

    messages.success(request, "Pinboard deleted successfully.")
    return redirect('pinboard_list')


@require_POST
def delete_follow_stream(request, stream_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    stream = get_object_or_404(Followstream, stream_id=stream_id, user_id=user_id)

    Includes.objects.filter(stream_id=stream_id).delete()
    stream.delete()

    messages.success(request, "Follow stream deleted.")
    return redirect('follow_streams')