import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import conf
    
def get_prompt():
    prompt = conf.PROMPT
    return {'prompt_text': prompt}
    