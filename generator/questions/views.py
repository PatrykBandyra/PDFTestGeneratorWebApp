from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from .forms import SubjectCreationForm, TestForm
from .models import Subject


@login_required
def create_subject(request):
    if request.method == 'POST':
        subject_form = SubjectCreationForm(data=request.POST)
        if subject_form.is_valid():
            new_subject = subject_form.save(commit=False)
            new_subject.author = request.user
            new_subject.save()  # First subject needs to get the id before ownership can be added
            new_subject.ownership.add(request.user)
            new_subject.save()
            return redirect('account:dashboard')
    else:
        subject_form = SubjectCreationForm()
    return render(request, 'questions/subject_form.html', {'subject_form': subject_form, 'section': 'create_subject'})


@login_required
def edit_subject(request, subject_id, subject_slug):
    if request.method == 'POST':
        subject_form = SubjectCreationForm(data=request.POST)
        if subject_form.is_valid():
            subject = get_object_or_404(Subject, id=subject_id)
            subject.name = subject_form.cleaned_data['name']
            subject.description = subject_form.cleaned_data['description']
            subject.save()
            return redirect('account:dashboard')
    else:
        subject = get_object_or_404(Subject, id=subject_id)
        subject_form = SubjectCreationForm(instance=subject)
    return render(request, 'questions/subject_form.html', {'subject_form': subject_form, 'section': 'edit_subject'})


@login_required
def subject(request, subject_id, subject_slug):
    return render(request, 'questions/subject_questions.html', {'form': TestForm()})
