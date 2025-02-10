from ollama import chat
import re
import os
from datetime import datetime

def check_grammar(sentences):
    # Create a prompt for grammar correction
    for sent in sentences:
        prompt = f"""You are a grammar checker for the LaTex draft of an academic paper. Correct the following sentence for obvious grammar mistakes. 
        You are not supposed to add quotation marks or modify other LaTex commands. Only return the corrected sentence without explanations or additional text.
        
        Sentence: "{sent}"
        Return your answer in a new line, beginning with "Corrected:" """
        
        response = chat(
            model='llama3.1',  # or any other model you prefer
            # model = 'deepseek-r1',
            messages=[{'role': 'user', 'content': prompt}],
        )
        
        # Extract the corrected text from response
        corrected_text = response['message']['content'].strip()
        yield corrected_text


def extract_sentences(latex_file):
    with open(latex_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split into sentences, remove the space at the begining of each senteces, start from the 4th sentence
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text)][2:]
    return sentences

def process_latex_file(latex_file):
    progress_dir = "progress"
    if not os.path.exists(progress_dir):
        os.makedirs(progress_dir)
    # Create timestamped progress file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    progress_file = os.path.join(progress_dir, f"correction_log_{timestamp}.txt")
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write("Grammar Correction Log\n")
        f.write("====================\n\n")
        f.write(f"Started at: {timestamp}\n\n")


    sentences = extract_sentences(latex_file)
    for original, corrected in zip(sentences, check_grammar(sentences)):
        # First remove the thinking process (everything between and including <think> tags)
        corrected = re.sub(r'<think>[\s\S]*?</think>\s*', '', corrected)
        # Then extract only what comes after "Corrected:"
        corrected = re.sub(r'^.*?Corrected:\s*', '', corrected)
        
        # only display if they are different
        if original != corrected:
            with open(progress_file, 'a', encoding='utf-8') as f:
                f.write("CHANGED:\n")
                f.write(f"Original :\n{original}\n")
                f.write(f"Corrected: \n{corrected}\n")
                # f.write(f"Explanation: \n{explanation}\n")
                f.write("\n")
latex_file = "main.tex"
process_latex_file(latex_file)
