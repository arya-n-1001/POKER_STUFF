import google.generativeai as genai
genai.configure(api_key="AIzaSyDt7EOG5HEfm1-PeYLu93KaEWG0P-xwb-w")

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)