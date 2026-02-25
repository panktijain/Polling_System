from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PollCreationForm, RegistrationForm, UserProfileForm
from .models import Option, Poll, Vote


def home(request):
    """
    Render the unique, attractive homepage for the polling system.
    """
    return render(request, 'polls/home.html')


def poll_list(request):
    # List polls, optionally filter by category
    category = request.GET.get('category')
    polls_qs = Poll.objects.filter(is_active=True)
    if category and category != 'all':
        polls_qs = polls_qs.filter(category=category)
    polls = polls_qs.prefetch_related('options').select_related('created_by')
    # Predefined categories for filter UI
    categories = [
        ('all', 'All'),
        ('technology', 'Technology'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('college_life', 'College Life'),
        ('sports', 'Sports'),
    ]
    return render(request, 'polls/poll_list.html', {
        'polls': polls,
        'categories': categories,
        'selected_category': category or 'all',
    })


def poll_detail(request, id):
    poll = get_object_or_404(Poll, pk=id)
    if not poll.is_active:
        return HttpResponseForbidden("This poll is not active.")

    already_voted = False
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, poll=poll).select_related('option').first()
        already_voted = user_vote is not None

    return render(request, 'polls/poll_detail.html', {
        'poll': poll,
        'already_voted': already_voted,
        'user_vote': user_vote,
    })


@login_required
def vote(request, id):
    if request.method != 'POST':
        return redirect('poll_detail', id=id)

    poll = get_object_or_404(Poll, pk=id, is_active=True)

    option_id = request.POST.get('option')
    if not option_id:
        return render(request, 'polls/poll_detail.html', {
            'poll': poll,
            'already_voted': False,
            'user_vote': None,
            'error': 'Please select an option before submitting.',
        })

    option = get_object_or_404(Option, pk=option_id, poll=poll)

    try:
        with transaction.atomic():
            Vote.objects.create(user=request.user, poll=poll, option=option)
            Option.objects.filter(pk=option.pk).update(vote_count=F('vote_count') + 1)
    except IntegrityError:
        # Race condition: user voted simultaneously from two tabs
        user_vote = Vote.objects.filter(user=request.user, poll=poll).select_related('option').first()
        return render(request, 'polls/poll_detail.html', {
            'poll': poll,
            'already_voted': True,
            'user_vote': user_vote,
        })

    return redirect('poll_results', id=id)


def poll_results(request, id):
    poll = get_object_or_404(Poll, pk=id)
    total_votes = poll.total_votes()
    options_data = [
        {
            'option': option,
            'percentage': option.percentage(total_votes),
        }
        for option in poll.options.all()
    ]
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, poll=poll).select_related('option').first()
    return render(request, 'polls/poll_results.html', {
        'poll': poll,
        'options_data': options_data,
        'total_votes': total_votes,
        'user_vote': user_vote,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('poll_list')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('poll_list')
    else:
        form = RegistrationForm()
    return render(request, 'polls/register.html', {'form': form})


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollCreationForm(request.POST)
        option_texts = [t.strip() for t in request.POST.getlist('option_text') if t.strip()]
        if form.is_valid():
            if len(option_texts) < 2:
                form.add_error(None, 'Please provide at least 2 options.')
            else:
                with transaction.atomic():
                    poll = form.save(commit=False)
                    poll.created_by = request.user
                    poll.save()
                    for text in option_texts:
                        Option.objects.create(poll=poll, text=text)
                messages.success(request, 'Poll created successfully!')
                return redirect('poll_detail', id=poll.id)
    else:
        form = PollCreationForm()
        option_texts = ['', '']
    return render(request, 'polls/create_poll.html', {'form': form, 'option_texts': option_texts})


@login_required
def my_polls(request):
    # Retrieve all polls created by the current user
    polls = Poll.objects.filter(created_by=request.user).prefetch_related('options').order_by('-created_at')
    # Calculate total votes across all user's polls
    total_votes = sum(poll.total_votes() for poll in polls)
    return render(request, 'polls/my_polls.html', {'polls': polls, 'total_votes': total_votes})


@login_required
def deactivate_poll(request, id):
    if request.method != 'POST':
        return redirect('poll_detail', id=id)
    poll = get_object_or_404(Poll, pk=id)
    if poll.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to modify this poll.")
    poll.is_active = not poll.is_active
    poll.save()
    status = 'activated' if poll.is_active else 'deactivated'
    messages.success(request, f'Poll "{poll.question}" has been {status}.')
    return redirect('my_polls')


@login_required
def delete_poll(request, id):
    poll = get_object_or_404(Poll, pk=id)
    if poll.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to delete this poll.")
    if request.method == 'POST':
        title = poll.question
        poll.delete()
        messages.success(request, f'Poll "{title}" has been deleted.')
        return redirect('my_polls')
    return render(request, 'polls/confirm_delete.html', {'poll': poll})


@login_required
def vote_history(request):
    user_votes = (
        Vote.objects.filter(user=request.user)
        .select_related('poll', 'option')
        .order_by('-voted_at')
    )
    return render(request, 'polls/vote_history.html', {'user_votes': user_votes})


@login_required
def user_profile(request):
    """Display user profile information"""
    total_polls = Poll.objects.filter(created_by=request.user).count()
    user_votes = Vote.objects.filter(user=request.user).count()
    context = {
        'total_polls': total_polls,
        'user_votes': user_votes,
    }
    return render(request, 'polls/profile.html', context)


@login_required
def edit_profile(request):
    """Allow user to edit their profile information"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'polls/edit_profile.html', context)
