from requests import get, post, delete

print(post('http://localhost:5000/api/orders').json())

print(post('http://localhost:5000/api/orders',
           json={'name': 'Сережки'}).json())

print(post('http://localhost:5000/api/orders',
           json={'name': 'Сережки',
                 'phone_number': '891112314124'}).json())