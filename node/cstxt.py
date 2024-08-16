import os
script_dir = os.path.dirname(os.path.abspath(__file__))
absolute_path_1 = ('txtlist')

file_path = os.path.join(script_dir,absolute_path_1)
txt_files = []
for file in os.listdir(file_path):
    if file.endswith(".txt"):
        txt_files.append(file)

class txt_input:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required":{
            "List":(txt_files,)
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("TXT",)
    FUNCTION = "positive"
    CATEGORY = "🐅Xstu/推文"

    def positive(self,List):
        new_path = os.path.join(file_path, List)
        with open(new_path, 'r', encoding='utf-8') as f:
            result = f.read().strip("\n")
        return (result,)

class txt_len:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required":{
            "txt":("STRING",{"multiline":True}),
            }
        }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("txt_length",)
    FUNCTION = "txt_length"
    CATEGORY = "🐅Xstu/推文"
    def txt_length(self, txt):
        cleaned_text = "\n".join(line for line in txt.split("\n") if line.strip())
        string_list = cleaned_text.split("\n")
        non_empty_lines = [line for line in string_list if line.strip()]  # 过滤掉空行
        line_count = len(non_empty_lines)
        return (line_count+1,)