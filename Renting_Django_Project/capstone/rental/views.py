import json
import re
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponseRedirect, JsonResponse, \
    HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import User, Ad, Message, Dialog
from .forms import NewMessage, NewAd


def read_dialog(request, dialog_object, action: str):
    """
    Change dialog's "read" status depending on user "action".
    "action" is a string: "read" or "send".
    Is used in the load_dialog(), star_dialogs(), send_message().
    """
    if action == "read":
        if request.user == dialog_object.recipient:
            dialog_object.recipient_read = True
        else:
            dialog_object.initiator_read = True
    if action == "send":
        if request.user == dialog_object.recipient:
            dialog_object.initiator_read = False
        else:
            dialog_object.recipient_read = False
    dialog_object.save()


def pagination(request, post_list, num_pages=8):
    paginator = Paginator(post_list, num_pages)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def redirect_to_main(request):
    return redirect("rental:main")


def filter_ads(parameters: dict) -> set:
    """
    Parameters - dict of GET parameters passed in the URL.
    Is used in the index() function.
    Returns QuerySet of Ad model objects.
    """
    city = parameters.get('city', 'all').strip().title()
    city_filter = {} if city == '' else {'city': city}
    pricefrom = parameters.get('pricefrom', 0)
    pricefrom = Decimal(0) if pricefrom == '' else pricefrom
    priceto = parameters.get('priceto', 1_000_000)
    priceto = Decimal(1_000_000) if priceto == '' else priceto
    rooms = int(parameters.get('rooms', 0))
    furniture = int(parameters.get('furniture', -1))

    # Exclude filtering by rooms if rooms parameter is set to 0.
    if rooms == 0 or rooms == 4:
        rooms_filter = {'rooms__gte': rooms}
    else:
        rooms_filter = {'rooms': rooms}

    # Exclude filtering by furniture if furniture parameter is None
    if furniture == 1:
        furniture_filter = {
            'furniture': True  # Filter for the specified furniture value
        }
    elif furniture == 0:
        furniture_filter = {
            'furniture': False
        }
    else:
        furniture_filter = {}

    ads = Ad.objects.filter(
        **city_filter,
        price__range=(pricefrom, priceto),
        **rooms_filter,
        **furniture_filter,
        is_actual=True  # Doesn't show archived ads on main page.
    )
    return ads


def sorting_ads(ads_set, sorting_method):
    """
    Order ads depending on sorting_method.
    Is used in the index() function.
    """
    if sorting_method == "price_desc":
        post_list = ads_set.order_by("-price")
        sorting = "Price - High to Low"
    elif sorting_method == "price_asc":
        post_list = ads_set.order_by("price")
        sorting = "Price - Low to High"
    else:   # If "newest" or any unrecognized sorting method.
        post_list = ads_set.order_by("-creation_date")
        sorting = "Creation - Newest"
    return post_list, sorting


def index(request, ad_id=0):
    """
    ad_id is used in case if particular ad is opened as first page. This
    parameter is used by JS fetch function to dynamically load ad.
    """
    is_filtered = request.GET.get("filter", False)  # Check if filter was applied.
    if is_filtered:
        ads = filter_ads(request.GET)
    else:
        ads = Ad.objects.filter(is_actual=True)

    sorting = request.GET.get("sorting", "newest")
    post_list, sorting = sorting_ads(ads, sorting)
    page_obj = pagination(request, post_list)

    # get_params is used with pagination. Preserve GET parameters when change page.
    get_params = ""
    for key, value in request.GET.items():
        if key != 'page':
            get_params += f"&{key}={value}"

    return render(request, "rental/index.html", {
        "page_obj": page_obj,
        "sorting": sorting,
        "get_params": get_params,
        "ad_id": ad_id
    })


