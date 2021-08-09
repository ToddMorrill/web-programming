import random
from django import forms
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import markdown2

from . import util


class QueryForm(forms.Form):
    q = forms.CharField(label='Query')


def get_html_entry(title):
    content = util.get_entry(title)
    if content is not None:
        return markdown2.markdown(content)
    return None


def index(request):
    entries = util.list_entries()
    # check if form data was submitted
    form = QueryForm(request.GET)
    if form.is_valid():
        # if entry, redirect to the wiki entry
        query = form.cleaned_data['q']
        if query in entries:
            return HttpResponseRedirect(
                reverse('entry', kwargs={'title': query}))

        # else display list of possible results
        else:
            possible_results = []
            for entry in entries:
                if query in entry:
                    possible_results.append(entry)

            return render(request, 'encyclopedia/results.html',
                          {'entries': possible_results})

    # else, just render the homepage
    return render(request, "encyclopedia/index.html", {"entries": entries})


def entry(request, title):
    content = get_html_entry(title)
    if content is not None:
        return render(request, "encyclopedia/entry.html", {
            'entry': content,
            'title': title
        })
    return render(request, 'encyclopedia/notfound.html', {'title': title})


class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={
            'placeholder': 'Title',
            'style': 'width: 300px;',
            'class': 'form-control'
        }))
    content = forms.CharField(
        label='Markdown Content',
        widget=forms.Textarea(attrs={
            'placeholder': 'Markdown Content',
            'rows': 4,
            'class': 'form-control'
        }))


def new_entry(request):
    # if POST method, process form data
    if request.method == 'POST':
        # attempt to create new entry
        form = NewEntryForm(request.POST)
        if form.is_valid():
            # check if page already exists
            title = form.cleaned_data['title']
            entries = util.list_entries()
            if title in entries:
                return render(request, 'encyclopedia/exists.html',
                              {'title': title})
            content = form.cleaned_data['content']
            # otherwise, save new content
            util.save_entry(title, content)
            return HttpResponseRedirect(
                reverse('entry', kwargs={'title': title}))

    # render a blank form for GET method
    form = NewEntryForm()
    return render(request, 'encyclopedia/newentry.html', {'form': form})


def edit_entry(request, title):
    # if POST method, process form data
    if request.method == 'POST':
        # update entry
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            # save new content
            util.save_entry(title, content)
            return HttpResponseRedirect(
                reverse('entry', kwargs={'title': title}))

    # render existing data for GET method
    content = util.get_entry(title)
    form = NewEntryForm({'title': title, 'content': content})
    return render(request, 'encyclopedia/editentry.html', {
        'form': form,
        'title': title
    })


def random_entry(request):
    entries = util.list_entries()
    choice = random.choice(entries)
    return HttpResponseRedirect(reverse('entry', kwargs={'title': choice}))
