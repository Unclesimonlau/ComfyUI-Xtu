import os
import requests
import torchaudio
import time
import random
import string
import json
import re
import asyncio
import edge_tts
import numpy as np
import folder_paths
from .xstugo import *
from ..tools.i18n.i18n import I18nAuto
from ..utils import *
from urllib.parse import quote
from gradio_client import Client
from datetime import datetime


# ====================处理GPTSoVits文本转语音====
i18n = I18nAuto()
language_list = [i18n("中文"), i18n("英文"), i18n("日文"), i18n("中英混合"), i18n("日英混合"), i18n("多语种混合")]

class Xstu_tts:
    SUPPORTED_FORMATS = ('.wav', '.mp3', '.ogg', '.flac', '.aiff', '.aif')

    @classmethod
    def INPUT_TYPES(cls):
        # 获取用户输入
        return {
            "required": {
                "URL": ("STRING", {
                    "default":"https://"
                    }),
                "stream": ([False, True], {"default": False}),
                "character": ([*TTS_MODELS], {
                    "default": "苏明",
                    "widget": "text"
                    }),   
                "text": ("STRING",{
                    "default": "这里输入你想要生成语言的内容",
                    "multiline": True
                    }),
                "text_language":(language_list,{
                    "default": i18n("中文"),
                    "widget": "text"
                    }),
                "speed":("FLOAT",{
                    "default": 1,
                    "min": 1,
                    "max": 5,
                    "step": 0.05,
                    "display": "slider"
                    }),
                "top_k":("INT",{
                    "default":20,
                    "min":1,
                    "max": 100,
                    "step": 1,
                    "display": "slider"
                    }),
                "top_p":("FLOAT",{
                    "default":1,
                    "min":0,
                    "max": 1,
                    "step": 0.05,
                    "display": "slider"
                    }),
                "temperature":("FLOAT",{
                    "default":1,
                    "min":0,
                    "max": 1,
                    "step": 0.05,
                    "display": "slider"
                    }),
            }
        }

    CATEGORY = "🐅Xstu/API"
    RETURN_TYPES = ("AUDIO", )
    FUNCTION = "xstu_func"

    @staticmethod
    def generate_random_filename(extension):
        """生成一个随机文件名"""
        timestamp = time.strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        return f"{timestamp}_{random_suffix}{extension}"

    def xstu_func(self, URL, stream, character, text_language, speed, top_k, top_p, temperature, text):
        # 对文本进行 URL 编码
        encoded_text = quote(text)
        # 构建请求URL
        url = f"{URL}/tts?stream={stream}&character={character}&text_language={text_language}&speed={speed}&top_k={top_k}&top_p={top_p}&temperature={temperature}&text={text}"
        response = requests.get(url)

        if response.status_code == 200:
            # 创建输出目录如果不存在
            output_dir = '/workspace/ComfyUI/output/wav/'
            os.makedirs(output_dir, exist_ok=True)

            # 保存文件
            file_extension = '.wav'  # 假设返回的音频格式是wav
            random_filename = self.generate_random_filename(file_extension)
            file_path = os.path.join(output_dir, random_filename)

            with open(file_path, 'wb') as f:
                f.write(response.content)

            # 加载音频文件
            waveform, sample_rate = torchaudio.load(file_path)
            audio = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
            return (audio, )
        else:
            raise Exception(f"请求失败，状态码：{response.status_code}")

# ==============处理GPTSoVits文本转语音推文版====

