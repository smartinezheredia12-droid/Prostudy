from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

LEAGUES = [
    ("papel",     "📄 Papel",      0),
    ("carton",    "📦 Cartón",     100),
    ("madera",    "🪵 Madera",     250),
    ("cobre",     "🟤 Cobre",      500),
    ("bronce",    "🥉 Bronce",     900),
    ("aluminio",  "⚙️ Aluminio",   1500),
    ("plata",     "🥈 Plata",      2400),
    ("oro",       "🥇 Oro",        3700),
    ("esmeralda", "💚 Esmeralda",  5500),
    ("cuarzo",    "🔮 Cuarzo",     8000),
    ("onix",      "🖤 Ónix",       11000),
    ("amatista",  "💜 Amatista",   15000),
    ("diamante",  "💎 Diamante",   20000),
    ("obsidiana", "🌑 Obsidiana",  27000),
]
LEAGUE_CHOICES = [(l[0], l[1]) for l in LEAGUES]

RANKS = [
    ("aprendiz",     "📖 Aprendiz",      0),
    ("estudioso",    "📚 Estudioso",     5),
    ("erudito",      "🧐 Erudito",       10),
    ("scholar",      "🎓 Scholar",       15),
    ("investigador", "🔬 Investigador",  20),
    ("prodigio",     "⚡ Prodigio",      25),
    ("academico",    "🏛️ Académico",     30),
    ("cientifico",   "⚗️ Científico",    38),
    ("filosofo",     "🦉 Filósofo",      46),
    ("sabio",        "🌟 Sabio",         55),
    ("maestro",      "🎯 Maestro",       65),
    ("visionario",   "🔭 Visionario",    76),
    ("genio",        "💡 Genio",         88),
    ("iluminado",    "✨ Iluminado",     100),
    ("leyenda",      "🏆 Leyenda",       115),
]
RANK_CHOICES = [(r[0], r[1]) for r in RANKS]


def xp_for_level(level):
    if level <= 0:
        return 0
    return int(50 * (level ** 1.8))


def get_league(xp):
    league = LEAGUES[0]
    for l in LEAGUES:
        if xp >= l[2]:
            league = l
    return league[0]


def get_rank_for_level(level):
    rank = RANKS[0]
    for r in RANKS:
        if level >= r[2]:
            rank = r
    return rank[0]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    league = models.CharField(max_length=20, choices=LEAGUE_CHOICES, default='papel')
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='aprendiz')
    last_login_date = models.DateField(null=True, blank=True)
    avatar_initial = models.CharField(max_length=2, default='')

    def save(self, *args, **kwargs):
        self.league = get_league(self.xp)
        self.rank = get_rank_for_level(self.level)
        if not self.avatar_initial and self.user:
            self.avatar_initial = self.user.username[:2].upper()
        super().save(*args, **kwargs)

    def add_xp(self, amount):
        self.xp = max(0, self.xp + amount)
        lvl = 0
        while xp_for_level(lvl + 1) <= self.xp:
            lvl += 1
        self.level = lvl
        self.save()

    def xp_to_next_level(self):
        return xp_for_level(self.level + 1) - self.xp

    def xp_progress_pct(self):
        current_floor = xp_for_level(self.level)
        next_ceil = xp_for_level(self.level + 1)
        if next_ceil == current_floor:
            return 100
        return int((self.xp - current_floor) / (next_ceil - current_floor) * 100)

    def league_display(self):
        for l in LEAGUES:
            if l[0] == self.league:
                return l[1]
        return self.league

    def rank_display(self):
        for r in RANKS:
            if r[0] == self.rank:
                return r[1]
        return self.rank

    def next_league_info(self):
        idx = next((i for i, l in enumerate(LEAGUES) if l[0] == self.league), 0)
        if idx + 1 < len(LEAGUES):
            nxt = LEAGUES[idx + 1]
            return {'name': nxt[1], 'xp_needed': nxt[2] - self.xp, 'total': nxt[2]}
        return None

    def __str__(self):
        return f"{self.user.username} — Lvl {self.level}"


class Folder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#F97316')
    created_at = models.DateTimeField(auto_now_add=True)

    def task_count(self):
        return self.tasks.count()

    def pending_count(self):
        return self.tasks.filter(completed=False).count()

    def __str__(self):
        return f"{self.user.username} / {self.name}"


class Task(models.Model):
    TASK_TYPE = [
        ('individual', '👤 Individual'),
        ('colaborativo', '👥 Colaborativo'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=15, choices=TASK_TYPE, default='individual')
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    penalty_applied_days = models.IntegerField(default=0)

    def days_remaining(self):
        if self.completed:
            return 0
        return (self.deadline - timezone.now().date()).days

    def urgency_class(self):
        if self.completed:
            return 'done'
        r = self.days_remaining()
        if r < 0:
            return 'overdue'
        if r <= 2:
            return 'urgent'
        if r <= 5:
            return 'warning'
        return 'ok'

    def xp_reward(self):
        return 20 if self.task_type == 'colaborativo' else 10

    def __str__(self):
        return f"[{self.task_type}] {self.title}"


class AdminMessage(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_messages')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"-> {self.recipient.username}: {self.message[:40]}"


class MotivationalQuote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=150)
    source = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'"{self.text[:50]}" - {self.author}'
