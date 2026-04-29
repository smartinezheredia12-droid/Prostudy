from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random
import datetime
from .models import (UserProfile, Folder, Task, AdminMessage,
                     MotivationalQuote, LEAGUES, xp_for_level)


# ─── AUTH ─────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # streak update
            profile = user.profile
            today = timezone.now().date()
            if profile.last_login_date:
                delta = (today - profile.last_login_date).days
                if delta == 1:
                    profile.streak += 1
                elif delta > 1:
                    profile.streak = 1
            else:
                profile.streak = 1
            profile.last_login_date = today
            profile.save()
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not username or not password1:
            messages.error(request, 'Completa todos los campos.')
        elif password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
        elif len(password1) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        else:
            user = User.objects.create_user(username=username, password=password1)
            # El perfil lo crea la señal post_save automáticamente
            login(request, user)
            messages.success(request, f'¡Bienvenido, {username}! Tu aventura comienza.')
            return redirect('dashboard')
    return render(request, 'core/register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    profile = request.user.profile
    # tarea penalización diaria
    _apply_daily_penalties(request.user)

    pending_tasks = Task.objects.filter(user=request.user, completed=False).order_by('deadline')[:5]
    collab_pending = Task.objects.filter(user=request.user, completed=False, task_type='colaborativo')

    # frase motivacional aleatoria
    quotes = list(MotivationalQuote.objects.all())
    quote = random.choice(quotes) if quotes else None

    # mensaje admin más reciente
    admin_msg = AdminMessage.objects.filter(recipient=request.user).first()

    # xp progreso
    xp_pct = profile.xp_progress_pct()
    xp_next = profile.xp_to_next_level()

    context = {
        'profile': profile,
        'pending_tasks': pending_tasks,
        'collab_pending': collab_pending,
        'quote': quote,
        'admin_msg': admin_msg,
        'xp_pct': xp_pct,
        'xp_next': xp_next,
    }
    return render(request, 'core/dashboard.html', context)


def _apply_daily_penalties(user):
    """Aplica -5 XP por cada día vencido en tareas individuales (solo una vez por día)."""
    overdue = Task.objects.filter(
        user=user, completed=False, task_type='individual',
        deadline__lt=timezone.now().date()
    )
    profile = user.profile
    for task in overdue:
        days_over = (timezone.now().date() - task.deadline).days
        new_days = days_over - task.penalty_applied_days
        if new_days > 0:
            profile.add_xp(-5 * new_days)
            task.penalty_applied_days += new_days
            task.save()


# ─── CARPETAS ─────────────────────────────────────────────────────────────────
@login_required
def folders_view(request):
    folders = Folder.objects.filter(user=request.user).order_by('name')
    return render(request, 'core/folders.html', {'folders': folders})


@login_required
def folder_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#F97316')
        if name:
            Folder.objects.create(user=request.user, name=name, color=color)
            messages.success(request, f'Carpeta "{name}" creada.')
        return redirect('folders')
    return redirect('folders')


@login_required
def folder_delete(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    folder.delete()
    messages.success(request, 'Carpeta eliminada.')
    return redirect('folders')


@login_required
def folder_detail(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    tasks = folder.tasks.filter(user=request.user).order_by('completed', 'deadline')
    return render(request, 'core/folder_detail.html', {'folder': folder, 'tasks': tasks})


# ─── TAREAS ───────────────────────────────────────────────────────────────────
@login_required
def tasks_view(request):
    tasks = Task.objects.filter(user=request.user).order_by('completed', 'deadline')
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'core/tasks.html', {'tasks': tasks, 'folders': folders})


@login_required
def task_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        task_type = request.POST.get('task_type', 'individual')
        deadline = request.POST.get('deadline')
        folder_id = request.POST.get('folder')
        if title and deadline:
            try:
                deadline_date = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Fecha inválida. Usa el formato YYYY-MM-DD.')
                return redirect('tasks')
            folder = None
            if folder_id:
                try:
                    folder = Folder.objects.get(pk=folder_id, user=request.user)
                except Folder.DoesNotExist:
                    pass
            Task.objects.create(
                user=request.user, title=title, description=description,
                task_type=task_type, deadline=deadline_date, folder=folder
            )
            messages.success(request, f'Tarea "{title}" registrada.')
        return redirect('tasks')
    return redirect('tasks')


@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if not task.completed:
        task.completed = True
        task.completed_at = timezone.now()
        task.save()
        request.user.profile.add_xp(task.xp_reward())
        messages.success(request, f'¡+{task.xp_reward()} XP! Tarea completada.')
    return redirect(request.META.get('HTTP_REFERER', 'tasks'))


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return redirect(request.META.get('HTTP_REFERER', 'tasks'))


# ─── LIGAS ────────────────────────────────────────────────────────────────────
@login_required
def leagues_view(request):
    profile = request.user.profile
    all_profiles = UserProfile.objects.select_related('user').order_by('-xp')

    # usuarios en la misma liga
    same_league = all_profiles.filter(league=profile.league).exclude(user=request.user)

    next_league = profile.next_league_info()

    context = {
        'profile': profile,
        'all_profiles': all_profiles,
        'same_league': same_league,
        'next_league': next_league,
        'leagues': LEAGUES,
    }
    return render(request, 'core/leagues.html', context)


# ─── ADMIN PANEL ─────────────────────────────────────────────────────────────
@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    users = User.objects.filter(is_superuser=False).select_related('profile').order_by('username')
    return render(request, 'core/admin_panel.html', {
        'users': users,
        'admin_profile': request.user.profile,
    })


@login_required
def admin_send_message(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message = request.POST.get('message', '').strip()
        if user_id and message:
            recipient = get_object_or_404(User, pk=user_id)
            AdminMessage.objects.create(recipient=recipient, message=message)
            messages.success(request, f'Mensaje enviado a {recipient.username}.')
    return redirect('admin_panel')


@login_required
def admin_adjust_xp(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount', 0)
        try:
            amount = int(amount)
            user = get_object_or_404(User, pk=user_id)
            user.profile.add_xp(amount)
            messages.success(request, f'XP ajustado para {user.username}: {amount:+d} XP.')
        except (ValueError, TypeError):
            messages.error(request, 'Cantidad inválida.')
    return redirect('admin_panel')


@login_required
def admin_change_password(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password', '')
        if user_id and new_password:
            user = get_object_or_404(User, pk=user_id)
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Contraseña de {user.username} actualizada.')
    return redirect('admin_panel')
