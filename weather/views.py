import requests
from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from .models import SearchHistory

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Обліковий запис {username} успішно створено! Тепер ви можете увійти.')
            return redirect('login')

    else:
        form = UserRegisterForm()

    return render(request, 'weather/register.html', {'form': form})

@login_required
def home(request):
    weather_data = None

    if request.method == 'POST':
        city = request.POST.get('city')
        api_key = 'f65c39b52d6465463aa280ddeee1c88a'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=uk'

        try:
            response = requests.get(url).json()

            if response.get('cod') == 200:
                weather_data = {
                    'city': response['name'],
                    'temperature': response['main']['temp'],
                    'humidity': response['main']['humidity'],
                    'description': response['weather'][0]['description'].capitalize(),
                }


                SearchHistory.objects.create(
                    user=request.user,
                    city=weather_data['city'],
                    temperature=weather_data['temperature'],
                    description=weather_data['description'],
                )
            else:
                messages.error(request, 'Місто не знайдено! Перевірте правильність назви.')

        except requests.exceptions.RequestException:
            messages.error(request, 'Помилка підключення до сервера погоди.')

    return render(request, 'weather/home.html', {'weather': weather_data})


@login_required
def history(request):
    user_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')
    return render(request, 'weather/history.html', {'history': user_history})