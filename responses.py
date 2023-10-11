import random

def handle_response(message: str) -> str:
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there!'
    
    if p_message == 'roll':
        return str(random.randint(1, 6))
    
    if p_message == 'that is Bihar':
        return 'Ching Chong Ching Ping Pong Ping Chinese Chinese'
        
    if p_message == '!help':
        return '`This is a help message that you can modify.`'
    
    return 'I didn\'t understand what you wrote. Try typing "!help".'