import re, random

def pick_a_sentence():
    sentences_arr = []
    temp_arr = []
    with open("sentences.txt", encoding="utf-8") as f:
        for line in f:
            arr = re.findall(r"[0-9]+、", line)
            if arr:
                sentences_arr.append('\n'.join(temp_arr))
                temp_arr = []
                line = line.split('、')[1]
                temp_arr.append(line)
            else:
                temp_arr.append(line+'\n')

    return sentences_arr[random.randint(1, sentences_arr.__len__()-1)]
        