class Xstu_tts_tuiwen:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "URL": ("STRING", {"default": "https://"}),
                "character": ([*TTS_MODELS], {
                    "default": "苏明",
                    "widget": "text"
                }),   
                "texts": ("STRING", {"multiline": True}),
                "text_language":(language_list,{
                    "default": i18n("中文"),
                    "widget": "text"
                }),
                "speed": ("FLOAT", {
                    "default": 1,
                    "min": 1,
                    "max": 5,
                    "step": 0.05,
                    "display": "slider"
                }),
                "top_k": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "display": "slider"
                }),
                "top_p": ("FLOAT", {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "step": 0.05,
                    "display": "slider"
                }),
                "temperature": ("FLOAT", {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "step": 0.05,
                    "display": "slider"
                }),
                "novel_name": ("STRING", {"default": "小说（故事）名"}),
                "audio_path": ("STRING", {"default": "output/wav/自定义音频文件夹"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("音频路径",)
    FUNCTION = "xstu_func_tuiwen"
    OUTPUT_NODE = True

    CATEGORY = "🐅Xstu/API"

    def xstu_func_tuiwen(self, URL, character, texts, text_language, speed, top_k, top_p, temperature, novel_name, audio_path):
        asyncio.run(self.generate_audio_files(texts, novel_name, character, audio_path, URL, text_language, speed, top_k, top_p, temperature))
        return (audio_path,)

    async def generate_audio_files(self, texts, novel_name, voice, audio_path, URL, text_language, speed, top_k, top_p, temperature):
        des = xtucf()
        sentences = re.split(r"\n", texts.strip())
        audio_folders = des.create_audio_folders(novel_name, len(sentences), audio_path)
        for i, sentence in enumerate(sentences):
            segments = sentence.split("，")
            for segment in segments:
                segment = segment.strip()
                if segment:
                    await des.text_to_audio(novel_name, voice, segment, audio_folders[i], URL, text_language, speed, top_k, top_p, temperature)

class xtucf:
    async def text_to_audio(self, novel_name, voice, text, audio_folder, URL, text_language, speed, top_k, top_p, temperature):
        file = f"{novel_name}_{len(os.listdir(audio_folder))}.mp3"
        audio_path = os.path.join(audio_folder, file)
        await self.sohoai_tts_text_to_audio(voice, text, audio_path, URL, text_language, speed, top_k, top_p, temperature)

    async def sohoai_tts_text_to_audio(self, voice, text, output_file, URL, text_language, speed, top_k, top_p, temperature):
        url = f"{URL}/tts?character={voice}&text_language={text_language}&speed={speed}&top_k={top_k}&top_p={top_p}&temperature={temperature}&text={requests.utils.quote(text)}"
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
        else:
            raise Exception(f"Failed to get audio: {response.status_code} - {response.text}")

    def create_audio_folders(self, novel_name, num_folders, audio_path):
        audio_folders = [os.path.join(audio_path, f"{novel_name}_{i}") for i in range(num_folders)]
        for folder in audio_folders:
            os.makedirs(folder, exist_ok=True)
        return audio_folders

# =========================微软文本转语音====

class mirco_2_audio:
    @classmethod
    def INPUT_TYPES(cls):
        VOICES=['zh-CN-XiaoxiaoNeural','zh-CN-XiaoyiNeural','zh-CN-YunjianNeural','zh-CN-YunxiNeural','zh-CN-YunxiaNeural','zh-CN-YunyangNeural','zh-CN-liaoning-XiaobeiNeural','zh-CN-shaanxi-XiaoniNeural','zh-HK-HiuGaaiNeural','zh-HK-HiuMaanNeural','zh-HK-WanLungNeural','zh-TW-HsiaoChenNeural','zh-TW-HsiaoYuNeural','zh-TW-YunJheNeural']
        return {
            "required": {
                "voice": (VOICES, ),
                "texts": ("STRING", {"multiline": True}),
                "novel_name": ("STRING", {"default": "小说（故事）名"}),
                "audio_path": ("STRING", {"default": "output/wav/自定义音频文件夹"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("音频路径",)
    
    FUNCTION = "mirco_to_audio"
    OUTPUT_NODE = True

    CATEGORY = "🐅Xstu/API"

    def mirco_to_audio(self,voice,texts,novel_name,audio_path):
        
        asyncio.run(generate_audio_files(texts, novel_name, voice, audio_path))
        return(audio_path,)


class xtucf_mirco:
    
    async def text_to_audio(self,novel_name, voice, text, audio_folder):
        file = f"{novel_name}_{len(os.listdir(audio_folder))}.mp3"
        audio_path = os.path.join(audio_folder, file)
        await edge_tts_text_to_audio(voice, text, audio_path)

async def edge_tts_text_to_audio(voice, text, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def create_audio_folders(novel_name, num_folders, audio_path):
    audio_folders = [os.path.join(audio_path, f"{novel_name}_{i}") for i in range(num_folders)]
    for folder in audio_folders:
        os.makedirs(folder, exist_ok=True)
    return audio_folders

async def generate_audio_files(texts, novel_name, voice, audio_path):
    des = xtucf_mirco()
    sentences = re.split(r"\n", texts.strip())
    audio_folders = create_audio_folders(novel_name, len(sentences), audio_path)
    for i, sentence in enumerate(sentences):
        segments = sentence.split("，")
        for segment in segments:
            segment = segment.strip()
            if segment:
                await des.text_to_audio(novel_name,voice, segment, audio_folders[i])

# ===============获取剪映草稿必备项======
class create_draf:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_name": ("STRING", {"default": "草稿"}),
                "text_line": ("STRING", {"multiline": True}),
                "voice_path": ("STRING", {"default": "output/audio"}),
                "image_path": ("STRING", {"default": "output/tuiwen/image"}),
                
            }

        }
    RETURN_TYPES = ("STRING","STRING","STRING","STRING",)
    RETURN_NAMES = ("项目名","单句字幕","单个音频","单个图片",)
    FUNCTION = "create_draft"
    OUTPUT_NODE = True
    CATEGORY = "🐅Xstu/剪映"

    def create_draft(self,novel_name,text_line,voice_path,image_path):
        self.novel_name=novel_name
        return (novel_name,text_line,voice_path,image_path)
    # def novel(self):
    #     novel_name=self.novel_name
    #     return novel_name
    

# ========================剪映草稿创建============
# ===============获取剪映json模板句柄===========
class sc_cao_gao:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "novel_name": ("STRING", {"default": "草稿"}),
                "text_line": ("STRING", {"default": "xx.txt"}),
                "voice_path": ("STRING", {"default": "output/audio"}),
                "image_path": ("STRING", {"default": "output/tuiwen/image/自定义路径"}),
                "cutcap_path": ("STRING", {"default": "output/cutcap/cutcappro"}),
                "len": ("INT", {"default": 1}),
                "zlen": ("INT", {"default": 100}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("项目名",)
    FUNCTION = "init_data"
    OUTPUT_NODE = True
    CATEGORY = "🐅Xstu/剪映"

    def init_data(self, novel_name, text_line, voice_path, image_path, cutcap_path, len, zlen):
        my_instance = init_path()
        
        my_instance.create_json(cutcap_path, novel_name)
        my_instance.text(text_line)
        my_instance.audio(len, voice_path, novel_name)
        my_instance.image_audio(image_path)
        my_instance.image(zlen)
        
        my_instance.write_data()
        return (novel_name,)

class init_path:
    def __init__(self):
        self.draft_content_template = {}
        self.draft_meta_template = {}
        self.template_duration = {"item_duration": [], "duration": []}

    def create_json(self, cutcap, novel_name):
        # 创建json文件
        self.base_path = cutcap  # 程序所在目录
        self.novel_name = novel_name  # 项目名
        self.folder_path = os.path.join(self.base_path, self.novel_name)
        self.template_meta_info_path, self.template_meta_content_path, self.template_duration_path = template_path()  # 返回两个模版的完整路径--基础模板
        self.draft_content_template = read_json(self.template_meta_content_path)  # 模版1
        self.draft_meta_template = read_json(self.template_meta_info_path)  # 模版2
        self.template_duration = read_json(self.template_duration_path)  # 模版3
        self.draft_content_template['id'] = generate_id()  # 给模版ID设置唯一id
        tracks_text_data = tracks()  # 创建tracks用于存放文字信息
        tracks_text_data['type'] = 'text'  # 类型
        self.draft_content_template['tracks'].append(tracks_text_data)
        tracks_video_data = tracks()  # 创建tracks用于存放图片信息
        tracks_video_data['type'] = 'video'  # 类型
        self.draft_content_template['tracks'].append(tracks_video_data)
        tracks_audio_data = tracks()  # 创建tracks用于存放音频信息
        tracks_audio_data['type'] = 'audio'  # 类型
        self.draft_content_template['tracks'].append(tracks_audio_data)  # 添加到模板里
        self.draft_meta_template['draft_id'] = generate_id()  # 给模版ID设置唯一id
        self.draft_meta_template['draft_root_path'] = self.base_path  # 剪映的草稿路径 如：D:\\\\software\\\\剪映\\\\JianyingPro Drafts
        self.draft_meta_template['tm_draft_create'] = int(time.time() * 1000)  # draft_meta_info.json创建时间，时间戳
        self.draft_meta_template['tm_draft_modified'] = generate_16_digit_timestamp()  # 13或16位毫秒级时间戳
        self.draft_meta_template['draft_removable_storage_device'] = get_drive_from_path(self.base_path)  # 磁盘的驱动器 如"D:"
        self.draft_meta_template['draft_fold_path'] = self.folder_path.replace('\\','/')  # 剪映安装路径加上项目名 如： D:/software/剪映/JianyingPro Drafts/六合八荒唯我独尊
        self.draft_meta_template['draft_name'] = self.novel_name  # 项目名

    def audio(self, indes, audio_path, novel_name):
        for i in range(indes):
            self.audio_path = os.path.join(audio_path, f"{novel_name}_{i}")
            self.audio_path_json = os.path.join(audio_path + 'duration.json')
            self.audiopath = self.audio_path.replace('\\', '/')
            audio_sold = process_audios_in_folder(self.audiopath)
            total_duration = 0
            for index, audio in enumerate(audio_sold):
                audio_items_data = audios()
                audio_items_data['path'] = audio['file_path'].replace('\\', '/')
                audio_items_data['name'] = audio['file_name']
                audio_items_data['duration'] = audio['duration']
                total_duration += audio['duration']
                items = items_duraion()
                items[index] = int(str(i) + str(index))
                items['dtn'] = audio['duration']
                items['start_value'] = total_duration - audio_items_data['duration']
                items['end_value'] = audio_items_data['duration']
                items["path"] = audio_items_data['path']
                items["name"] = audio_items_data['name']
                items["duration"] = audio_items_data['duration']
                self.template_duration['item_duration'].append(items)
            self.duration_item_data = durations_items()
            self.duration_item_data['index'] = i
            self.duration_item_data['value'] = total_duration
            self.template_duration['duration'].append(self.duration_item_data)
        with open(self.audio_path_json, 'w', encoding='utf-8') as json_file:
            json.dump(self.template_duration, json_file, indent=4, ensure_ascii=False)

    def image_audio(self, image_path):
        self.imagepath = image_path.replace('\\', '/')
        image_sold = process_images_in_folder(self.imagepath)
        total_image_duration = 0
        for index, image in enumerate(image_sold):
            videos_items_data = videos_items()
            videos_items_data['path'] = image['file_path'].replace('\\', '/')
            videos_items_data['material_name'] = image['file_name']
            videos_items_data['width'] = image['width']
            videos_items_data['height'] = image['height']
            videos_items_data['id'] = generate_id()
            self.draft_content_template['materials']['videos'].append(videos_items_data)
            canvases_items_data = canvases_items()
            canvases_items_data['id'] = generate_id()
            self.draft_content_template['materials']['canvases'].append(canvases_items_data)
            sound_items_data = sound_items()
            sound_items_data['id'] = generate_id()
            self.draft_content_template['materials']['sound_channel_mappings'].append(sound_items_data)
            speeds_items_data = speeds_items()
            speeds_items_data['id'] = generate_id()
            self.draft_content_template['materials']['speeds'].append(speeds_items_data)
            material_animations_items_data = material_animations_items()
            material_animations_items_data['id'] = generate_id()
            self.draft_content_template['materials']['material_animations'].append(material_animations_items_data)
            choice_items_data = vocal()
            choice_items_data['id'] = generate_id()
            self.draft_content_template['materials']['vocal_separations'].append(choice_items_data)
            segments_video_data = segment_video()
            segments_video_data['material_id'] = videos_items_data['id']
            segments_video_data['extra_material_refs'] = [speeds_items_data['id'], canvases_items_data['id'], material_animations_items_data['id'], sound_items_data['id'], choice_items_data['id']]
            segments_video_data['id'] = generate_id()
            duration_image_item = self.template_duration['duration'][index]['value']
            total_image_duration += duration_image_item
            self.draft_content_template['tracks'][1]['segments'].append(segments_video_data)
            self.draft_content_template['tracks'][1]['segments'][index]['source_timerange']['duration'] = duration_image_item
            self.draft_content_template['tracks'][1]['segments'][index]['target_timerange']['duration'] = duration_image_item + 1
            self.draft_content_template['tracks'][1]['segments'][index]['source_timerange']['start'] = 0
            self.draft_content_template['tracks'][1]['segments'][index]['target_timerange']['start'] = total_image_duration - duration_image_item
        self.draft_content_template['duration'] = total_image_duration

    def text(self,text_line):
        
        
        # ==============处理文本=========
        
        # 按照逗号、句号和问号分割文本行
        sentences = re.split(r"[。，！？]", text_line)
        
        for lines in sentences:
            line = lines.strip()
            # ===================material_animations======================
            material_animations_items_data=material_animations_items()
            material_animations_items_data['id']=generate_id()
            self.draft_content_template['materials']['material_animations'].append(material_animations_items_data)  # 添加到模板里
            # ====================tracks-segments-text=
            segment_text_data = text_segment_items()
            
            segment_text_data['extra_material_refs'] = [material_animations_items_data['id']]
            self.draft_content_template['tracks'][0]['segments'].append(segment_text_data)  # 添加到模板里
            text_length = len(line)
            start_index = 0
            end_index = text_length
            text_data = text_items()
            
            text_data['id'] = segment_text_data['material_id']
            text_data_content = json.loads(text_data['content'])
            
            text_data_content['text'] = line
            text_data_content['styles'][0]['range']= [start_index, end_index]
            text_data['content']= json.dumps(text_data_content, ensure_ascii=False)
            
            self.draft_content_template['materials']['texts'].append(text_data)  # 添加到模板里
            
            
            
    def image(self,ledx):
        total_duration=0
        for index in range(ledx):
            duration_audio_item=self.template_duration['item_duration']
            audio_items_data=audios()
            audio_items_data['path'] = duration_audio_item[index]["path"]
            audio_items_data['name'] = duration_audio_item[index]["name"]
            audio_items_data['duration'] = duration_audio_item[index]["duration"]
            total_duration += audio_items_data['duration']
            audio_items_data['id']=generate_id()
            self.draft_content_template['materials']['audios'].append(audio_items_data)  # 添加到模板里
            # ====================speeds==============================
            speeds_items_data=speeds_items()
            speeds_items_data['id']=generate_id()
            self.draft_content_template['materials']['speeds'].append(speeds_items_data)  # 添加到模板里
            # ==============================beats=============
            beats_items_data=beats_items()
            beats_items_data['id']=generate_id()
            self.draft_content_template['materials']['beats'].append(beats_items_data)  # 添加到模板里
            #=========================audio_channel_mappings=============

            sound_items_data=sound_items()
            sound_items_data['id']=generate_id()
            self.draft_content_template['materials']['sound_channel_mappings'].append(sound_items_data)  # 添加到模板里
            # =================vocal_separations================
            choice_items_data=vocal()
            choice_items_data['id']=generate_id()
            self.draft_content_template['materials']['vocal_separations'].append(choice_items_data)  # 添加到模板里
        # =============tracks-segments-audio=======
            segments_audio_data = segment_audio()
            segments_audio_data['material_id'] = audio_items_data['id']
            self.draft_content_template['tracks'][2]['segments'].append(segments_audio_data)  # 添加到模板里
            segments_audio_data['extra_material_refs'] = [speeds_items_data['id'], beats_items_data['id'],sound_items_data['id'],choice_items_data['id']]
        #=============duration===============================
            segments_audio_data['target_timerange']['duration'] = duration_audio_item[index]['duration']
            segments_audio_data['source_timerange']['start'] = 0
            segments_audio_data['target_timerange']['start'] = total_duration-duration_audio_item[index]['duration']
            segments_audio_data['source_timerange']['duration'] = duration_audio_item[index]['duration']
            
            self.draft_content_template['tracks'][0]['segments'][index]['target_timerange']['start']=total_duration-duration_audio_item[index]['duration']
            self.draft_content_template['tracks'][0]['segments'][index]['target_timerange']['duration']=duration_audio_item[index]['duration']
            

    
      
    def write_data(self):
        """
        创建文件,并写入数据
        """
        self.meta_info_path = self.folder_path+ '/draft_meta_info.json'
        self.content_path = self.folder_path + '/draft_content.json'
        # 创建文件夹
        os.makedirs(self.folder_path, exist_ok=True)
        # 创建 draft_meta_info.json
        with open(self.meta_info_path, 'w', encoding='utf-8') as meta_info_file:
            json.dump(self.draft_meta_template, meta_info_file, indent=4, ensure_ascii=False)

        with open(self.content_path, 'w', encoding='utf-8') as content_file:
            json.dump(self.draft_content_template, content_file, indent=4, ensure_ascii=False)
