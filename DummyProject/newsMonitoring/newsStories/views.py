from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, SourceForm, StoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
import feedparser
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from bs4 import beautifulsoup
from django.contrib.auth.models import User


def index(request):
    return render(request, "newsStories/index.html")


def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        user = request.POST.get('username')
        company = request.POST.get('company')
        client = request.POST.get('client')
        # import ipdb;ipdb.set_trace()

        if form.is_valid():
            form.save()
            try:
                company = Company.objects.get(name=company)
            except Company.DoesNotExist:
                company = Company.objects.create(name=company)

            try:
                client = Company.objects.get(name=client)
            except Company.DoesNotExist:
                client = Company.objects.create(name=client)

            user = User.objects.get(username=user)
            subscribed = Subscriber.objects.create(user=user, company=company, client=client)
            subscribed.save()
            messages.success(request, 'Account successfully created')
            return redirect('login')

    context = {'form': form}
    return render(request, "newsStories/register.html", context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            subscriber = Subscriber.objects.get(user=user.id)
            if Source.objects.filter(created_by=subscriber).exists():
                return redirect('/storylist')
            else:
                return redirect('/source')
        else:
            messages.info(request, 'Username or password is incorrect')

    context = {}
    return render(request, 'newsStories/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def source(request):
    # import ipdb;ipdb.set_trace()
    form = SourceForm()
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            user_here = request.user.id
            name = request.POST.get('name')
            url = request.POST.get('url')

            sub = Subscriber.objects.get(user=user_here)
            client = sub.client

            source_save = Source.objects.create(name=name, url=url, created_by=sub, client=client)
            source_save.save()

        messages.success(request, 'Source successfully created')
        return redirect('/sources')
    else:
        context = {'form': form}
        return render(request, "newsStories/source.html", context)


def sourceList(request):
    user_here = request.user
    if user_here.is_staff:
        sources = Source.objects.all()
        count = Source.objects.all().count()
        if count == 0:
            return redirect('/source')
        # import ipdb;
        # ipdb.set_trace()

    else:
        user_here = request.user.id
        sub = Subscriber.objects.get(user=user_here)

        sources = Source.objects.filter(created_by=sub)
        count = Source.objects.filter(created_by=sub).count()

    context = {'sources': sources, 'count': count}
    return render(request, "newsStories/sourcesList.html", context)


def update_source(request, pk):
    form = SourceForm()
    if request.method == 'POST':
        form = SourceForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data['name']
            new_url = form.cleaned_data['url']
            old_data = Source.objects.get(id=pk)
            old_data.name = new_name
            old_data.url = new_url
            old_data.save()
            messages.success(request, 'Source successfully updated')
            return redirect('/sources')

    else:
        source_obj = Source.objects.get(id=pk)
        context = {'source_obj': source_obj}
        return render(request, "newsStories/update_source.html", context)


def source_delete(request, pk):
    old_data = Source.objects.get(id=pk)
    old_data.delete()
    return redirect('/sources')


def source_search(request):
    user_here = request.user.id
    sub = Subscriber.objects.get(user=user_here)
    # import ipdb;ipdb.set_trace()
    search = request.GET.get('search')
    if request.user.is_staff:
        sources = Source.objects.filter((Q(name__icontains=search) | Q(url__icontains=search)))

    else:
        sources = Source.objects.filter((Q(name__icontains=search) | Q(url__icontains=search)) & Q(created_by=sub))
    context = {'sources': sources, }
    return render(request, "newsStories/sourcesList.html", context)


def add_story(request):
    form = StoryForm()
    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            user_here = request.user.id
            title = form.cleaned_data['title']
            url = form.cleaned_data['url']
            pub_date = form.cleaned_data['pub_date']
            body_text = form.cleaned_data['body_text']
            source = form.cleaned_data['source']
            company = form.cleaned_data['company']
            count = company.count()
            sub = Subscriber.objects.get(user=user_here)
            client = sub.client

            story_save = Story.objects.create(title=title, url=url, pub_date=pub_date, client=client,
                                              body_text=body_text, source=source)
            story_save.save()
            for i in range(count):
                company_id = company[i].id
                story_save.companies.add(company_id)

        messages.success(request, 'Source successfully updated')
        return redirect('/storylist')
    else:
        context = {'form': form}
        return render(request, "newsStories/addStory.html", context)


def story_listing(request):

    if request.user.is_staff:
        stories_list = Story.objects.all()
    else:
        user_here = request.user.id
        sb = Subscriber.objects.get(user=user_here)
        curr_client = sb.client
        stories_list = Story.objects.filter(client=curr_client)

    page = request.GET.get('page', 1)

    paginator = Paginator(stories_list, 5)
    try:
        stories = paginator.page(page)
    except PageNotAnInteger:
        stories = paginator.page(1)
    except EmptyPage:
        stories = paginator.page(paginator.num_pages)

    context = {
        'stories': stories,
    }
    return render(request, 'newsStories/storyListing.html', context)


def update_story(request, pk):
    form = StoryForm()

    if request.method == 'POST':
        form = StoryForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data['title']
            new_url = form.cleaned_data['url']
            new_pub_date = form.cleaned_data['pub_date']
            new_body_text = form.cleaned_data['body_text']
            new_source = form.cleaned_data['source']
            new_company = form.cleaned_data['company']
            old_data = Story.objects.get(id=pk)
            old_data.title = new_title
            old_data.url = new_url
            old_data.pub_date = new_pub_date
            old_data.body_text = new_body_text
            old_data.source = new_source
            old_data.companies = new_company
            old_data.save()

        messages.success(request, 'Story successfully updated')
        return redirect('/storylist')

    else:

        story_obj = Story.objects.get(id=pk)
        print(story_obj)
        context = {'story_obj': story_obj}
        return render(request, "newsStories/update_story.html", context)


def story_search(request):
    user_here = request.user.id
    sub = Subscriber.objects.get(user=user_here)
    client_here = sub.client
    # import ipdb;ipdb.set_trace()
    search = request.GET.get('search')
    if request.user.is_staff:
        stories = Story.objects.filter((Q(title__icontains=search) | Q(url__icontains=search)))

    else:
        stories = Story.objects.filter((Q(title__icontains=search) | Q(url__icontains=search)) & Q(client=client_here))
    context = {'stories': stories, }
    return render(request, "newsStories/storyListing.html", context)


def story_delete(request, pk):
    old_data = Story.objects.get(id=pk)
    old_data.delete()
    return redirect('/storylist')


def story_fetch(request, pk):
    client_source = Source.objects.get(id=pk)
    source_url = client_source.url
    feed = feedparser.parse(source_url)
    list = feed.entries

    for e in list:
        entry_title = e.title
        entry_link = e.link
        entry_desc = e.description
        entry_pub = e.published
        curr_source = Source.objects.get(url=source_url)
        curr_client = curr_source.client
        curr_company = curr_client.id
        if Story.objects.filter(title=entry_title).exists():
            pass
        else:
            try:
                story_data = Story.objects.create(title=entry_title, url=entry_link, body_text=entry_desc,
                                                  pub_date=entry_pub, source=curr_source, client=curr_client)
                story_data.save()
                story_data.companies.add(curr_company)
            except IntegrityError as e:
                continue

    return redirect('/storylist')