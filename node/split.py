from typing import Any, Dict, List, Tuple
import re
class srow:
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(self)-> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "Text":("STRING",{"multiline":True}),
        }
    }
        
           

    RETURN_TYPES = ("STRING","INT")
    RERURN_NAMES = ("Strings","Number")
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (True,)

    FUNCTION = "to_string_list"

    CATEGORY = "🐅Xstu/推文"
    def to_string_list(self, Text: str) -> Tuple[List[str], int]:
        cleaned_text = "\n".join(line for line in Text.split("\n") if line.strip())
        string_list = cleaned_text.split("\n")
        length = len(string_list)
        return string_list, length
    
class fenkuai:
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(self)-> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "Text":("STRING",{"multiline":True}),
        }
    }
        
           

    RETURN_TYPES = ("STRING",)
    RERURN_NAMES = ("Strings",)
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (True,)

    FUNCTION = "to_string_dan"

    CATEGORY = "🐅Xstu/推文"
    def to_string_dan(self, Text: str,):
        sentences = re.split(r"[。，！？]", Text)
        result = []
        
        for lines in sentences:
            line=lines.strip()
            if line:
                result.append(line)
            
        return (result,)
class srowtostring:
    
    def __init__(self):
        
        pass
    
    @classmethod
    def INPUT_TYPES(self)-> Dict[str, Dict[str, Any]]:
       
        
        return {
            "required": {
                "Text":("STRING",{"multiline":True}),
                "select_prompt": ("INT", {"default": 1, "min": 1, "max": 9999}),

        }
    }
           
    RETURN_TYPES = ("STRING","INT")
    RERURN_NAMES = ("String","Position")
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,False)
    
    FUNCTION = "get_string_with_position"

    CATEGORY = "🐅Xstu/推文"
   
    def get_string_with_position(self, Text: str,select_prompt: int) -> Tuple[str, int]:
        cleaned_text = "\n".join(line for line in Text.split("\n") if line.strip())
        string_list = cleaned_text.split("\n")
        
        # 获取列表长度
        length = len(string_list)
        
        
        # start_index = max(0, min(start_index, length - 1))

        
        # end_index = length
        
        # select_prompt = string_list[start_index:end_index]
        if 1<=select_prompt<=length:
            select_string = string_list[select_prompt-1]
        return (select_string, select_prompt,)

class autotext:
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(self)-> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "Text":("STRING",{"multiline":True}),
        }
    }
        
           

    RETURN_TYPES = ("INT",)
    RERURN_NAMES = ("NUMBER",)
    INPUT_IS_LIST = True
   

    FUNCTION = "to_string_dans"

    CATEGORY = "🐅Xstu/推文"
    def to_string_dans(self, Text: str,):
        length = len(Text)
            
        return (length,)