from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, MotivationalQuote


class Command(BaseCommand):
    help = 'Crea datos iniciales: admin y frases motivacionales'

    def handle(self, *args, **kwargs):
        # Admin
        if not User.objects.filter(username='ADMIN').exists():
            admin = User.objects.create_superuser('ADMIN', '', 'AdMiN2026')
            UserProfile.objects.get_or_create(user=admin, defaults={'avatar_initial': 'AD'})
            self.stdout.write(self.style.SUCCESS('✓ Admin creado: ADMIN / AdMiN2026'))
        else:
            admin = User.objects.get(username='ADMIN')
            if not hasattr(admin, 'profile'):
                UserProfile.objects.create(user=admin, avatar_initial='AD')
            self.stdout.write('ℹ Admin ya existe')

        # Frases
        quotes = [
            ("El éxito es la suma de pequeños esfuerzos repetidos día tras día.", "Robert Collier", "Autor"),
            ("Nunca es tarde para ser lo que podrías haber sido.", "George Eliot", "Literatura"),
            ("Todo lo que puedas imaginar es real.", "Pablo Picasso", "Arte"),
            ("La disciplina es el puente entre metas y logros.", "Jim Rohn", "Empresario"),
            ("No cuentes los días, haz que los días cuenten.", "Muhammad Ali", "Boxeo"),
            ("El único lugar donde el éxito viene antes que el trabajo es en el diccionario.", "Vidal Sassoon", "Empresario"),
            ("La vida es lo que te pasa mientras estás ocupado haciendo otros planes.", "John Lennon", "Música"),
            ("Todo parece imposible hasta que se hace.", "Nelson Mandela", "Política"),
            ("Si puedes soñarlo, puedes hacerlo.", "Walt Disney", "Cine"),
            ("El que no arriesga no gana.", "Refrán Popular", "Sabiduría"),
            ("Porque todo lo puedo en Cristo que me fortalece.", "Filipenses 4:13", "Biblia"),
            ("No temas, porque yo estoy contigo.", "Isaías 41:10", "Biblia"),
            ("El que trabaja su tierra se saciará de pan.", "Proverbios 12:11", "Biblia"),
            ("Cuando crees en ti mismo, los demás no tienen otra opción que creer en ti.", "Sheryl Crow", "Música"),
            ("La motivación te pone en marcha. El hábito te mantiene en movimiento.", "Jim Ryun", "Atletismo"),
            ("It's not about how hard you hit. It's about how hard you can get hit and keep moving forward.", "Rocky Balboa", "Rocky (1976)"),
            ("Do or do not. There is no try.", "Yoda", "Star Wars"),
            ("The secret of getting ahead is getting started.", "Mark Twain", "Literatura"),
            ("Every moment gives us a chance to become more than what we are.", "Ratatouille", "Ratatouille (2007)"),
            ("What we do in life echoes in eternity.", "Maximus", "Gladiator (2000)"),
            ("Believe in yourself and you will be unstoppable.", "Emily Guay", "Emprendimiento"),
            ("A ship in harbor is safe, but that is not what ships are for.", "John A. Shedd", "Escritor"),
            ("Press X to not die.", "Dark Souls", "Videojuego"),
            ("War. War never changes.", "Fallout", "Videojuego"),
            ("The mind is everything. What you think, you become.", "Buda", "Filosofía"),
            ("Dondequiera que vayas, ve con todo tu corazón.", "Confucio", "Filosofía"),
            ("Caer siete veces, levantarse ocho.", "Proverbio Japonés", "Sabiduría"),
            ("No esperes el momento perfecto. Toma el momento y hazlo perfecto.", "Zoey Sayward", "Motivación"),
            ("Una pequeña llama ilumina toda la oscuridad.", "Dante Alighieri", "Literatura"),
            ("Primero estudia, después opina.", "Epicteto", "Filosofía"),
        ]

        created = 0
        for text, author, source in quotes:
            obj, c = MotivationalQuote.objects.get_or_create(author=author, defaults={'text': text, 'source': source})
            if c:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {created} frases motivacionales añadidas'))
