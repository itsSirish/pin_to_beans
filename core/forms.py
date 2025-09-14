from django import forms
from .models import User
from .models import Pinboard
from .models import Image, Pin, Tag

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords must match.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # Simple assignment (not hashed):
        user.password = self.cleaned_data['password1']
        # If you want hashing, uncomment:
        # user.password = make_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class PinboardForm(forms.ModelForm):
    class Meta:
        model = Pinboard
        fields = ['name', 'category', 'friends_only_comments']
        widgets = {
            'friends_only_comments': forms.CheckboxInput()
        }


class UploadImageForm(forms.Form):
    board = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Replace the text field with ModelMultipleChoiceField
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'select2-tags',
            'data-placeholder': 'Select tags...'
        }),
        required=False
    )
    
    upload_method = forms.ChoiceField(
        choices=[('file', 'Upload File'), ('url', 'From URL')],
        widget=forms.RadioSelect,
        initial='file'
    )
    
    image_file = forms.ImageField(required=False)
    image_url = forms.URLField(required=False)
    source_url = forms.URLField(required=False)
    
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        if user_id:
            self.fields['board'].queryset = Pinboard.objects.filter(user_id=user_id)
    
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('upload_method')
        
        if method == 'file' and not cleaned_data.get('image_file'):
            self.add_error('image_file', 'Please select a file to upload.')
        elif method == 'url' and not cleaned_data.get('image_url'):
            self.add_error('image_url', 'Please enter an image URL.')
            
        return cleaned_data
    
class RepinForm(forms.Form):
    board_id = forms.IntegerField()
    pin_id = forms.IntegerField(widget=forms.HiddenInput)


class LikeForm(forms.Form):
    pin_id = forms.IntegerField(widget=forms.HiddenInput)

class CommentForm(forms.Form):
    pin_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea, min_length=1)

class FriendRequestForm(forms.Form):
    target_email = forms.EmailField(label="Friend's Email")

class FollowStreamForm(forms.Form):
    name = forms.CharField(label="Stream Name", max_length=100)

class EditProfileForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    email = forms.EmailField(label="Email")

class ProfilePictureForm(forms.Form):
    upload_method = forms.ChoiceField(choices=[('file', 'Upload File'), ('url', 'Paste URL')])
    image_file = forms.ImageField(required=False)
    image_url = forms.URLField(required=False)


class PinForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'id': 'tag-input',
            'multiple': 'multiple',
            'style': 'display: none;'  # hide the select box
        }),
        required=False,
        label='Tags'
    )
    
    upload_method = forms.ChoiceField(
        choices=[('file', 'Upload File'), ('url', 'From URL')],
        widget=forms.RadioSelect,
        initial='file'
    )
    
    image_file = forms.ImageField(required=False)
    image_url = forms.URLField(required=False)
    source_url = forms.URLField(required=False)
    
    board = forms.ModelChoiceField(
        queryset=None,  # We'll set this in __init__
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['board'].queryset = Pinboard.objects.filter(user=user)
    
    class Meta:
        model = Pin
        fields = ['board', 'tags', 'source_url']
