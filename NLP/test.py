import requests

requests.post('http://158.130.167.232/classify', json = {'url':'https://3dwarehouse.sketchup.com/warehouse/getpubliccontent?contentId=e15b7820-5a82-4b81-bb79-6abb9499c9c3', 'query':'book'} ).text
# requests.post('http://158.130.167.232/classify', json = {'url':'https://3dwarehouse.sketchup.com/warehouse/getpubliccontent?contentId=f04ea502-0db8-484f-bb2b-1906a01458b7', 'query':'book'} ).text
# requests.post('http://158.130.167.232/classify', json = {'url':'https://3dwarehouse.sketchup.com/warehouse/getpubliccontent?contentId=76a7c6d6-da2c-41ee-a0eb-a9718cfca4d4', 'query':'book'} ).text