@login_required
def create_ad(request):
    if request.method == 'POST':
        form = NewAd(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return HttpResponseRedirect(reverse('rental:main'))
        else:
            return render(request, 'rental/create.html', {'form': form})
    else:
        form = NewAd()
    return render(request, 'rental/create.html', {'form': form})


@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if request.user != ad.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = NewAd(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            # Update only if any data was changed.
            if form.changed_data:
                ad = form.save(commit=False)
                ad.update_date = datetime.now()
                form.save()
            return HttpResponseRedirect(reverse('rental:main'))
    else:
        form = NewAd(instance=ad)
    return render(request, 'rental/create.html', {
        'form': form,
        'edit': True,  # To change form action on create.html page.
        'ad_id': ad_id
    })


@login_required
def profile(request, section=None):
    """Load profile page."""
    new_message = NewMessage()  # Is used at dialog page.
    return render(request, "rental/profile.html", {
        "new_message": new_message,
        "section": section
    })


@login_required
def profile_load_ads(request):
    """Dynamically load user's ads to the profile page."""
    ads = Ad.objects.filter(user=request.user).order_by("-creation_date")
    if not ads:
        json_response = None
    else:
        json_response = []
        for ad in ads:
            json_ad = {"id": ad.id, "city": ad.city, "title": ad.title,
                       "price": ad.price, "description": ad.description,
                       "isactive": ad.is_actual, "creation_date": ad.creation_date.strftime("%Y-%m-%d %H:%M")}
            json_response.append(json_ad)
    return JsonResponse(json_response, safe=False)


@login_required
def profile_load_saved(request):
    """Dynamically load to the profile page ads saved by user."""
    saved_ads = request.user.saved.all()
    if not saved_ads:
        json_response = None
    else:
        json_response = []
        for ad in saved_ads:
            json_ad = {"id": ad.id, "city": ad.city, "title": ad.title,
                       "price": ad.price, "description": ad.description,
                       "isactive": ad.is_actual, "creation_date":
                           ad.creation_date.strftime("%Y-%m-%d %H:%M")}
            json_response.append(json_ad)
    return JsonResponse(json_response, safe=False)


@login_required
def load_dialogs(request):
    """Dynamically load to the profile page user's dialogs."""
    dialogs = (Dialog.objects.filter(initiator=request.user) |
               Dialog.objects.filter(recipient=request.user))

    # Create field last_message_date for further ordering by it
    # depending on last message sent.
    dialogs = dialogs.annotate(
        last_message_date=Max('dialog_messages__creation_date'))
    dialogs = dialogs.order_by('-last_message_date')

    if not dialogs:
        json_response = None
    else:
        json_response = []
        for dialog in dialogs:
            if dialog.recipient == request.user:
                user = dialog.initiator.username
                read = dialog.recipient_read  # Indicates if it is new not yet read message.
            else:
                user = dialog.recipient.username
                read = dialog.initiator_read
            lst_msg = dialog.dialog_messages.order_by("-creation_date")[0]
            lst_msg_date = lst_msg.creation_date.strftime("%Y-%m-%d %H:%M")
            json_message = {"id": dialog.id, "ad_title": dialog.ad.title,
                            "user": user, "ad_city": dialog.ad.city,
                            "ad_price": dialog.ad.price,
                            "last_message_text": lst_msg.text,
                            "last_message_date": lst_msg_date,
                            "is_read": read
                            }
            json_response.append(json_message)
    return JsonResponse(json_response, safe=False)


@login_required
def load_dialog(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)

    # Checks if requested user is one of the dialog's participant.
    if request.user != dialog.initiator and request.user != dialog.recipient:
        return HttpResponseForbidden()

    messages = dialog.dialog_messages.all().order_by("creation_date")
    # Mark all messages as "read" when load dialog:
    read_dialog(request, dialog, "read")
    json_messages = []
    for message in messages:
        json_messages.append({"author": message.author.username,
                              "text": message.text,
                              "datetime": message.creation_date.strftime("%Y-%m-%d %H:%M")})
    json_response = {"id": dialog.id, "ad_title": dialog.ad.title,
                     "ad_city": dialog.ad.city, "ad_price": dialog.ad.price,
                     "messages": json_messages}
    return JsonResponse(json_response, safe=False)


@login_required
def start_dialog(request, ad_id):
    """
    Dynamically create dialog/send message on the ad page with the
    author of the ad.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        ad = get_object_or_404(Ad, id=ad_id)
        try:  # If add is already exists just send new message.
            dialog = Dialog.objects.get(ad=ad, initiator=request.user,
                                        recipient=ad.user)  # ad.user same as author of the ad
        except Dialog.DoesNotExist:
            dialog = None
        if not dialog:
            if request.user == ad.user:
                message = "Cannot create dialog with yourself."
                return JsonResponse({'message': message})
            else:  # Create dialog if not exists.
                dialog = Dialog(ad=ad, initiator=request.user,
                                recipient=ad.user)
                dialog.save()

        # Create message object if message is not empty.
        if text and text.strip():
            new_message = Message(author=request.user, dialog=dialog,
                                  text=text)
            new_message.save()
            message = "Message has been successfully sent."
            read_dialog(request, dialog, "send")
        else:
            message = "Message text is empty."
    else:
        message = "Invalid request method."
    return JsonResponse({'message': message})


@login_required
def send_message(request, dialog_id):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        if text.strip():
            dialog = get_object_or_404(Dialog, id=dialog_id)
            new_message = Message(author=request.user, dialog=dialog,
                                  text=text)
            new_message.save()
            message = "Successfully sent"
            read_dialog(request, dialog, "send")
        else:
            message = "Message text is empty"
    else:
        message = "Invalid request method"
    return JsonResponse({'message': message})


def load_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    ad_object = {"city": ad.city, "title": ad.title, "price": ad.price,
                 "description": ad.description,
                 "furniture": ad.furniture, "rooms": ad.rooms,
                 "isavailable": ad.available_now,
                 "available_from": ad.available_from.strftime("%Y-%m-%d") if ad.available_from else None,
                 "creation_date": ad.creation_date, "isactive": ad.is_actual,
                 "author": ad.user.username, "phone": ad.user.mobile_phone,
                 "is_author": request.user == ad.user,
                 "image_url": ad.image.url if ad.image else None
                 }
    return JsonResponse(ad_object, safe=False)


@login_required
def is_saved(request, ad_id):
    """Check if ad is already in user's saved ads."""
    ad = get_object_or_404(Ad, id=ad_id)
    saved_ads = request.user.saved.all()
    if ad in saved_ads:
        message = "saved"
    else:
        message = "not_saved"
    return JsonResponse({"message": message})


@login_required
@require_http_methods(["PUT"])
def to_saved(request, ad_id):
    """Add or remove ad to/from user's ads depending on current state"""
    try:
        ad = Ad.objects.get(id=ad_id)
    except Ad.DoesNotExist:
        return JsonResponse({'message': f'Ad with id {ad_id} not exists'},
                            status=404)
    if request.user == ad.user:
        message = 'Cannot save your own ad.'
        status = 400
    else:
        # Check if the ad is already saved by the user
        if request.user.saved.filter(pk=ad_id).exists():
            # If the ad is already saved, remove it from saved
            request.user.saved.remove(ad)
            message = 'removed'
        else:
            # If the ad is not saved, add to saved
            request.user.saved.add(ad)
            message = 'saved'
        status = 200
    return JsonResponse({'message': message}, status=status)


@login_required
def update_profile(request):
    """Update spans (number of saved ads and unread dialogs)"""
    saved_ads_num = len(request.user.saved.all())
    unread_dialogs = Dialog.objects.filter(initiator=request.user,
                                           initiator_read=False).count()
    unread_dialogs += Dialog.objects.filter(recipient=request.user,
                                            recipient_read=False).count()
    return JsonResponse({'saved_ads_num': saved_ads_num, "unread_dialogs": unread_dialogs})


@login_required
@require_http_methods(["PUT"])
def change_active(request, ad_id):
    """Change is_actual attr of Ad object depending on current value."""
    try:
        ad = Ad.objects.get(id=ad_id)
    except Ad.DoesNotExist:
        return JsonResponse({'message': f'Ad with id {ad_id} not exists'},
                            status=404)
    # Check if author of ad sending request.
    if ad.user == request.user:
        if ad.is_actual:
            ad.is_actual = False
            message = 'deactivated'
        else:
            ad.is_actual = True
            message = 'activated'
        ad.save()
        status = 200
    else:
        message = 'Access denied'
        status = 403
    return JsonResponse({'message': message}, status=status)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("rental:index"))
        else:
            return render(request, "rental/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "rental/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("rental:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        # Ensure phone matches required US phone number format
        if not re.match(r"^\([0-9]{3}\) ?[0-9]{3}-[0-9]{4}\b$", phone):
            return render(request, "rental/register.html", {
                "message": "Not appropriate phone number format"
            })
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "rental/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password,
                                            mobile_phone=phone)
            user.save()
        except IntegrityError:
            return render(request, "rental/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("rental:index"))
    else:
        return render(request, "rental/register.html")
