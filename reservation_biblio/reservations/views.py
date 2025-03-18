from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import Student, Reservation, Room
from datetime import datetime, timedelta, date, time
import random
from django.shortcuts import render, get_object_or_404


def check_24h_interval(student, reservation_date):
    today = date.today()
    next_week_start = today + timedelta(days=(7 - today.weekday()))  # Lundi de la semaine prochaine

    # Vérifier si la réservation est pour la semaine prochaine
    if reservation_date >= next_week_start:
        last_reservation = Reservation.objects.filter(student=student).order_by('-date', '-start_time').first()
        if last_reservation:
            last_reservation_end = datetime.combine(last_reservation.date, last_reservation.end_time)
            now = datetime.now()
            return (now - last_reservation_end).total_seconds() >= 24 * 3600  # Vérifier la règle de 24h
    return True  # Si c'est pour la semaine en cours, pas de restriction


# Vérifier si l'étudiant a dépassé la limite de 2 réservations par semaine
def check_reservation_limit(student):
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche de cette semaine
    # Compter le nombre de réservations effectuées cette semaine
    reservations_this_week = Reservation.objects.filter(
        student=student,
        date__range=[start_of_week, end_of_week]
    )
    return reservations_this_week.count() < 2  # Retourner True si l'étudiant n'a pas dépassé la limite

# Générer les créneaux horaires disponibles
def generate_time_slots(start_time, end_time, interval_minutes):
    slots = []
    current_time = start_time
    # Générer des créneaux horaires toutes les 15 minutes
    while current_time < end_time:  # Ne pas inclure `end_time`
        slots.append(current_time.strftime('%H:%M'))
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=interval_minutes)).time()
    return slots

def home(request):
    return redirect('login')  # Rediriger vers la page de connexion

def login(request):
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        email = f"{student_number}@parisnanterre.fr"
        code = str(random.randint(1000, 9999))  # Générer un code aléatoire pour la connexion

        # Préparer l'email
        email_subject = "Votre code de connexion à la Bibliothèque Universitaire"
        email_message = f"""Bonjour,

Votre code de connexion est : {code}

Veuillez entrer ce code pour accéder au service de réservation.

Cordialement,
La Bibliothèque Universitaire
Université Paris Nanterre"""

        try:
            # Envoyer l'email avec le code de connexion
            send_mail(email_subject, email_message, 'bibliotheque@parisnanterre.fr', [email], fail_silently=False)
        except Exception as e:
            return HttpResponse(f"Erreur lors de l'envoi de l'e-mail : {str(e)}")

        request.session['student_number'] = student_number  # Enregistrer le numéro d'étudiant dans la session
        request.session['login_code'] = code  # Enregistrer le code dans la session
        return redirect('validate_login')  # Rediriger vers la page de validation du code

    return render(request, 'login.html')

def validate_login(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        # Vérifier si le code entré correspond à celui envoyé par email
        if code == request.session.get('login_code'):
            student_number = request.session.get('student_number')
            Student.objects.get_or_create(student_number=student_number, email=f"{student_number}@parisnanterre.fr")
            return redirect('reservation')  # Rediriger vers la page de réservation
        else:
            return render(request, 'validate_login.html', {'error': 'Code incorrect'})
    return render(request, 'validate_login.html')

def reservation(request):
    if not request.session.get('student_number'):
        return redirect('login')  # Si l'étudiant n'est pas connecté, le rediriger vers la page de connexion

    student_number = request.session.get('student_number')
    student = Student.objects.get(student_number=student_number)

    start_time = time(8, 0)
    end_time = time(20, 0)
    time_slots = generate_time_slots(start_time, end_time, 15)  # Générer les créneaux horaires disponibles
    today_date = date.today().strftime('%Y-%m-%d')  # Obtenir la date actuelle

    if request.method == 'POST':
        date_selected = request.POST.get('date')
        room_name = request.POST.get('room')
        # Si la date et la salle sont spécifiées, vérifier la disponibilité
        if date_selected and room_name:
            return redirect('check_availability', date_selected=date_selected, room_name=room_name)
        else:
            return render(request, 'reservation.html', {
                'error': 'Veuillez remplir tous les champs.',
                'rooms': Room.objects.all(),
                'today_date': today_date,
                'hours': time_slots,
                'student_number': student_number
            })
    return render(request, 'reservation.html', {
        'today_date': today_date,
        'rooms': Room.objects.all(),
        'hours': time_slots,
        'student_number': student_number
    })

def check_availability(request, date_selected=None, room_name=None):
    if not date_selected or not room_name:
        return HttpResponse("Date ou salle non spécifiée.")

    # Xử lý tên phòng cũ sang tên phòng mới (nếu cần)
    name_mapping = {
        "Salle A": "Box A",
        "Salle B": "Box B"
    }
    room_name = name_mapping.get(room_name, room_name)  

    # Récupérer la salle par son nom ou retourner une erreur si elle n'existe pas
    room = get_object_or_404(Room, name=room_name)

    # Récupérer les réservations existantes pour la salle et la date sélectionnées
    reservations = Reservation.objects.filter(date=date_selected, room=room)

    # Générer les créneaux horaires disponibles
    time_slots = generate_time_slots(time(8, 0), time(20, 0), 15)
    availability = {}

    for slot in time_slots:
        start_time = datetime.strptime(slot, '%H:%M').time()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=15)).time()

        # Vérifier si le créneau horaire est déjà réservé
        is_booked = reservations.filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        hour_key = slot.split(':')[0]  # Récupérer l'heure du créneau horaire (ex. '08' pour '08:00')
        if hour_key not in availability:
            availability[hour_key] = []  # Initialiser une liste pour chaque heure

        availability[hour_key].append({
            'hour': slot,
            'status': 'booked' if is_booked else 'available'  # Marquer comme réservé ou disponible
        })

    student_number = request.session.get('student_number', 'Inconnu')

    return render(request, 'availability.html', {
        'availability': availability,  # Dictionnaire des créneaux horaires par heure
        'date_selected': date_selected,
        'room_name': room_name,
        'student_number': student_number
    })


