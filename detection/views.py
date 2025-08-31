import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import ImageUploadForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

model = load_model(str(Path(__file__).resolve().parent.parent / 'crop_disease_model.h5'))
class_names = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot', 'Tomato__Tomato_YellowLeaf__Curl_Virus','Tomato__Tomato_mosaic_virus', 'Tomato_healthy']

disease_info = {
    'Pepper__bell___Bacterial_spot': {
        'solution': 'Remove and destroy infected plants. Use disease-free seeds and resistant varieties. Apply copper-based fungicides.',
        'medicine': 'Copper Oxychloride, Streptocycline'
    },
    'Pepper__bell___healthy': {
        'solution': 'No action needed.',
        'medicine': 'N/A'
    },
    'Potato___Early_blight': {
        'solution': 'Remove infected leaves. Practice crop rotation. Apply recommended fungicides.',
        'medicine': 'Mancozeb, Chlorothalonil'
    },
    'Potato___Late_blight': {
        'solution': 'Remove and destroy infected plants. Use preventive fungicidal sprays.',
        'medicine': 'Metalaxyl, Mancozeb'
    },
    'Potato___healthy': {
        'solution': 'No action needed.',
        'medicine': 'N/A'
    },
    'Tomato_Bacterial_spot': {
        'solution': 'Remove infected leaves. Use disease-free seeds. Employ crop rotation.',
        'medicine': 'Copper-based fungicide'
    },
    'Tomato_Early_blight': {
        'solution': 'Prune affected areas, rotate crops.',
        'medicine': 'Chlorothalonil spray'
    },
    'Tomato_Late_blight': {
        'solution': 'Remove infected leaves. Use copper-based fungicide.',
        'medicine': 'Copper Oxychloride, Mancozeb'
    },
    'Tomato_Leaf_Mold': {
        'solution': 'Increase air circulation. Remove infected leaves and avoid overhead watering.',
        'medicine': 'Chlorothalonil, Mancozeb'
    },
    'Tomato_Septoria_leaf_spot': {
        'solution': 'Remove affected leaves. Practice crop rotation and ensure proper spacing.',
        'medicine': 'Chlorothalonil, Mancozeb'
    },
    'Tomato_Spider_mites_Two_spotted_spider_mite': {
        'solution': 'Spray with water to remove mites. Use insecticidal soap or neem oil.',
        'medicine': 'Neem oil, Insecticidal soap'
    },
    'Tomato__Target_Spot': {
        'solution': 'Remove diseased leaves and avoid overhead watering. Apply fungicide if necessary.',
        'medicine': 'Mancozeb, Chlorothalonil'
    },
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {
        'solution': 'Remove infected plants and control whitefly vectors. Use resistant varieties.',
        'medicine': 'No direct treatment. Control vectors (Imidacloprid recommended for whiteflies)'
    },
    'Tomato__Tomato_mosaic_virus': {
        'solution': 'Remove and destroy infected plants. Sanitize tools and hands after handling.',
        'medicine': 'No direct treatment. Preventive sanitation and resistant varieties recommended.'
    },
    'Tomato_healthy': {
        'solution': 'No action needed.',
        'medicine': 'N/A'
    }
}

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload') 
        else:
            return redirect('login')
    return render(request, 'detection/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return redirect('register')

        if User.objects.filter(username=username).exists():
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        return redirect('login')
    return render(request, 'detection/register.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            image_path = image_instance.image.path 
            prediction = predict_disease(image_path)
            request.session['result'] = {
                'predicted_disease': prediction[0],
                'solution': prediction[1].get('solution'),
                'medicine': prediction[1].get('medicine'),
                'image_url': image_instance.image.url
            }
            return redirect('result')
    else:
        form = ImageUploadForm()
    return render(request, 'detection/upload.html', {'form': form})

@login_required(login_url='login')
def result_view(request):
    result = request.session.get('result')
    if not result:
        return redirect('upload')
    return render(request, 'detection/result.html', result)

def predict_disease(img_path):
    print("Predicting:", img_path)  
    img = image.load_img(img_path, target_size=(224,224))
    arr = image.img_to_array(img) / 255.0
    pred = model.predict(np.expand_dims(arr, 0))
    print("Prediction raw output:", pred) 
    d = class_names[np.argmax(pred)]
    print("Predicted index:", np.argmax(pred))
    print("Predicted class:", class_names[np.argmax(pred)])
    return d, disease_info.get(d, {})

@login_required(login_url='login')
def shop_view(request):
    return render(request, 'detection/shop.html')

@login_required(login_url='login')
def add_to_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        item = {
            'id': int(request.POST.get('product_id')),
            'name': request.POST.get('name'),
            'price': int(request.POST.get('price')),
            'quantity': int(request.POST.get('quantity', 1)),
        }
        for cart_item in cart:
            if cart_item['id'] == item['id']:
                cart_item['quantity'] += item['quantity']
                break
        else:
            cart.append(item)
        request.session['cart'] = cart
        return redirect('cart')
    return redirect('shop')

@login_required(login_url='login')
def cart_view(request):
    cart = request.session.get('cart', [])
    for item in cart:
        item['subtotal'] = item['price'] * item['quantity']
    total = sum(item['subtotal'] for item in cart)
    return render(request, 'detection/cart.html', {'cart_items': cart, 'total': total})

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', [])  
    cart = [item for item in cart if item['id'] != item_id]
    request.session['cart'] = cart
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    request.session['cart'] = []
    return redirect('shop')