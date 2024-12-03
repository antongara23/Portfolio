from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'rental'

urlpatterns = [
    path("", views.redirect_to_main, name="index"),
    path("main", views.index, name="main"),
    path("ad-<int:ad_id>", views.index, name="open-ad"),
    path("create", views.create_ad, name="create"),
    path("edit/<int:ad_id>", views.edit_ad, name="edit"),
    path("profile", views.profile, name="profile"),
    path("profile-<str:section>", views.profile, name="profile-section"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # For use by JS fetch functions:
    path("index/message/<int:ad_id>", views.start_dialog, name="start_dialog"),
    path("ad/<int:ad_id>", views.load_ad, name="load_ad"),
    path("ad/is_saved/<int:ad_id>", views.is_saved, name="is_saved"),
    path("ad/save/<int:ad_id>", views.to_saved, name="save_ad"),
    path("ad/activate/<int:ad_id>", views.change_active, name="change_active"),
    path("profile/load_ads", views.profile_load_ads, name="profile_load_ads"),
    path("profile/load_saved", views.profile_load_saved, name="profile_load_saved"),
    path("profile/dialogs", views.load_dialogs, name="load_dialogs"),
    path("profile/dialog/<int:dialog_id>", views.load_dialog, name="load_dialog"),
    path("profile/message/<int:dialog_id>", views.send_message, name="send_message"),
    path("profile/update", views.update_profile, name="profile_update"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

