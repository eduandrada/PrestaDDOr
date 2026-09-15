import re

def clean_repetitive_speech_text(text: str) -> str:
    if not text:
        return ""
    
    # 1. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Remove consecutive duplicate words
    text = re.sub(r'\b(\w+)(?:\s+\1)+\b', r'\1', text, flags=re.IGNORECASE)
    
    # 3. Strip greetings/fillers repeated in dictation
    text = re.sub(r'(?i)\bhola\b|\bcómo estás\b|\bcomo estas\b|\bnecesito\b|\bquisiera\b|\bpor favor\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. Filter out partial prefix words if full word appears shortly after
    words = text.split()
    filtered_words = []
    n = len(words)
    for i in range(n):
        w = words[i].lower()
        if len(w) <= 4:
            is_prefix = False
            for j in range(i + 1, min(i + 6, n)):
                next_w = words[j].lower()
                if len(next_w) > len(w) and next_w.startswith(w):
                    is_prefix = True
                    break
            if is_prefix:
                continue
        filtered_words.append(words[i])
        
    # 5. Remove phrase duplicates
    unique_words = []
    for w in filtered_words:
        if not unique_words or w.lower() != unique_words[-1].lower():
            unique_words.append(w)
            
    result = " ".join(unique_words)
    result = re.sub(r'\s+', ' ', result).strip()
    if result:
        result = result[0].upper() + result[1:]
    return result

test_text = """Hola Hola Hola cómo Hola cómo estás Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar Hola Cómo estás Necesito comprar lec Hola Cómo estás Necesito comprar lechu Hola Cómo estás Necesito comprar lechuga Hola Cómo estás Necesito comprar lechuga toma Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate Hola Cómo estás Necesito comprar lechuga tomate  2  2 kg  2 kg de  2 kg de toma  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate  2 kg de tomate"""

cleaned = clean_repetitive_speech_text(test_text)
print("ORIGINAL:")
print(test_text)
print("\nLIMPIO:")
print(cleaned)
