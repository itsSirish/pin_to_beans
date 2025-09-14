# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    # profile_picture = models.ForeignKey('Image', models.DO_NOTHING, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'User'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    pin = models.ForeignKey('Pin', models.DO_NOTHING)
    text = models.TextField()
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Follows(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'board_id')
    user = models.ForeignKey(User, models.DO_NOTHING)
    board = models.ForeignKey('Pinboard', models.DO_NOTHING)
    since_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'follows'
        unique_together = (('user', 'board'),)


class Followstream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    name = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'followstream'
        unique_together = (('user', 'name'),)


class Friendship(models.Model):
    pk = models.CompositePrimaryKey('user_id1', 'user_id2')
    user_id1 = models.ForeignKey(User, models.DO_NOTHING, db_column='user_id1')
    user_id2 = models.ForeignKey(User, models.DO_NOTHING, db_column='user_id2', related_name='friendship_user_id2_set')
    since_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friendship'
        unique_together = (('user_id1', 'user_id2'),)


class Friendshiprequest(models.Model):
    pk = models.CompositePrimaryKey('requester_id', 'target_id')
    requester = models.ForeignKey(User, models.DO_NOTHING)
    target = models.ForeignKey(User, models.DO_NOTHING, related_name='friendshiprequest_target_set')
    status = models.TextField()
    request_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friendshiprequest'
        unique_together = (('requester', 'target'),)


class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    url = models.TextField()
    source_url = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, models.DO_NOTHING, db_column='uploaded_by', blank=True, null=True)
    stored_blob = models.BinaryField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'image'


class Imagetag(models.Model):
    pk = models.CompositePrimaryKey('image_id', 'tag_id')
    image = models.ForeignKey(Image, models.DO_NOTHING)
    tag = models.ForeignKey('Tag', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'imagetag'
        unique_together = (('image', 'tag'),)


class Includes(models.Model):
    pk = models.CompositePrimaryKey('stream_id', 'board_id')
    stream = models.ForeignKey(Followstream, models.DO_NOTHING)
    board = models.ForeignKey('Pinboard', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'includes'
        unique_together = (('stream', 'board'),)


class Likes(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'pin_id')
    user = models.ForeignKey(User, models.DO_NOTHING)
    pin = models.ForeignKey('Pin', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'likes'
        unique_together = (('user', 'pin'),)


class Pin(models.Model):
    pin_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    image = models.ForeignKey(Image, models.DO_NOTHING)
    board = models.ForeignKey('Pinboard', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    repin_from = models.ForeignKey('self', models.DO_NOTHING, db_column='repin_from', blank=True, null=True)
    root_pin = models.ForeignKey('self', models.DO_NOTHING, related_name='pin_root_pin_set')
    is_original = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'pin'
        unique_together = (('user', 'image', 'board'),)


class Pinboard(models.Model):
    board_id = models.AutoField(primary_key=True)
    name = models.TextField()
    category = models.TextField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    friends_only_comments = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_liked_collection = models.BooleanField(default=False)

    def __str__(self):
        """
        Return the board's name for display purposes (e.g., in dropdowns).
        """
        return self.name

    class Meta:
        managed = True
        db_table = 'pinboard'
        unique_together = (('user', 'name'),)

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        managed = False
        db_table = 'tag'



class ProfilePicture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='pfp')
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    class Meta:
        db_table = 'profile_picture'

class Followstreamboard(models.Model):
    stream = models.ForeignKey(
        Followstream,
        on_delete=models.CASCADE,
        db_column='stream_id',
        related_name='board_links'
    )
    board  = models.ForeignKey(
        'Pinboard',
        on_delete=models.CASCADE,
        db_column='board_id'
    )

    class Meta:
        db_table = 'followstreamboard'
        unique_together = (('stream', 'board'),)
        # managed=True by default—this table will be created by migrations