# Créer une nouvelle réservation
from django.core.mail import send_mail

def create_reservation(request, date_selected, room_name, hour):
    if not request.session.get('student_number'):
        return redirect('login')

    student_number = request.session.get('student_number')
    student = Student.objects.get(student_number=student_number)

    # Vérification de la validité de la date
    try:
        date_selected_obj = datetime.strptime(date_selected, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Date invalide, veuillez choisir une date valide.")

    # Vérifier les conditions de réservation
    if not check_reservation_limit(student):
        return render(request, 'error.html', {'message': "Vous avez déjà atteint la limite de 2 réservations pour cette semaine."})

    if not check_24h_interval(student, date_selected_obj):
        return render(request, 'error.html', {'message': "Si vous souhaitez réserver pour la semaine prochaine, vous devez attendre 24 heures après votre dernière réservation."})


    try:
        room = Room.objects.get(name=room_name)  # Récupérer l'objet Room
    except Room.DoesNotExist:
        return HttpResponse("Salle introuvable.")

    time_slots = generate_time_slots(time(8, 0), time(20, 0), 15)
    if hour not in time_slots:
        return HttpResponse("Heure invalide, veuillez choisir une heure valide.")

    start_time = datetime.strptime(hour, '%H:%M').time()

    if request.method == 'POST':
        end_time_str = request.POST.get('end_time')
        participants = request.POST.get('participants')

        if end_time_str:
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            if datetime.combine(date_selected_obj, end_time) <= datetime.combine(date_selected_obj, start_time):
                return render(request, 'error.html', {'message': "La durée minimale de réservation est de 15 minutes."})

            reservation = Reservation.objects.create(
                student=student,
                room=room,
                date=date_selected_obj,
                start_time=start_time,
                end_time=end_time,
                participants=participants,
            )

            # Envoyer un email de confirmation
            subject = "Confirmation de réservation"
            message = f"""
Bonjour {student_number},

Votre réservation a été confirmée.
Détails :
- Salle : {room.name}
- Date : {date_selected}
- Heure : {hour} à {end_time.strftime('%H:%M')}
- Nombre de participants : {participants}

Cordialement,
La Bibliothèque Universitaire
Université Paris Nanterre
"""
            send_mail(
                subject,
                message,
                'bibliotheque@parisnanterre.fr',
                [student.email],
                fail_silently=False
            )

            return redirect('manage_reservations')

    return render(request, 'create_reservation.html', {
        'student_number': student_number,
        'room_name': room_name,
        'date_selected': date_selected,
        'start_time': hour,
        'time_slots': time_slots
    })



def manage_reservations(request):
    student_number = request.session.get('student_number')
    student = Student.objects.get(student_number=student_number)
    reservations = Reservation.objects.filter(student=student).order_by('-date', '-start_time')

    now = datetime.now()
    for reservation in reservations:
        end_datetime = datetime.combine(reservation.date, reservation.end_time)
        reservation.room_name = reservation.room.name 
        reservation.status = 'en cours' if end_datetime > now else 'passé'  # Mettre à jour le statut de la réservation

    return render(request, 'manage_reservations.html', {'reservations': reservations,'student_number': student_number})

def cancel_reservation(request, reservation_id):
    student_number = request.session.get('student_number')
    student = Student.objects.get(student_number=student_number)
    
    try:
        reservation = Reservation.objects.get(id=reservation_id, student=student)
    except Reservation.DoesNotExist:
        return HttpResponse("Réservation introuvable ou non autorisée.")

    # Lưu thông tin để gửi email trước khi xóa
    room_name = reservation.room.name
    date_selected = reservation.date
    start_time = reservation.start_time.strftime('%H:%M')
    end_time = reservation.end_time.strftime('%H:%M')

    # Supprimer la réservation
    reservation.delete()

    # Gửi email thông báo hủy đặt phòng
    subject = "Annulation de réservation"
    message = f"""
Bonjour {student_number},

Votre réservation a été annulée.
Détails de la réservation annulée :
- Salle : {room_name}
- Date : {date_selected}
- Heure : {start_time} à {end_time}

Si vous n'avez pas effectué cette action, veuillez contacter la bibliothèque.

Cordialement,
La Bibliothèque Universitaire
Université Paris Nanterre
"""
    send_mail(
        subject,
        message,
        'bibliotheque@parisnanterre.fr',
        [student.email],
        fail_silently=False
    )

    return redirect('manage_reservations')


def logout(request):
    request.session.flush()  # Effacer la session de l'utilisateur
    return redirect('login')  # Rediriger vers la page de connexion
